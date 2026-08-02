"""Deterministic specialist agents and governed orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .core import ActionProposal, AuditLog, EvidenceItem, SpecialistAgent
from .policy import PolicyDecision, PolicyEngine


def _evidence_ids(items: tuple[EvidenceItem, ...]) -> tuple[str, ...]:
    return tuple(item.evidence_id for item in items)


@dataclass(frozen=True)
class DataQualityAgent:
    name: str = "data_quality_agent"

    def propose(
        self,
        evidence: dict[str, Any],
        evidence_items: tuple[EvidenceItem, ...],
    ) -> ActionProposal:
        critical = bool(evidence.get("critical_failure", False))
        failed = tuple(evidence.get("failed_rules", ()))
        action = "quarantine_model_run" if critical else "continue_monitoring"
        rationale = (
            f"Critical quality rules failed: {', '.join(failed)}."
            if critical
            else "No critical data-quality rule failed."
        )
        return ActionProposal(action, rationale, _evidence_ids(evidence_items), self.name)


@dataclass(frozen=True)
class MonitoringAgent:
    name: str = "monitoring_agent"
    review_psi: float = 0.10
    investigate_psi: float = 0.25
    minimum_auc: float = 0.60

    def propose(
        self,
        evidence: dict[str, Any],
        evidence_items: tuple[EvidenceItem, ...],
    ) -> ActionProposal:
        psi = float(evidence.get("pd_psi", 0.0))
        auc = float(evidence.get("roc_auc", 1.0))
        if psi >= self.investigate_psi or auc < self.minimum_auc:
            action = "open_model_investigation"
            rationale = f"Material monitoring signal: PSI={psi:.3f}, matured AUC={auc:.3f}."
        elif psi >= self.review_psi:
            action = "increase_monitoring_frequency"
            rationale = f"Early drift signal: PSI={psi:.3f}."
        else:
            action = "continue_monitoring"
            rationale = f"No approved threshold breached: PSI={psi:.3f}, AUC={auc:.3f}."
        return ActionProposal(action, rationale, _evidence_ids(evidence_items), self.name)


@dataclass(frozen=True)
class ValidationAgent:
    name: str = "validation_agent"

    def propose(
        self,
        evidence: dict[str, Any],
        evidence_items: tuple[EvidenceItem, ...],
    ) -> ActionProposal:
        unresolved = int(evidence.get("unresolved_findings", 0))
        severity = str(evidence.get("maximum_severity", "none")).lower()
        if unresolved and severity in {"high", "critical"}:
            action = "request_human_validation"
            rationale = f"There are {unresolved} unresolved {severity}-severity findings."
        else:
            action = "continue_monitoring"
            rationale = "No unresolved high- or critical-severity validation finding was supplied."
        return ActionProposal(action, rationale, _evidence_ids(evidence_items), self.name)


@dataclass(frozen=True)
class OrchestrationResult:
    proposal: ActionProposal
    policy_decision: PolicyDecision
    audit_event_sha256: str


class GovernedAgentOrchestrator:
    """Route evidence to specialists, evaluate policy, and record—not execute."""

    def __init__(
        self,
        specialists: tuple[SpecialistAgent, ...] | None = None,
        *,
        policy_engine: PolicyEngine | None = None,
        audit_log: AuditLog | None = None,
    ) -> None:
        self.specialists = specialists or (
            DataQualityAgent(),
            MonitoringAgent(),
            ValidationAgent(),
        )
        self.policy_engine = policy_engine or PolicyEngine()
        self.audit_log = audit_log or AuditLog()

    def run(
        self,
        specialist_name: str,
        evidence: dict[str, Any],
        *,
        evidence_source: str,
    ) -> OrchestrationResult:
        specialist = next(
            (candidate for candidate in self.specialists if candidate.name == specialist_name),
            None,
        )
        if specialist is None:
            raise ValueError(f"Unknown or unapproved specialist: {specialist_name}")
        item = EvidenceItem.from_payload(evidence_source, evidence)
        self.audit_log.append("evidence_registered", specialist_name, asdict(item))
        proposal = specialist.propose(evidence, (item,))
        self.audit_log.append("action_proposed", specialist_name, asdict(proposal))
        decision = self.policy_engine.evaluate(proposal)
        event = self.audit_log.append("policy_evaluated", "policy_engine", asdict(decision))
        if not self.audit_log.verify():
            raise AssertionError("Agent audit hash chain failed verification")
        return OrchestrationResult(proposal, decision, event.event_sha256)

"""Deterministic permission and human-approval policy engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from .core import ActionProposal, PolicyDecision


@dataclass(frozen=True)
class AgentPolicy:
    allowed_actions: frozenset[str] = frozenset(
        {
            "continue_monitoring",
            "increase_monitoring_frequency",
            "open_data_quality_issue",
            "open_model_investigation",
            "request_human_validation",
            "draft_documentation_update",
            "quarantine_model_run",
        }
    )
    prohibited_actions: frozenset[str] = frozenset(
        {
            "approve_customer_credit",
            "decline_customer_credit",
            "change_customer_price",
            "change_customer_limit",
            "deploy_model",
            "retrain_model",
            "alter_source_evidence",
            "post_accounting_entry",
        }
    )
    actions_requiring_human_approval: frozenset[str] = frozenset(
        {
            "increase_monitoring_frequency",
            "open_data_quality_issue",
            "open_model_investigation",
            "request_human_validation",
            "draft_documentation_update",
            "quarantine_model_run",
        }
    )


class PolicyEngine:
    def __init__(self, policy: AgentPolicy | None = None) -> None:
        self.policy = policy or AgentPolicy()

    def evaluate(self, proposal: ActionProposal) -> PolicyDecision:
        if proposal.action in self.policy.prohibited_actions:
            decision, reason, approval = (
                "DENY",
                "The requested action is outside agent authority and is explicitly prohibited.",
                False,
            )
        elif proposal.action not in self.policy.allowed_actions:
            decision, reason, approval = (
                "DENY",
                "The action is not present in the approved capability allow-list.",
                False,
            )
        elif not proposal.evidence_ids:
            decision, reason, approval = (
                "DENY",
                "No immutable evidence identifiers support the proposal.",
                False,
            )
        elif proposal.action in self.policy.actions_requiring_human_approval:
            decision, reason, approval = (
                "PENDING_HUMAN_APPROVAL",
                "The proposal is permitted for recommendation but requires an authorised human decision.",
                True,
            )
        else:
            decision, reason, approval = (
                "ALLOW_RECOMMENDATION_ONLY",
                "The action may be recorded as a recommendation; it grants no customer-decision authority.",
                False,
            )
        return PolicyDecision(
            decision=decision,
            reason=reason,
            human_approval_required=approval,
            proposal_sha256=proposal.proposal_sha256,
            evaluated_at_utc=datetime.now(UTC).isoformat(),
        )

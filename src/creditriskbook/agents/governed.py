"""A bounded agent that triages model evidence but cannot decide customer credit."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from creditriskbook.data.quality import QualityReport


@dataclass(frozen=True)
class AgentRecommendation:
    status: str
    reasons: tuple[str, ...]
    recommended_action: str
    human_approval_required: bool
    authorised_scope: str
    prohibited_actions: tuple[str, ...]
    evidence_sha256: str
    created_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GovernedMonitoringAgent:
    """Apply pre-approved thresholds and produce an auditable recommendation."""

    prohibited_actions = (
        "approve_customer_credit",
        "decline_customer_credit",
        "change_customer_price_or_limit",
        "retrain_or_deploy_without_approval",
        "alter_source_evidence",
    )

    def review(self, quality: QualityReport, monitoring: dict[str, float]) -> AgentRecommendation:
        evidence = {"quality": quality.to_dict(), "monitoring": monitoring}
        digest = hashlib.sha256(
            json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        reasons: list[str] = []
        if quality.critical_failure:
            status = "HALT"
            reasons.append(f"Critical data-quality failures: {', '.join(quality.failed_rules)}")
            action = "Quarantine the run and assign the issues to data and model owners."
        elif monitoring.get("pd_psi", 0.0) >= 0.25:
            status = "ESCALATE"
            reasons.append(f"Prediction PSI is {monitoring['pd_psi']:.3f}, at or above 0.25.")
            action = "Open a material-drift investigation; do not redeploy automatically."
        elif monitoring.get("roc_auc", 1.0) < 0.60:
            status = "ESCALATE"
            reasons.append(f"Matured-outcome AUC is {monitoring['roc_auc']:.3f}, below 0.60.")
            action = "Investigate performance, segmentation, data changes, and calibration."
        elif monitoring.get("pd_psi", 0.0) >= 0.10:
            status = "REVIEW"
            reasons.append(f"Prediction PSI is {monitoring['pd_psi']:.3f}, at or above 0.10.")
            action = "Increase monitoring frequency and request owner review."
        else:
            status = "CONTINUE_MONITORING"
            reasons.append("No pre-approved escalation threshold was breached.")
            action = "Continue the approved monitoring schedule."
        return AgentRecommendation(
            status=status,
            reasons=tuple(reasons),
            recommended_action=action,
            human_approval_required=True,
            authorised_scope="model-monitoring triage only",
            prohibited_actions=self.prohibited_actions,
            evidence_sha256=digest,
            created_at_utc=datetime.now(UTC).isoformat(),
        )


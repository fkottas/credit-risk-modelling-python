"""Structured-output contract for deterministic or language-model implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

ALLOWED_RECOMMENDATIONS = frozenset(
    {"request_missing_evidence", "refer_for_human_review", "no_automated_action"}
)
PROHIBITED_DECISION_WORDS = frozenset({"approve", "approved", "decline", "declined"})


class StructuredTextModel(Protocol):
    """Provider-neutral interface introduced only after the output schema is tested."""

    def generate_structured(self, *, instructions: str, input_text: str) -> dict[str, Any]:
        """Return a JSON-like object; the caller validates it before use."""


@dataclass(frozen=True)
class UnderwritingEvidenceMemo:
    application_id: str
    verified_facts: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    inconsistencies: tuple[str, ...]
    safety_flags: tuple[str, ...]
    policy_citations: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    recommendation: str
    uncertainty: str


def validate_memo(
    memo: UnderwritingEvidenceMemo,
    *,
    available_evidence_ids: set[str],
    available_policy_ids: set[str],
) -> None:
    """Fail closed on unsupported citations, forbidden decisions, or missing identity."""
    if not memo.application_id:
        raise ValueError("The memo requires an application_id")
    if memo.recommendation not in ALLOWED_RECOMMENDATIONS:
        raise ValueError(f"Recommendation is outside the bounded schema: {memo.recommendation}")
    words = set(memo.recommendation.lower().replace("_", " ").split())
    if words & PROHIBITED_DECISION_WORDS:
        raise ValueError("The memo attempts a customer credit decision")
    unsupported_evidence = set(memo.evidence_ids) - available_evidence_ids
    if unsupported_evidence:
        raise ValueError(f"Unsupported evidence citations: {sorted(unsupported_evidence)}")
    unsupported_policy = set(memo.policy_citations) - available_policy_ids
    if unsupported_policy:
        raise ValueError(f"Unsupported policy citations: {sorted(unsupported_policy)}")
    if not memo.evidence_ids:
        raise ValueError("The memo cannot be issued without immutable evidence")

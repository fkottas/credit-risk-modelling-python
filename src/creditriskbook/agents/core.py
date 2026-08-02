"""Provider-neutral governed-agent primitives for credit-risk workflows."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol


def _canonical_digest(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    source: str
    payload_sha256: str
    created_at_utc: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(
        cls,
        source: str,
        payload: Any,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> EvidenceItem:
        digest = _canonical_digest(payload)
        return cls(
            evidence_id=f"ev-{digest[:16]}",
            source=source,
            payload_sha256=digest,
            created_at_utc=datetime.now(UTC).isoformat(),
            metadata=metadata or {},
        )


@dataclass(frozen=True)
class ActionProposal:
    action: str
    rationale: str
    evidence_ids: tuple[str, ...]
    requested_by: str
    parameters: dict[str, Any] = field(default_factory=dict)

    @property
    def proposal_sha256(self) -> str:
        return _canonical_digest(asdict(self))


@dataclass(frozen=True)
class PolicyDecision:
    decision: str
    reason: str
    human_approval_required: bool
    proposal_sha256: str
    evaluated_at_utc: str


@dataclass(frozen=True)
class AuditEvent:
    sequence: int
    event_type: str
    actor: str
    payload_sha256: str
    previous_event_sha256: str
    event_sha256: str
    created_at_utc: str


class AuditLog:
    """Append-only hash chain for deterministic teaching audits."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    @property
    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)

    def append(self, event_type: str, actor: str, payload: Any) -> AuditEvent:
        sequence = len(self._events) + 1
        previous = self._events[-1].event_sha256 if self._events else "GENESIS"
        payload_sha = _canonical_digest(payload)
        created = datetime.now(UTC).isoformat()
        event_sha = _canonical_digest(
            {
                "sequence": sequence,
                "event_type": event_type,
                "actor": actor,
                "payload_sha256": payload_sha,
                "previous_event_sha256": previous,
                "created_at_utc": created,
            }
        )
        event = AuditEvent(
            sequence=sequence,
            event_type=event_type,
            actor=actor,
            payload_sha256=payload_sha,
            previous_event_sha256=previous,
            event_sha256=event_sha,
            created_at_utc=created,
        )
        self._events.append(event)
        return event

    def verify(self) -> bool:
        previous = "GENESIS"
        for expected_sequence, event in enumerate(self._events, start=1):
            if event.sequence != expected_sequence or event.previous_event_sha256 != previous:
                return False
            recalculated = _canonical_digest(
                {
                    "sequence": event.sequence,
                    "event_type": event.event_type,
                    "actor": event.actor,
                    "payload_sha256": event.payload_sha256,
                    "previous_event_sha256": event.previous_event_sha256,
                    "created_at_utc": event.created_at_utc,
                }
            )
            if recalculated != event.event_sha256:
                return False
            previous = event.event_sha256
        return True


class SpecialistAgent(Protocol):
    name: str

    def propose(
        self, evidence: dict[str, Any], evidence_items: tuple[EvidenceItem, ...]
    ) -> ActionProposal:
        """Return a proposal; specialist agents never execute customer actions."""

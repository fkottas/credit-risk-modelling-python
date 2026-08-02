from __future__ import annotations

import unittest

from creditriskbook.agents import (
    ActionProposal,
    AuditLog,
    GovernedAgentOrchestrator,
    PolicyEngine,
)


class AgenticSystemTests(unittest.TestCase):
    def test_critical_quality_proposal_is_gated_for_human_approval(self) -> None:
        orchestrator = GovernedAgentOrchestrator()
        result = orchestrator.run(
            "data_quality_agent",
            {"critical_failure": True, "failed_rules": ["target_leakage"]},
            evidence_source="quality-report/run-42",
        )
        self.assertEqual(result.proposal.action, "quarantine_model_run")
        self.assertEqual(result.policy_decision.decision, "PENDING_HUMAN_APPROVAL")
        self.assertTrue(result.policy_decision.human_approval_required)
        self.assertTrue(orchestrator.audit_log.verify())

    def test_customer_decision_and_unlisted_actions_are_denied(self) -> None:
        engine = PolicyEngine()
        evidence = ("ev-123",)
        forbidden = engine.evaluate(
            ActionProposal("approve_customer_credit", "model says yes", evidence, "unsafe_agent")
        )
        unknown = engine.evaluate(
            ActionProposal("send_external_email", "notify", evidence, "unknown_agent")
        )
        self.assertEqual(forbidden.decision, "DENY")
        self.assertEqual(unknown.decision, "DENY")

    def test_audit_log_forms_a_hash_chain(self) -> None:
        log = AuditLog()
        first = log.append("evidence", "agent", {"a": 1})
        second = log.append("proposal", "agent", {"b": 2})
        self.assertEqual(second.previous_event_sha256, first.event_sha256)
        self.assertTrue(log.verify())


if __name__ == "__main__":
    unittest.main()

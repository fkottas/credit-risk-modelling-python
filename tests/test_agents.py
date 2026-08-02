from __future__ import annotations

import unittest

from creditriskbook.agents import GovernedMonitoringAgent
from creditriskbook.data.datasets import load_dataset
from creditriskbook.data.quality import assess_quality, inject_teaching_defects


class AgentTests(unittest.TestCase):
    def test_agent_halts_on_critical_data_failure_and_has_no_credit_authority(self) -> None:
        bundle = load_dataset("synthetic_retail", n_rows=500, seed=2)
        dirty = inject_teaching_defects(bundle, seed=3)
        report = assess_quality(bundle, dirty)
        recommendation = GovernedMonitoringAgent().review(report, {"pd_psi": 0.01, "roc_auc": 0.75})
        self.assertEqual(recommendation.status, "HALT")
        self.assertTrue(recommendation.human_approval_required)
        self.assertIn("approve_customer_credit", recommendation.prohibited_actions)
        self.assertEqual(len(recommendation.evidence_sha256), 64)

    def test_agent_escalates_material_prediction_drift(self) -> None:
        bundle = load_dataset("synthetic_retail", n_rows=500, seed=4)
        report = assess_quality(bundle)
        recommendation = GovernedMonitoringAgent().review(report, {"pd_psi": 0.31, "roc_auc": 0.74})
        self.assertEqual(recommendation.status, "ESCALATE")


if __name__ == "__main__":
    unittest.main()


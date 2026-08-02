from __future__ import annotations

import unittest

from creditriskbook.workflows import run_end_to_end


class WorkflowTests(unittest.TestCase):
    def test_synthetic_workflow_reaches_model_monitoring_and_ecl(self) -> None:
        result = run_end_to_end("synthetic_retail", n_rows=2_000, seed=23)
        self.assertEqual(result["dataset"]["key"], "synthetic_retail")
        self.assertGreater(result["rows"]["quarantined"], 0)
        self.assertFalse(result["quality_after"]["critical_failure"])
        self.assertGreater(result["pd_metrics"]["roc_auc"], 0.60)
        self.assertEqual(result["ecl"]["status"], "educational_simplification")
        self.assertGreater(result["ecl"]["total_probability_weighted_ecl"], 0)


if __name__ == "__main__":
    unittest.main()

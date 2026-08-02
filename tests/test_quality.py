from __future__ import annotations

import unittest

from creditriskbook.data.datasets import load_dataset
from creditriskbook.data.quality import assess_quality, inject_teaching_defects, quarantine_invalid_rows


class DataQualityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = load_dataset("synthetic_retail", n_rows=1_000, seed=7)

    def test_defects_are_detected_and_quarantined_without_imputation(self) -> None:
        dirty = inject_teaching_defects(self.bundle, seed=8, rate=0.02)
        before = assess_quality(self.bundle, dirty)
        self.assertTrue(before.critical_failure)
        self.assertIn("unique_application_id", before.failed_rules)
        self.assertIn("complete_model_fields", before.failed_rules)
        self.assertIn("valid_as_of_date", before.failed_rules)

        clean, quarantine = quarantine_invalid_rows(self.bundle, dirty)
        after = assess_quality(self.bundle, clean)
        self.assertFalse(after.critical_failure)
        self.assertGreater(len(quarantine), 0)
        self.assertFalse(clean[list(self.bundle.model_features)].isna().any().any())

    def test_source_frame_is_not_mutated(self) -> None:
        original_rows = len(self.bundle.frame)
        _ = inject_teaching_defects(self.bundle, seed=3)
        self.assertEqual(len(self.bundle.frame), original_rows)
        self.assertNotIn("target_derived_score", self.bundle.frame)


if __name__ == "__main__":
    unittest.main()


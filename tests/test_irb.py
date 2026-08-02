from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from creditriskbook.irb import (
    add_margin_of_conservatism,
    asset_correlation,
    calibrate_pd_to_long_run_average,
    grade_backtest,
    herfindahl_concentration,
    irb_capital,
    weighted_long_run_default_rate,
)


class IRBTests(unittest.TestCase):
    def test_asset_class_formulas_and_capital_reconciliation(self) -> None:
        pd_values = np.array([0.002, 0.01, 0.05])
        self.assertTrue(np.allclose(asset_correlation(pd_values, "residential_mortgage"), 0.15))
        self.assertTrue(
            np.allclose(asset_correlation(pd_values, "qualifying_revolving_retail"), 0.04)
        )
        corporate = irb_capital(
            pd_values,
            0.45,
            1_000_000,
            asset_class="corporate",
            maturity_years=2.5,
        )
        self.assertTrue(corporate.rows["capital"].is_monotonic_increasing)
        np.testing.assert_allclose(
            corporate.rows["risk_weighted_assets"], 12.5 * corporate.rows["capital"]
        )
        self.assertAlmostEqual(
            corporate.summary["risk_weighted_assets"],
            corporate.rows["risk_weighted_assets"].sum(),
        )

    def test_pd_calibration_matches_long_run_average(self) -> None:
        raw = np.array([0.005, 0.01, 0.02, 0.04, 0.08])
        result = calibrate_pd_to_long_run_average(raw, 0.03)
        self.assertAlmostEqual(result.post_calibration_mean, 0.03, places=8)
        self.assertTrue(((result.calibrated_pd > 0) & (result.calibrated_pd < 1)).all())
        history = pd.DataFrame({"defaults": [2, 3, 8], "obligors": [100, 120, 160]})
        self.assertAlmostEqual(weighted_long_run_default_rate(history), 13 / 380)

    def test_margin_of_conservatism_and_grade_backtest_are_auditable(self) -> None:
        final, audit = add_margin_of_conservatism(
            np.array([0.02, 0.40]),
            {"data": np.array([0.005, 0.02]), "method": 0.01},
        )
        np.testing.assert_allclose(final, [0.035, 0.43])
        self.assertIn("moc_total", audit)
        observations = pd.DataFrame(
            {
                "grade": ["A"] * 100 + ["B"] * 100,
                "pd": [0.01] * 100 + [0.05] * 100,
                "default": [1] + [0] * 99 + [1] * 6 + [0] * 94,
            }
        )
        table = grade_backtest(observations)
        self.assertEqual(table["observations"].sum(), 200)
        self.assertTrue((table["lower_confidence"] <= table["upper_confidence"]).all())
        self.assertAlmostEqual(herfindahl_concentration(np.array([50, 30, 20])), 0.38)


if __name__ == "__main__":
    unittest.main()

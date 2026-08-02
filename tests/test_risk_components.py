from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from creditriskbook.capital import corporate_irb_capital, vasicek_portfolio_loss_quantile
from creditriskbook.decisioning import cutoff_table, expected_application_value
from creditriskbook.risk_components import calculate_workout_lgd, construct_ccf, ead_from_ccf
from creditriskbook.survival import cumulative_pd_from_hazard, kaplan_meier, marginal_pd_from_hazard


class RiskComponentTests(unittest.TestCase):
    def test_workout_lgd_discounts_recovery_and_preserves_raw_value(self) -> None:
        ledger = pd.DataFrame(
            {
                "account_id": ["A", "A", "B"],
                "default_date": ["2024-01-01"] * 3,
                "cashflow_date": ["2024-07-01", "2025-01-01", "2024-01-01"],
                "recovery": [3_000.0, 2_500.0, 11_000.0],
                "direct_cost": [200.0, 100.0, 0.0],
                "ead_at_default": [10_000.0, 10_000.0, 10_000.0],
                "effective_interest_rate": [0.10, 0.10, 0.10],
            }
        )
        result = calculate_workout_lgd(ledger).set_index("account_id")
        self.assertGreater(result.loc["A", "lgd_raw"], 0.45)
        self.assertLess(result.loc["A", "lgd_raw"], 0.55)
        self.assertLess(result.loc["B", "lgd_raw"], 0.0)
        self.assertEqual(result.loc["B", "lgd_model"], 0.0)
        self.assertNotEqual(result.loc["B", "boundary_adjustment"], 0.0)

    def test_ccf_and_ead_are_reconciled(self) -> None:
        observations = pd.DataFrame(
            {
                "facility_id": ["F1", "F2"],
                "drawn_reference": [4_000.0, 9_000.0],
                "limit_reference": [10_000.0, 10_000.0],
                "ead_at_default": [7_000.0, 10_500.0],
            }
        )
        result = construct_ccf(observations)
        self.assertAlmostEqual(result.loc[0, "ccf_raw"], 0.5)
        self.assertAlmostEqual(result.loc[1, "ccf_raw"], 1.5)
        self.assertEqual(result.loc[1, "ccf_model"], 1.0)
        ead = ead_from_ccf(
            result["drawn_reference"], result["undrawn_reference"], result["ccf_model"]
        )
        np.testing.assert_allclose(ead, [7_000.0, 10_000.0])

    def test_irb_capital_increases_with_pd_and_reconciles_to_rwa(self) -> None:
        result = corporate_irb_capital(
            np.array([0.005, 0.02, 0.08]), np.array([0.45] * 3), np.array([1_000_000.0] * 3)
        )
        self.assertTrue(np.all(np.diff(result["capital"]) > 0))
        np.testing.assert_allclose(result["risk_weighted_assets"], 12.5 * result["capital"])
        quantile = vasicek_portfolio_loss_quantile(0.02, 0.45, asset_correlation=0.15)
        self.assertGreater(quantile, 0.02 * 0.45)

    def test_survival_hazard_identity(self) -> None:
        hazard = np.array([0.05, 0.07, 0.10])
        marginal = marginal_pd_from_hazard(hazard)
        cumulative = cumulative_pd_from_hazard(hazard)
        self.assertAlmostEqual(cumulative[-1], 1 - np.prod(1 - hazard))
        self.assertTrue(np.allclose(cumulative, np.cumsum(marginal)))
        km = kaplan_meier(np.array([1, 2, 2, 3, 4]), np.array([1, 1, 0, 1, 0]))
        self.assertTrue(km["survival"].is_monotonic_decreasing)
        self.assertTrue(km["cumulative_pd"].is_monotonic_increasing)

    def test_cutoff_profit_and_expected_value(self) -> None:
        pd_values = np.array([0.01, 0.04, 0.20, 0.40])
        outcomes = np.array([0, 0, 1, 1])
        table = cutoff_table(pd_values, outcomes, cutoffs=np.array([0.05, 0.25]))
        self.assertEqual(table.loc[0, "approved"], 2)
        self.assertEqual(table.loc[1, "approved"], 3)
        values = expected_application_value(
            pd_values, performing_margin=1_000.0, loss_given_default=0.5, exposure=10_000.0
        )
        self.assertGreater(values[0], 0)
        self.assertLess(values[-1], 0)


if __name__ == "__main__":
    unittest.main()

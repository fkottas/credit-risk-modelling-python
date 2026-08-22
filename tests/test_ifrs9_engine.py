from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from creditriskbook.ifrs9 import (
    Scenario,
    StagingPolicy,
    assign_stages,
    build_provision_matrix,
    calculate_ecl,
    constant_hazard_curve,
    hazard_to_marginal,
    marginal_to_cumulative,
    marginal_to_hazard,
)


class IFRS9EngineTests(unittest.TestCase):
    def test_curve_transformations_reconcile(self) -> None:
        hazard = np.array([0.01, 0.02, 0.03, 0.04])
        marginal = hazard_to_marginal(hazard)
        recovered = marginal_to_hazard(marginal)
        np.testing.assert_allclose(recovered, hazard)
        self.assertAlmostEqual(marginal_to_cumulative(marginal)[-1], 1 - np.prod(1 - hazard))
        monthly = constant_hazard_curve(0.12, 24).reshape(-1)
        self.assertAlmostEqual(monthly[:12].sum(), 0.12, places=10)
        self.assertGreater(monthly.sum(), 0.12)

    def test_staging_policy_returns_reasons_and_flags(self) -> None:
        accounts = pd.DataFrame(
            {
                "account_id": ["A", "B", "C", "D"],
                "origination_pd_12m": [0.01, 0.01, 0.01, 0.02],
                "current_pd_12m": [0.011, 0.035, 0.012, 0.30],
                "days_past_due": [0, 0, 45, 95],
                "watchlist_flag": [False, False, False, False],
                "default_flag": [False, False, False, True],
            }
        )
        result = assign_stages(accounts, StagingPolicy())
        self.assertEqual(result["stage"].tolist(), [1, 2, 2, 3])
        self.assertEqual(result.loc[1, "stage_reason"], "relative_pd_increase")
        self.assertEqual(result.loc[2, "stage_reason"], "30_dpd_backstop")
        self.assertEqual(result.loc[3, "stage_reason"], "default_flag")

    def test_multiscenario_ecl_reconciles_and_stage2_uses_lifetime(self) -> None:
        rows = []
        for account_id, stage in (("S1", 1), ("S2", 2)):
            curve = constant_hazard_curve(0.12, 24).reshape(-1)
            for period, marginal in enumerate(curve, start=1):
                rows.append(
                    {
                        "account_id": account_id,
                        "period": period,
                        "stage": stage,
                        "marginal_pd": marginal,
                        "lgd": 0.40,
                        "ead": max(10_000 - 300 * (period - 1), 1_000),
                        "effective_interest_rate": 0.06,
                    }
                )
        scenarios = (
            Scenario("upside", 0.20, 0.8, 0.9, 0.98),
            Scenario("base", 0.55),
            Scenario("downside", 0.25, 1.5, 1.2, 1.05),
        )
        result = calculate_ecl(pd.DataFrame(rows), scenarios)
        account = result.account.set_index("account_id")
        self.assertGreater(account.loc["S2", "ecl"], account.loc["S1", "ecl"])
        self.assertTrue(np.allclose(result.reconciliation["amount"], result.account["ecl"].sum()))
        self.assertEqual(len(result.scenario), 6)
        first_month = result.detail.loc[result.detail["period"].eq(1), "discount_factor"].iloc[0]
        self.assertAlmostEqual(first_month, (1.0 + 0.06) ** (-1.0 / 12.0))

    def test_provision_matrix_applies_forward_multiplier(self) -> None:
        history = pd.DataFrame(
            {
                "aging_bucket": ["current", "current", "31-60", "31-60"],
                "exposure": [1_000, 2_000, 800, 1_200],
                "credit_loss": [5, 10, 80, 120],
            }
        )
        matrix = build_provision_matrix(history, forward_multipliers={"31-60": 1.25})
        late = matrix.set_index("aging_bucket").loc["31-60"]
        self.assertGreater(late["adjusted_loss_rate"], late["historical_loss_rate"])
        self.assertAlmostEqual(late["ecl"], late["exposure"] * late["adjusted_loss_rate"])


if __name__ == "__main__":
    unittest.main()

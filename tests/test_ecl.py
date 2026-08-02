from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from creditriskbook.ecl import educational_ecl, lifetime_pd_from_constant_hazard


class ECLTests(unittest.TestCase):
    def test_lifetime_pd_is_monotonic_in_horizon(self) -> None:
        values = lifetime_pd_from_constant_hazard(np.array([0.10, 0.10, 0.10]), np.array([1, 2, 5]))
        self.assertTrue(np.all(np.diff(values) > 0))
        self.assertAlmostEqual(values[0], 0.10)

    def test_stage_three_uses_full_default_probability(self) -> None:
        exposures = pd.DataFrame(
            {
                "stage": [1, 2, 3],
                "pd_12m": [0.05, 0.05, 0.05],
                "lgd": [0.40, 0.40, 0.40],
                "ead": [10_000, 10_000, 10_000],
                "remaining_months": [12, 36, 36],
                "effective_interest_rate": [0.05, 0.05, 0.05],
            }
        )
        result = educational_ecl(exposures)
        self.assertGreater(result.loc[1, "ecl_probability_weighted"], result.loc[0, "ecl_probability_weighted"])
        self.assertGreater(result.loc[2, "ecl_probability_weighted"], result.loc[1, "ecl_probability_weighted"])
        self.assertTrue((result["ecl_downside"] >= result["ecl_base"]).all())


if __name__ == "__main__":
    unittest.main()


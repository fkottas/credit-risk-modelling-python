"""Explicitly simplified expected-credit-loss teaching functions."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd

DEFAULT_SCENARIO_WEIGHTS = {"upside": 0.20, "base": 0.55, "downside": 0.25}
DEFAULT_PD_MULTIPLIERS = {"upside": 0.75, "base": 1.00, "downside": 1.45}
DEFAULT_LGD_MULTIPLIERS = {"upside": 0.90, "base": 1.00, "downside": 1.15}


def lifetime_pd_from_constant_hazard(pd_12m: np.ndarray, years: np.ndarray) -> np.ndarray:
    pd_one_year = np.clip(np.asarray(pd_12m, dtype=float), 0.0, 1.0)
    horizon = np.maximum(np.asarray(years, dtype=float), 0.0)
    return 1.0 - np.power(1.0 - pd_one_year, horizon)


def educational_ecl(
    exposures: pd.DataFrame,
    *,
    scenario_weights: Mapping[str, float] = DEFAULT_SCENARIO_WEIGHTS,
    pd_multipliers: Mapping[str, float] = DEFAULT_PD_MULTIPLIERS,
    lgd_multipliers: Mapping[str, float] = DEFAULT_LGD_MULTIPLIERS,
) -> pd.DataFrame:
    """Calculate a compact probability-weighted ECL illustration.

    Required columns are `stage`, `pd_12m`, `lgd`, `ead`, `remaining_months`,
    and `effective_interest_rate`. This is not a full IFRS 9 accounting engine:
    it uses a constant-hazard lifetime-PD approximation and one average timing
    point rather than a contractual monthly cash-flow schedule.
    """

    required = {
        "stage",
        "pd_12m",
        "lgd",
        "ead",
        "remaining_months",
        "effective_interest_rate",
    }
    missing = required - set(exposures.columns)
    if missing:
        raise ValueError(f"Missing ECL columns: {sorted(missing)}")
    if set(scenario_weights) != set(pd_multipliers) or set(scenario_weights) != set(
        lgd_multipliers
    ):
        raise ValueError("Scenario keys must agree")
    if not np.isclose(sum(scenario_weights.values()), 1.0):
        raise ValueError("Scenario weights must sum to 1")

    result = exposures.copy()
    stage = result["stage"].astype(int).to_numpy()
    if not np.isin(stage, [1, 2, 3]).all():
        raise ValueError("Stage must be 1, 2, or 3")
    years = np.maximum(result["remaining_months"].to_numpy(float) / 12.0, 1 / 12)
    timing = np.where(stage == 1, np.minimum(years, 1.0), years / 2.0)
    discount = np.power(1.0 + result["effective_interest_rate"].to_numpy(float), -timing)
    ead = np.maximum(result["ead"].to_numpy(float), 0.0)
    base_pd = np.clip(result["pd_12m"].to_numpy(float), 0.0, 1.0)
    base_lgd = np.clip(result["lgd"].to_numpy(float), 0.0, 1.0)

    weighted = np.zeros(len(result), dtype=float)
    for scenario, weight in scenario_weights.items():
        pd_12m = np.clip(base_pd * pd_multipliers[scenario], 0.0, 1.0)
        lifetime_pd = lifetime_pd_from_constant_hazard(pd_12m, years)
        applicable_pd = np.where(stage == 1, pd_12m, np.where(stage == 2, lifetime_pd, 1.0))
        scenario_lgd = np.clip(base_lgd * lgd_multipliers[scenario], 0.0, 1.0)
        scenario_ecl = applicable_pd * scenario_lgd * ead * discount
        result[f"ecl_{scenario}"] = scenario_ecl
        weighted += weight * scenario_ecl
    result["ecl_probability_weighted"] = weighted
    return result

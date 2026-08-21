"""Survival and lifetime-PD utilities without specialist survival libraries."""

from __future__ import annotations

import numpy as np
import pandas as pd


def kaplan_meier(durations: np.ndarray, events: np.ndarray) -> pd.DataFrame:
    """Compute the Kaplan-Meier product-limit curve and Greenwood standard error."""

    time = np.asarray(durations, dtype=float)
    event = np.asarray(events, dtype=int)
    if len(time) != len(event) or np.any(time < 0) or not np.isin(event, [0, 1]).all():
        raise ValueError(
            "Durations must be non-negative and events must be binary with matching length"
        )
    rows = []
    survival = 1.0
    greenwood = 0.0
    for t in np.sort(np.unique(time[event == 1])):
        at_risk = int(np.sum(time >= t))
        defaults = int(np.sum((time == t) & (event == 1)))
        censored = int(np.sum((time == t) & (event == 0)))
        survival *= 1.0 - defaults / at_risk
        if at_risk > defaults:
            greenwood += defaults / (at_risk * (at_risk - defaults))
        standard_error = survival * np.sqrt(greenwood)
        rows.append(
            {
                "time": float(t),
                "at_risk": at_risk,
                "events": defaults,
                "censored": censored,
                "survival": survival,
                "cumulative_pd": 1.0 - survival,
                "standard_error": standard_error,
            }
        )
    return pd.DataFrame(rows)


def marginal_pd_from_hazard(hazard: np.ndarray) -> np.ndarray:
    hazard_values = np.clip(np.asarray(hazard, dtype=float), 0.0, 1.0)
    survival_start = np.r_[1.0, np.cumprod(1.0 - hazard_values)[:-1]]
    return survival_start * hazard_values


def cumulative_pd_from_hazard(hazard: np.ndarray) -> np.ndarray:
    return np.cumsum(marginal_pd_from_hazard(hazard))

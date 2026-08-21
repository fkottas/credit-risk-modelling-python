"""Grade-level IRB validation summaries with exact confidence intervals."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import beta


def _clopper_pearson(defaults: int, total: int, alpha: float) -> tuple[float, float]:
    lower = 0.0 if defaults == 0 else float(beta.ppf(alpha / 2, defaults, total - defaults + 1))
    upper = (
        1.0 if defaults == total else float(beta.ppf(1 - alpha / 2, defaults + 1, total - defaults))
    )
    return lower, upper


def grade_backtest(
    observations: pd.DataFrame,
    *,
    grade_column: str = "grade",
    pd_column: str = "pd",
    target_column: str = "default",
    confidence: float = 0.95,
) -> pd.DataFrame:
    """Compare grade PD with observed default rates and binomial uncertainty."""

    required = {grade_column, pd_column, target_column}
    if required - set(observations):
        raise ValueError("Grade backtest input is missing required columns")
    if not 0.5 < confidence < 1:
        raise ValueError("confidence must be between 0.5 and 1")
    if not observations[target_column].isin([0, 1]).all():
        raise ValueError("target must be binary")
    if ((observations[pd_column] < 0) | (observations[pd_column] > 1)).any():
        raise ValueError("PD must be in [0, 1]")
    rows = []
    alpha = 1 - confidence
    for grade, group in observations.groupby(grade_column, sort=False):
        n = len(group)
        defaults = int(group[target_column].sum())
        lower, upper = _clopper_pearson(defaults, n, alpha)
        mean_pd = float(group[pd_column].mean())
        rows.append(
            {
                "grade": grade,
                "observations": n,
                "defaults": defaults,
                "observed_default_rate": defaults / n,
                "mean_pd": mean_pd,
                "lower_confidence": lower,
                "upper_confidence": upper,
                "pd_inside_observed_interval": lower <= mean_pd <= upper,
                "observed_minus_pd": defaults / n - mean_pd,
            }
        )
    return pd.DataFrame(rows)


def herfindahl_concentration(exposures: np.ndarray) -> float:
    """Return the exposure-share Herfindahl index."""

    values = np.asarray(exposures, dtype=float)
    if values.ndim != 1 or np.any(values < 0) or values.sum() <= 0:
        raise ValueError("exposures must be a non-negative vector with positive total")
    shares = values / values.sum()
    return float(np.square(shares).sum())

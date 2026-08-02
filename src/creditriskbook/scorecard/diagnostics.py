"""Diagnostics for transparent scorecard development and validation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm

from .model import LogisticScorecard


def variance_inflation_factors(X: pd.DataFrame) -> pd.DataFrame:
    """Calculate VIF with least squares, without a statistics-model library."""

    matrix = np.asarray(X, dtype=float)
    if matrix.ndim != 2 or not np.isfinite(matrix).all() or matrix.shape[1] < 2:
        raise ValueError("VIF requires at least two finite numeric columns")
    rows = []
    for index, feature in enumerate(X.columns):
        target = matrix[:, index]
        others = np.delete(matrix, index, axis=1)
        design = np.column_stack([np.ones(len(others)), others])
        fitted = design @ np.linalg.lstsq(design, target, rcond=None)[0]
        residual_ss = float(np.square(target - fitted).sum())
        total_ss = float(np.square(target - target.mean()).sum())
        r_squared = 1.0 - residual_ss / total_ss if total_ss > 0 else 1.0
        vif = np.inf if r_squared >= 1 - 1e-12 else 1.0 / (1.0 - r_squared)
        rows.append({"feature": feature, "r_squared": r_squared, "vif": vif})
    return pd.DataFrame(rows).sort_values("vif", ascending=False)


def coefficient_inference(scorecard: LogisticScorecard) -> pd.DataFrame:
    """Return approximate IRLS coefficient uncertainty for independent review."""

    if not scorecard.features_ or scorecard.model_.covariance_ is None:
        raise RuntimeError("Fit the scorecard before requesting coefficient inference")
    coefficient = np.r_[scorecard.model_.intercept_, scorecard.model_.coef_]
    standard_error = np.sqrt(np.maximum(np.diag(scorecard.model_.covariance_), 0.0))
    z_value = np.divide(
        coefficient,
        standard_error,
        out=np.full_like(coefficient, np.nan),
        where=standard_error > 0,
    )
    return pd.DataFrame(
        {
            "term": ("intercept", *scorecard.features_),
            "coefficient": coefficient,
            "standard_error": standard_error,
            "z_value": z_value,
            "p_value": 2 * norm.sf(np.abs(z_value)),
        }
    )


def binned_population_stability(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    *,
    smoothing: float = 1e-6,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calculate bin-level and characteristic-level PSI for categorical bins."""

    missing = set(reference.columns) - set(current.columns)
    if missing:
        raise ValueError(f"Current sample is missing binned features: {sorted(missing)}")
    rows = []
    for feature in reference.columns:
        categories = sorted(set(reference[feature].astype(str)) | set(current[feature].astype(str)))
        reference_share = reference[feature].astype(str).value_counts(normalize=True)
        current_share = current[feature].astype(str).value_counts(normalize=True)
        for category in categories:
            expected = max(float(reference_share.get(category, 0.0)), smoothing)
            actual = max(float(current_share.get(category, 0.0)), smoothing)
            component = (actual - expected) * np.log(actual / expected)
            rows.append(
                {
                    "feature": feature,
                    "bin": category,
                    "reference_share": expected,
                    "current_share": actual,
                    "psi_component": component,
                }
            )
    detail = pd.DataFrame(rows)
    summary = (
        detail.groupby("feature", as_index=False)["psi_component"]
        .sum()
        .rename(columns={"psi_component": "psi"})
        .sort_values("psi", ascending=False)
    )
    return detail, summary


def scorecard_policy_flags(
    scorecard: LogisticScorecard,
    *,
    high_iv: float = 0.50,
    minimum_bin_count: int = 30,
) -> pd.DataFrame:
    """Create review flags; thresholds are policy inputs, not universal rules."""

    points = scorecard.points_table()
    rows = []
    for feature, table in points.groupby("feature", sort=False):
        iv = float(table["iv_component"].sum())
        flags = []
        if iv >= high_iv:
            flags.append("high_iv_check_leakage")
        if int(table["count"].min()) < minimum_bin_count:
            flags.append("small_bin")
        if (table["bad_rate"].isin([0.0, 1.0])).any():
            flags.append("zero_event_or_zero_non_event")
        rows.append(
            {
                "feature": feature,
                "information_value": iv,
                "minimum_bin_count": int(table["count"].min()),
                "flags": ";".join(flags) if flags else "none",
            }
        )
    return pd.DataFrame(rows).sort_values("information_value", ascending=False)

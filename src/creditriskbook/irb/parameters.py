"""IRB parameter calibration and conservatism utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CalibrationResult:
    calibrated_pd: np.ndarray
    scale_factor: float
    pre_calibration_mean: float
    target_long_run_average: float
    post_calibration_mean: float


def weighted_long_run_default_rate(
    annual: pd.DataFrame,
    *,
    defaults_column: str = "defaults",
    obligors_column: str = "obligors",
    weighting: str = "obligor",
) -> float:
    """Estimate a long-run average using obligor or equal-year weighting."""

    required = {defaults_column, obligors_column}
    if required - set(annual):
        raise ValueError("Annual default history is missing required columns")
    defaults = annual[defaults_column].to_numpy(float)
    obligors = annual[obligors_column].to_numpy(float)
    if np.any(defaults < 0) or np.any(obligors <= 0) or np.any(defaults > obligors):
        raise ValueError("Annual default counts and obligor counts are inconsistent")
    rates = defaults / obligors
    if weighting == "obligor":
        return float(defaults.sum() / obligors.sum())
    if weighting == "year":
        return float(rates.mean())
    raise ValueError("weighting must be 'obligor' or 'year'")


def calibrate_pd_to_long_run_average(
    raw_pd: np.ndarray,
    target_long_run_average: float,
    *,
    weights: np.ndarray | None = None,
    floor: float = 0.0005,
) -> CalibrationResult:
    """Apply an odds-scale intercept shift to match a target central tendency."""

    probability = np.asarray(raw_pd, dtype=float)
    if probability.ndim != 1 or np.any((probability <= 0) | (probability >= 1)):
        raise ValueError("raw_pd must be one-dimensional and strictly between zero and one")
    if not floor <= target_long_run_average < 1:
        raise ValueError("target long-run average is outside the valid range")
    sample_weight = np.ones(len(probability)) if weights is None else np.asarray(weights, float)
    if sample_weight.shape != probability.shape or np.any(sample_weight <= 0):
        raise ValueError("weights must be positive and match raw_pd")

    def weighted_mean(shift: float) -> float:
        logit = np.log(probability / (1 - probability)) + shift
        calibrated = 1 / (1 + np.exp(-np.clip(logit, -35, 35)))
        calibrated = np.clip(calibrated, floor, 1 - 1e-10)
        return float(np.average(calibrated, weights=sample_weight))

    lower, upper = -30.0, 30.0
    for _ in range(100):
        middle = (lower + upper) / 2
        if weighted_mean(middle) < target_long_run_average:
            lower = middle
        else:
            upper = middle
    shift = (lower + upper) / 2
    odds = probability / (1 - probability) * np.exp(shift)
    calibrated = np.clip(odds / (1 + odds), floor, 1 - 1e-10)
    return CalibrationResult(
        calibrated_pd=calibrated,
        scale_factor=float(np.exp(shift)),
        pre_calibration_mean=float(np.average(probability, weights=sample_weight)),
        target_long_run_average=float(target_long_run_average),
        post_calibration_mean=float(np.average(calibrated, weights=sample_weight)),
    )


def add_margin_of_conservatism(
    estimate: np.ndarray,
    components: dict[str, np.ndarray | float],
    *,
    upper_bound: float = 1.0,
) -> tuple[np.ndarray, pd.DataFrame]:
    """Add named MoC components and return a row-level audit table."""

    base = np.asarray(estimate, dtype=float)
    if base.ndim != 1 or np.any(base < 0):
        raise ValueError("estimate must be a non-negative one-dimensional array")
    audit = pd.DataFrame({"estimate": base})
    total = np.zeros(len(base), dtype=float)
    for name, values in components.items():
        component = np.broadcast_to(np.asarray(values, float), base.shape).copy()
        if not np.isfinite(component).all() or np.any(component < 0):
            raise ValueError(f"MoC component {name!r} must be finite and non-negative")
        audit[f"moc_{name}"] = component
        total += component
    audit["moc_total"] = total
    audit["final_estimate"] = np.clip(base + total, 0.0, upper_bound)
    audit["boundary_adjustment"] = audit["final_estimate"] - (base + total)
    return audit["final_estimate"].to_numpy(), audit


def downturn_lgd(
    observed_lgd: np.ndarray,
    downturn_indicator: np.ndarray,
    *,
    minimum_uplift: float = 0.0,
) -> dict[str, float]:
    """Estimate a simple downturn uplift while keeping raw evidence visible."""

    lgd = np.asarray(observed_lgd, dtype=float)
    indicator = np.asarray(downturn_indicator, dtype=bool)
    if lgd.shape != indicator.shape or lgd.ndim != 1 or np.any((lgd < 0) | (lgd > 1)):
        raise ValueError("LGD and downturn indicators must be valid matching vectors")
    if not indicator.any() or indicator.all() or minimum_uplift < 0:
        raise ValueError(
            "Both downturn and non-downturn observations and non-negative uplift are required"
        )
    long_run = float(lgd.mean())
    downturn_mean = float(lgd[indicator].mean())
    uplift = max(downturn_mean - long_run, minimum_uplift)
    return {
        "long_run_lgd": long_run,
        "downturn_observed_lgd": downturn_mean,
        "uplift": uplift,
        "downturn_lgd": min(long_run + uplift, 1.0),
    }

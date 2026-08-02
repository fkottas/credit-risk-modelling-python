"""Probability term-structure transformations used by the ECL engine."""

from __future__ import annotations

import numpy as np


def _probability_array(values: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim == 0:
        array = array.reshape(1)
    if not np.isfinite(array).all() or np.any((array < 0) | (array > 1)):
        raise ValueError(f"{name} must contain finite probabilities in [0, 1]")
    return array


def hazard_to_marginal(hazard: np.ndarray, *, axis: int = -1) -> np.ndarray:
    """Convert conditional period hazards into unconditional marginal PDs."""

    conditional = _probability_array(hazard, "hazard")
    survival_after = np.cumprod(1.0 - conditional, axis=axis)
    survival_before = np.roll(survival_after, 1, axis=axis)
    index = [slice(None)] * conditional.ndim
    index[axis] = 0
    survival_before[tuple(index)] = 1.0
    return survival_before * conditional


def marginal_to_cumulative(marginal_pd: np.ndarray, *, axis: int = -1) -> np.ndarray:
    """Convert unconditional marginal PDs into cumulative PDs."""

    marginal = _probability_array(marginal_pd, "marginal_pd")
    cumulative = np.cumsum(marginal, axis=axis)
    if np.any(cumulative > 1.0 + 1e-10):
        raise ValueError("Marginal probabilities sum to more than one")
    return np.clip(cumulative, 0.0, 1.0)


def cumulative_to_marginal(cumulative_pd: np.ndarray, *, axis: int = -1) -> np.ndarray:
    """Convert a non-decreasing cumulative PD curve into marginal PDs."""

    cumulative = _probability_array(cumulative_pd, "cumulative_pd")
    difference = np.diff(cumulative, axis=axis, prepend=0.0)
    if np.any(difference < -1e-10):
        raise ValueError("Cumulative PD must be non-decreasing")
    return np.clip(difference, 0.0, 1.0)


def marginal_to_hazard(marginal_pd: np.ndarray, *, axis: int = -1) -> np.ndarray:
    """Convert unconditional marginal PDs into conditional period hazards."""

    marginal = _probability_array(marginal_pd, "marginal_pd")
    cumulative = marginal_to_cumulative(marginal, axis=axis)
    cumulative_before = np.roll(cumulative, 1, axis=axis)
    index = [slice(None)] * marginal.ndim
    index[axis] = 0
    cumulative_before[tuple(index)] = 0.0
    survival_before = 1.0 - cumulative_before
    hazard = np.divide(
        marginal,
        survival_before,
        out=np.zeros_like(marginal),
        where=survival_before > 1e-12,
    )
    return np.clip(hazard, 0.0, 1.0)


def scale_hazard(hazard: np.ndarray, multiplier: float) -> np.ndarray:
    """Apply a scenario multiplier on the cumulative-intensity scale.

    ``1 - (1 - h)**multiplier`` stays in the probability domain and avoids the
    arbitrary clipping produced by multiplying probabilities directly.
    """

    conditional = _probability_array(hazard, "hazard")
    if not np.isfinite(multiplier) or multiplier < 0:
        raise ValueError("multiplier must be a finite non-negative number")
    return 1.0 - np.power(1.0 - conditional, float(multiplier))


def constant_hazard_curve(
    pd_12m: float | np.ndarray,
    periods: int,
    *,
    periods_per_year: int = 12,
) -> np.ndarray:
    """Create marginal PD curves whose first-year cumulative PD equals PD12."""

    if periods < 1 or periods_per_year < 1:
        raise ValueError("periods and periods_per_year must be positive integers")
    annual = _probability_array(np.asarray(pd_12m), "pd_12m")
    period_hazard = 1.0 - np.power(1.0 - annual, 1.0 / periods_per_year)
    hazards = np.repeat(period_hazard[..., np.newaxis], periods, axis=-1)
    return hazard_to_marginal(hazards)

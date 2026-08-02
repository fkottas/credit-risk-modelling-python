"""Small, inspectable monitoring metrics used by the book examples."""

from __future__ import annotations

import numpy as np


def population_stability_index(
    reference: np.ndarray,
    current: np.ndarray,
    *,
    bins: int = 10,
    epsilon: float = 1e-6,
) -> float:
    expected = np.asarray(reference, dtype=float)
    actual = np.asarray(current, dtype=float)
    if expected.size < bins * 2 or actual.size < bins * 2:
        raise ValueError("Both samples must contain at least twice the requested bin count")
    edges = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    if edges.size < 3:
        return 0.0 if np.allclose(expected.mean(), actual.mean()) else float("inf")
    edges[0], edges[-1] = -np.inf, np.inf
    expected_counts = np.histogram(expected, bins=edges)[0] / expected.size
    actual_counts = np.histogram(actual, bins=edges)[0] / actual.size
    expected_counts = np.clip(expected_counts, epsilon, None)
    actual_counts = np.clip(actual_counts, epsilon, None)
    return float(np.sum((actual_counts - expected_counts) * np.log(actual_counts / expected_counts)))


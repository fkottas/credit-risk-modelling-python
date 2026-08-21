"""Chapter 2: Expected Loss, Unexpected Loss, and the Loss Distribution.

Standalone construction code: no creditriskbook imports.
"""

import numpy as np


def loss_distribution(pd, lgd, ead, *, simulations=20_000, seed=802):
    """Simulate Bernoulli defaults and expose EL, quantile loss, and unexpected loss."""
    pd, lgd, ead = map(lambda x: np.asarray(x, dtype=float), (pd, lgd, ead))
    if not (pd.shape == lgd.shape == ead.shape):
        raise ValueError("PD, LGD, and EAD must have the same shape")
    if np.any((pd < 0) | (pd > 1)) or np.any((lgd < 0) | (lgd > 1)):
        raise ValueError("PD and LGD must be proportions")
    rng = np.random.default_rng(seed)
    defaults = rng.random((simulations, len(pd))) < pd
    simulated = (defaults * lgd * ead).sum(axis=1)
    analytical_el = float(np.sum(pd * lgd * ead))
    q99 = float(np.quantile(simulated, 0.99, method="higher"))
    return {
        "analytical_el": analytical_el,
        "simulated_mean": simulated.mean(),
        "q99": q99,
        "unexpected_loss_99": q99 - analytical_el,
    }


result = loss_distribution([0.02, 0.05, 0.10], [0.35, 0.45, 0.60], [10_000, 8_000, 5_000])
print({key: round(value, 2) for key, value in result.items()})

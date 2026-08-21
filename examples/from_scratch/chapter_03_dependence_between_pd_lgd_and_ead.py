"""Chapter 3: Dependence Between PD, LGD, and EAD.

Standalone construction code: no creditriskbook imports.
"""

import numpy as np


def dependent_component_losses(n=50_000, seed=803):
    """Create a transparent common-factor dependence experiment."""
    rng = np.random.default_rng(seed)
    systematic = rng.normal(size=n)
    idiosyncratic = rng.normal(size=(n, 3))
    latent = 0.55 * systematic[:, None] + np.sqrt(1 - 0.55**2) * idiosyncratic
    defaults = latent < np.array([-1.65, -1.40, -1.15])
    lgd = np.clip(0.40 - 0.08 * systematic[:, None], 0.10, 0.90)
    ead = np.array([10_000.0, 8_000.0, 6_000.0]) * (1 + 0.06 * np.maximum(-systematic[:, None], 0))
    losses = defaults * lgd * ead
    portfolio = losses.sum(axis=1)
    return {
        "component_correlation": float(np.corrcoef(losses.T)[0, 1]),
        "mean_loss": float(portfolio.mean()),
        "q99_loss": float(np.quantile(portfolio, 0.99)),
    }


result = dependent_component_losses()
print({key: round(value, 3) for key, value in result.items()})

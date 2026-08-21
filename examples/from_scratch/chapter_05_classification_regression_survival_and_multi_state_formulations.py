"""Chapter 5: Classification, Regression, Survival, and Multi-State Formulations.

Standalone construction code: no creditriskbook imports.
"""

import numpy as np


def sigmoid(linear_predictor):
    z = np.clip(np.asarray(linear_predictor, dtype=float), -35, 35)
    return 1.0 / (1.0 + np.exp(-z))


def cumulative_pd_from_hazards(hazards):
    h = np.asarray(hazards, dtype=float)
    if np.any((h < 0) | (h > 1)):
        raise ValueError("Hazards must lie in [0, 1]")
    return 1.0 - np.cumprod(1.0 - h)


classification_pd = sigmoid([-2.0, -0.5, 1.0])
regression_lgd = np.clip([0.18, 0.42, 0.77], 0, 1)
survival_pd = cumulative_pd_from_hazards([0.02, 0.03, 0.05, 0.08])
print("Classification PD:", np.round(classification_pd, 4).tolist())
print("Regression LGD:", np.round(regression_lgd, 4).tolist())
print("Cumulative lifetime PD:", np.round(survival_pd, 4).tolist())

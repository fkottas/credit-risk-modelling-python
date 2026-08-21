"""Chapter 5: Classification, Regression, Survival, and Multi-State Formulations.

Standalone construction code: no creditriskbook imports.
"""

from math import exp


def sigmoid(value):
    return 1.0 / (1.0 + exp(-value))


def cumulative_pd(hazards):
    survival = 1.0
    result = []
    for hazard in hazards:
        if not 0.0 <= hazard <= 1.0:
            raise ValueError("Each hazard must lie between zero and one")
        survival *= 1.0 - hazard
        result.append(1.0 - survival)
    return result


classification_pd = [round(sigmoid(value), 4) for value in (-2.0, -0.5, 1.0)]
regression_lgd = [0.18, 0.42, 0.77]
lifetime_pd = [round(value, 4) for value in cumulative_pd([0.02, 0.03, 0.05, 0.08])]
print("Classification PD:", classification_pd)
print("Regression LGD:", regression_lgd)
print("Cumulative lifetime PD:", lifetime_pd)

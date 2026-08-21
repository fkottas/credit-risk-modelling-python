"""Chapter 17: CECL and Its Relationship to IFRS 9.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def cecl_loss_rate(exposure, historical_loss_rate, qualitative_adjustment=0.0):
    adjusted = historical_loss_rate + qualitative_adjustment
    if exposure < 0 or not 0 <= adjusted <= 1:
        raise ValueError("Invalid exposure or adjusted loss rate")
    return exposure * adjusted


pools = pd.DataFrame(
    {
        "pool": ["prime", "near_prime", "subprime"],
        "exposure": [1_000_000, 600_000, 250_000],
        "historical_loss_rate": [0.008, 0.035, 0.110],
        "qualitative_adjustment": [0.002, 0.005, 0.010],
    }
)
pools["lifetime_cecl"] = pools.apply(
    lambda r: cecl_loss_rate(r.exposure, r.historical_loss_rate, r.qualitative_adjustment), axis=1
)
print(pools.to_string(index=False))
print("Total CECL:", pools["lifetime_cecl"].sum())

"""Chapter 13: Basel Credit Risk Architecture: Standardised and IRB Approaches.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def standardised_rwa(exposure: float, risk_weight: float) -> dict:
    if exposure < 0 or risk_weight < 0:
        raise ValueError("Exposure and risk weight cannot be negative")
    rwa = exposure * risk_weight
    return {
        "exposure": exposure,
        "risk_weight": risk_weight,
        "rwa": rwa,
        "minimum_capital_8pct": 0.08 * rwa,
    }


rows = [standardised_rwa(1_000_000, rw) for rw in (0.20, 0.50, 1.00, 1.50)]
print(pd.DataFrame(rows).to_string(index=False))

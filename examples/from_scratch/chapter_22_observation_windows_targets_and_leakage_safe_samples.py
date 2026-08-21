"""Chapter 22: Observation Windows, Targets, and Leakage-Safe Samples.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def build_default_target(reference_dates, default_dates, horizon_months=12):
    reference = pd.to_datetime(reference_dates)
    default = pd.to_datetime(default_dates)
    horizon_end = reference + pd.offsets.DateOffset(months=horizon_months)
    observed = default.notna() & (default > reference) & (default <= horizon_end)
    return pd.DataFrame(
        {
            "reference_date": reference,
            "horizon_end": horizon_end,
            "default_date": default,
            "default_in_horizon": observed.astype(int),
        }
    )


target = build_default_target(
    ["2024-01-31", "2024-01-31", "2024-01-31"],
    ["2024-08-15", "2025-05-01", None],
)
print(target.to_string(index=False))

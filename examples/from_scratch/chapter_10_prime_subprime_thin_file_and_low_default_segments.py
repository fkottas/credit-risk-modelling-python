"""Chapter 10: Prime, Subprime, Thin-File, and Low-Default Segments.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def assign_segment(row) -> str:
    if row["business_obligor"] and row["observed_defaults"] < 5:
        return "low_default_portfolio"
    if row["bureau_months"] < 12 or row["open_trades"] < 2:
        return "thin_file"
    if row["estimated_pd"] >= 0.12:
        return "subprime"
    return "prime"


borrowers = pd.DataFrame(
    {
        "borrower": ["A", "B", "C", "D"],
        "estimated_pd": [0.02, 0.18, 0.07, 0.03],
        "bureau_months": [96, 72, 5, 60],
        "open_trades": [5, 4, 1, 3],
        "business_obligor": [False, False, False, True],
        "observed_defaults": [100, 100, 100, 2],
    }
)
borrowers["segment"] = borrowers.apply(assign_segment, axis=1)
print(borrowers[["borrower", "segment"]].to_string(index=False))

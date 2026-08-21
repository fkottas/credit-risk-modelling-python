"""Chapter 23: Data Profiling, Reconciliation, Cleaning, and Quarantine.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def clean_performance(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return accepted rows and a row-level quarantine; do not impute or winsorise."""
    frame = raw.copy(deep=True)
    issue_rows = []
    checks = {
        "negative_dpd": frame["dpd"] < 0,
        "negative_balance": frame["balance"] < 0,
        "payment_exceeds_balance_plus_tolerance": frame["payment"] > frame["balance"] * 1.25,
        "future_snapshot": frame["snapshot_date"] > frame["as_of_date"],
    }
    bad = pd.Series(False, index=frame.index)
    for rule, mask in checks.items():
        bad |= mask
        issue_rows.extend({"row_id": int(i), "rule": rule} for i in frame.index[mask])
    return frame.loc[~bad].copy(), pd.DataFrame(issue_rows)


raw = pd.DataFrame(
    {
        "dpd": [0, -4, 35, 0],
        "balance": [1000, 800, -10, 500],
        "payment": [100, 90, 20, 900],
        "snapshot_date": pd.to_datetime(["2025-01-31", "2025-01-31", "2025-03-31", "2025-01-31"]),
        "as_of_date": pd.to_datetime(["2025-02-01"] * 4),
    }
)
accepted, quarantine = clean_performance(raw)
print("Accepted rows:", accepted.index.tolist())
print(quarantine.to_string(index=False))

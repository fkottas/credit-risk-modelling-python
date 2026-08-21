"""Chapter 24: Behavioural and Bureau Feature Engineering.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def behavioral_features(performance, contracts, reference_date):
    ref = pd.Timestamp(reference_date)
    known_perf = performance.loc[performance["snapshot_date"] <= ref].sort_values("snapshot_date")
    window_6m = known_perf.loc[known_perf["snapshot_date"] > ref - pd.DateOffset(months=6)]
    known_contracts = contracts.loc[contracts["open_date"] <= ref]
    new_6m = known_contracts.loc[known_contracts["open_date"] > ref - pd.DateOffset(months=6)]
    return {
        "last_dpd": int(known_perf.iloc[-1]["dpd"]) if len(known_perf) else None,
        "max_dpd_6m": int(window_6m["dpd"].max()) if len(window_6m) else None,
        "count_dpd30_6m": int((window_6m["dpd"] >= 30).sum()),
        "mean_utilisation_6m": float(window_6m["balance"].div(window_6m["limit"]).mean()),
        "CountContractsLast6Months": int(len(new_6m)),
    }


performance = pd.DataFrame(
    {
        "snapshot_date": pd.to_datetime(["2025-01-31", "2025-02-28", "2025-03-31", "2025-04-30"]),
        "dpd": [0, 12, 45, 8],
        "balance": [500, 650, 800, 700],
        "limit": [1000] * 4,
    }
)
contracts = pd.DataFrame(
    {
        "contract_id": ["C1", "C2", "C3"],
        "open_date": pd.to_datetime(["2023-01-01", "2025-01-20", "2025-05-01"]),
    }
)
print(behavioral_features(performance, contracts, "2025-04-30"))

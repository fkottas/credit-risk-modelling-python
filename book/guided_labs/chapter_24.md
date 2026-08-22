## Worked calculation — How are maxDPD, lastDPD, delinquency counts, utilisation, and recent-contract counts constructed?

These features summarise different aspects of recency, severity, frequency, and exposure and therefore should not be treated as substitutes.

**Companion case:** `synthetic_behavioral_history`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
maxDPD_i(w)=\max_{t_i-w<s\le t_i}DPD_{i,s},\quad CountContracts_i(w)=\sum_j\mathbf{1}\{t_i-w<open_{ij}\le t_i\}
\]


### Python implementation

```python
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


performance = pd.DataFrame({
    "snapshot_date": pd.to_datetime(["2025-01-31", "2025-02-28", "2025-03-31", "2025-04-30"]),
    "dpd": [0, 12, 45, 8], "balance": [500, 650, 800, 700], "limit": [1000] * 4,
})
contracts = pd.DataFrame({"contract_id": ["C1", "C2", "C3"],
                          "open_date": pd.to_datetime(["2023-01-01", "2025-01-20", "2025-05-01"])})
print(behavioral_features(performance, contracts, "2025-04-30"))
```

### Executed result

```output
{'last_dpd': 8, 'max_dpd_6m': 45, 'count_dpd30_6m': 1, 'mean_utilisation_6m': 0.6625, 'CountContractsLast6Months': 1}
```

### Interpretation

The example distinguishes recency (`last_dpd`), severity (`max_dpd_6m`), frequency and new-credit activity. The values differ because each feature answers a different behavioural question.

**Validation:** Calculate each feature from raw event rows and prove that no event after the reference date enters the result.

### Exercises

1. Repeat the calculation with **synthetic behavioural history and student-supplied longitudinal credit data** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

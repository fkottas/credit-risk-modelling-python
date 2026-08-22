## Worked calculation — How are data defects detected, explained, corrected, or excluded?

Automatic imputation can hide source failure and alter model relationships.

**Companion case:** `synthetic_behavioral_history`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
Q=\sum_{k=1}^{K} w_k q_k
\]


![Figure 23.1 — Missing-value and rule-violation rates after controlled defect injection.](book/figures/part-04-data-quality.png)

### Python implementation

```python
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


raw = pd.DataFrame({
    "dpd": [0, -4, 35, 0], "balance": [1000, 800, -10, 500], "payment": [100, 90, 20, 900],
    "snapshot_date": pd.to_datetime(["2025-01-31", "2025-01-31", "2025-03-31", "2025-01-31"]),
    "as_of_date": pd.to_datetime(["2025-02-01"] * 4),
})
accepted, quarantine = clean_performance(raw)
print("Accepted rows:", accepted.index.tolist())
print(quarantine.to_string(index=False))
```

### Executed result

```output
Accepted rows: [0]
 row_id                                   rule
      1                           negative_dpd
      2                       negative_balance
      2 payment_exceeds_balance_plus_tolerance
      3 payment_exceeds_balance_plus_tolerance
      2                        future_snapshot
```

### Interpretation

Only row 0 passes all rules; the defect table records why other rows are excluded. Row reconciliation makes the effect of cleaning measurable.

**Validation:** Retain the raw value, record the rule and disposition, and reconcile row counts and balances after cleaning.

### Exercises

1. Repeat the calculation with **controlled defective copies of South German Credit and synthetic behavioural history** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

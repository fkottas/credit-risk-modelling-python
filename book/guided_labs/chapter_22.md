## Worked calculation — How are observation and performance windows constructed without leakage?

Features must exist by the reference date and outcomes must mature after it.

**Companion case:** `synthetic_behavioral_history`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
Y_i=\mathbf{1}\{T_i\le h\}
\]


![Figure 22.1 — Features are measured before the reference date and the 12-month outcome afterwards.](book/figures/observation-performance-windows.png)

### Python implementation

```python
import pandas as pd


def build_default_target(reference_dates, default_dates, horizon_months=12):
    reference = pd.to_datetime(reference_dates)
    default = pd.to_datetime(default_dates)
    horizon_end = reference + pd.offsets.DateOffset(months=horizon_months)
    observed = default.notna() & (default > reference) & (default <= horizon_end)
    return pd.DataFrame({"reference_date": reference, "horizon_end": horizon_end,
                         "default_date": default, "default_in_horizon": observed.astype(int)})


target = build_default_target(
    ["2024-01-31", "2024-01-31", "2024-01-31"],
    ["2024-08-15", "2025-05-01", None],
)
print(target.to_string(index=False))
```

### Executed result

```output
reference_date horizon_end default_date  default_in_horizon
    2024-01-31  2025-01-31   2024-08-15                   1
    2024-01-31  2025-01-31   2025-05-01                   0
    2024-01-31  2025-01-31          NaT                   0
```

### Interpretation

Only the default dated inside the stated 12-month performance window is labelled one. The later default is correctly excluded from that horizon.

**Validation:** Test every feature timestamp and exclude observations whose outcome window is incomplete.

### Exercises

1. Repeat the calculation with **synthetic behavioural history and the Taiwan credit-card payment history** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

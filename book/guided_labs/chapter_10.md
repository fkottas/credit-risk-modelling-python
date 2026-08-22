## Worked calculation — When does segmentation improve estimation rather than merely rename customers?

Segments are useful only when risk relationships or operational treatment differ sufficiently and sample sizes remain credible.

**Companion case:** `synthetic_retail`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
PD_s=\Pr(D=1\mid S=s)
\]


### Python implementation

```python
import pandas as pd


def assign_segment(row) -> str:
    if row["business_obligor"] and row["observed_defaults"] < 5:
        return "low_default_portfolio"
    if row["bureau_months"] < 12 or row["open_trades"] < 2:
        return "thin_file"
    if row["estimated_pd"] >= 0.12:
        return "subprime"
    return "prime"


borrowers = pd.DataFrame({
    "borrower": ["A", "B", "C", "D"], "estimated_pd": [0.02, 0.18, 0.07, 0.03],
    "bureau_months": [96, 72, 5, 60], "open_trades": [5, 4, 1, 3],
    "business_obligor": [False, False, False, True], "observed_defaults": [100, 100, 100, 2],
})
borrowers["segment"] = borrowers.apply(assign_segment, axis=1)
print(borrowers[["borrower", "segment"]].to_string(index=False))
```

### Executed result

```output
borrower               segment
       A                 prime
       B              subprime
       C             thin_file
       D low_default_portfolio
```

### Interpretation

The rules assign borrowers to mutually exclusive segments from explicit thresholds. The labels are descriptive policy outputs; they are not evidence that the segments have different default behaviour.

**Validation:** Compare event counts, calibration, and parameter stability within and across candidate segments.

### Exercises

1. Repeat the calculation with **South German Credit and Polish bankruptcy data** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

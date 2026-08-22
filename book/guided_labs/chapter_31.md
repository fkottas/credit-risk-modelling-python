## Worked calculation — Which sample design gives credible development and out-of-time evidence?

Random cross-validation can mix periods and policies, whereas future use requires evidence from later observations with mature outcomes.

**Companion case:** `synthetic_retail`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
\widehat{R}_{OOT}=\frac{1}{n_{OOT}}\sum_{i\in OOT}\ell(y_i,\widehat p_i)
\]


### Python implementation

```python
import pandas as pd


dates = pd.date_range("2022-01-31", periods=36, freq="ME")
sample = pd.DataFrame({"observation_date": dates})
sample["outcome_end"] = sample["observation_date"] + pd.DateOffset(months=12)
as_of = pd.Timestamp("2025-06-30")
sample["mature"] = sample["outcome_end"] <= as_of
sample["partition"] = pd.cut(
    sample["observation_date"],
    [pd.Timestamp("2021-12-31"), pd.Timestamp("2023-06-30"),
     pd.Timestamp("2024-06-30"), pd.Timestamp("2025-12-31")],
    labels=["development", "validation", "out_of_time"],
)
print(sample.groupby(["partition", "mature"], observed=False).size().unstack(fill_value=0))
```

### Executed result

```output
mature       False  True
partition
development      0     18
validation       0     12
out_of_time      6      0
```

### Interpretation

The partition table separates chronology and outcome maturity. Rows without a complete performance window cannot contribute to an out-of-time performance estimate.

**Validation:** Verify chronology, maturity, entity separation, and transformation fitting within the development partition.

### Exercises

1. Repeat the calculation with **synthetic retail dates and a no-date UCI benchmark** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

## Worked calculation — What evidence shows that an internal rating system is used consistently?

A rating system used only for reporting is not embedded in risk management and may not satisfy the intended use test.

**Companion case:** `synthetic_corporate_irb`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
\widehat{PD}_g=\frac{\sum_{i=1}^{n_g}w_iD_i}{\sum_{i=1}^{n_g}w_i}
\]


### Python implementation

```python
import pandas as pd


def grade_backtest(frame: pd.DataFrame) -> pd.DataFrame:
    grouped = frame.groupby("grade", observed=True)
    result = grouped.agg(observations=("default", "size"), predicted_pd=("pd", "mean"),
                         observed_rate=("default", "mean"), defaults=("default", "sum"))
    result["observed_to_expected"] = result["observed_rate"] / result["predicted_pd"]
    return result.reset_index()


portfolio = pd.DataFrame({
    "grade": ["A"] * 5 + ["B"] * 5, "pd": [0.02] * 5 + [0.10] * 5,
    "default": [0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
})
print(grade_backtest(portfolio).round(3).to_string(index=False))
```

### Executed result

```output
grade  observations  predicted_pd  observed_rate  defaults  observed_to_expected
    A             5          0.02            0.2         1                  10.0
    B             5          0.10            0.4         2                   4.0
```

### Interpretation

Observed rates exceed assigned PDs in the tiny grades, but each grade has only five observations. The example motivates uncertainty analysis rather than a conclusion of systematic miscalibration.

**Validation:** Compare assigned grades, observed outcomes, overrides, pricing, limits, and review actions by grade.

### Exercises

1. Repeat the calculation with **the synthetic corporate portfolio and EBA disclosure aggregates** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

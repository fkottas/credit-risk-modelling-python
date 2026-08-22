## Worked calculation — What should exploratory analysis establish before scorecard binning?

Volumes, missingness, event rates, timing, and segment behaviour determine whether a characteristic is interpretable and stable.

**Companion case:** `synthetic_retail`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
\widehat{p}_j=\frac{B_j}{G_j+B_j}
\]


![Figure 25.1 — Observed default rate across ordered bins of a candidate characteristic.](book/figures/part-05-characteristic.png)

### Python implementation

```python
import pandas as pd


data = pd.DataFrame({
    "utilisation": [0.10, 0.18, 0.25, 0.42, 0.55, 0.71, 0.83, 0.95],
    "default":     [0,    0,    0,    0,    1,    0,    1,    1],
})
data["bin"] = pd.cut(data["utilisation"], [0, 0.3, 0.6, 1.0], include_lowest=True)
table = data.groupby("bin", observed=False)["default"].agg(["count", "sum", "mean"])
table.columns = ["accounts", "defaults", "default_rate"]
print(table.to_string(float_format=lambda x: f"{x:.3f}"))
```

### Executed result

```output
accounts  defaults  default_rate
bin
(-0.001, 0.3]         3         0         0.000
(0.3, 0.6]            2         1         0.500
(0.6, 1.0]            3         2         0.667
```

### Interpretation

Default rates rise from 0% to 50% and 66.7% across the three illustrative utilisation bins. With only eight accounts, the pattern is a calculation check rather than stability evidence.

**Validation:** Reconcile counts and default rates from raw records to every displayed bin.

### Exercises

1. Repeat the calculation with **synthetic retail data and South German Credit** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

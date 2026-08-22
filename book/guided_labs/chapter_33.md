## Worked calculation — How are probabilities calibrated and converted into stable rating grades?

Ratings aggregate account probabilities for use in reporting and decisions, but grade design can hide poor within-grade calibration.

**Companion case:** `synthetic_retail`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
\Pr(Y=1\mid\widehat p=p)=p
\]


![Figure 33.1 — Observed default rate is compared with mean predicted PD by probability band.](book/figures/part-06-calibration.png)

### Python implementation

```python
import numpy as np
import pandas as pd


pd_hat = np.array([0.01, 0.02, 0.03, 0.05, 0.08, 0.12, 0.20, 0.30])
y = np.array([0, 0, 0, 0, 1, 0, 1, 1])
grades = pd.cut(pd_hat, [0, 0.03, 0.10, 1], labels=["A", "B", "C"], include_lowest=True)
review = pd.DataFrame({"grade": grades, "pd": pd_hat, "default": y}).groupby(
    "grade", observed=False
).agg(accounts=("default", "size"), predicted_pd=("pd", "mean"), observed_rate=("default", "mean"))
print(review.to_string(float_format=lambda x: f"{x:.4f}"))
```

### Executed result

```output
accounts  predicted_pd  observed_rate
grade
A             3        0.0200         0.0000
B             2        0.0650         0.5000
C             3        0.2067         0.6667
```

### Interpretation

The grade table compares mean assigned PD with observed default rate and population size. A zero observed rate in a three-account grade is not evidence of zero risk.

**Validation:** Compare predicted and observed rates by grade, time, and migration direction.

### Exercises

1. Repeat the calculation with **synthetic corporate data and Taiwan credit-card data** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

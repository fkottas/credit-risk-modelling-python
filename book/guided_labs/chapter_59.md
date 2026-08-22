## Worked calculation — How are calibrated risk estimates translated into cutoff, price, and profitability decisions?

The economically preferred threshold depends on margin, loss, cost, capital, take-up, and affordability—not AUC alone.

**Companion case:** `synthetic_retail`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
RAROC=\frac{Revenue-EL-Cost}{Economic\ Capital}
\]


![Figure 59.1 — Expected value changes with the PD approval threshold in the synthetic decision case.](book/figures/part-10-cutoff-economics.png)

### Python implementation

```python
import numpy as np


pd_hat = np.array([0.01, 0.03, 0.06, 0.10, 0.18])
ead = np.array([5000, 8000, 7000, 9000, 6000], dtype=float)
lgd, margin_rate, operating_cost = 0.45, 0.12, 120.0
for cutoff in (0.04, 0.08, 0.12):
    approve = pd_hat <= cutoff
    expected_profit = np.sum(approve * (ead * margin_rate - pd_hat * lgd * ead - operating_cost))
    print("cutoff", cutoff, "approved", int(approve.sum()), "expected profit", round(float(expected_profit), 2))
```

### Executed result

```output
cutoff 0.04 approved 2 expected profit 1189.5
cutoff 0.08 approved 3 expected profit 1720.5
cutoff 0.12 approved 4 expected profit 2275.5
```

### Interpretation

Expected profit rises across the three displayed cutoffs in this fixture and is highest at 0.12. The comparison is conditional on the margin, loss and applicant assumptions and ignores unobserved rejected outcomes.

**Validation:** Recalculate expected value under alternative cutoffs and stress each economic assumption.

### Exercises

1. Repeat the calculation with **the synthetic retail portfolio and a CC BY credit dataset** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

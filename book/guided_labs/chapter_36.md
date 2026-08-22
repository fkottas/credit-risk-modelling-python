## Worked calculation — What can be learned when outcomes are observed only for accepted applicants?

Acceptance creates selection bias because rejected applicants lack performance outcomes.

**Companion case:** `synthetic_retail`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
\mathbb{E}[Y\mid A=1,X]\ne\mathbb{E}[Y\mid X]
\]


### Python implementation

```python
import pandas as pd


applicants = pd.DataFrame({
    "income_band": [1, 1, 2, 2, 3, 3, 4, 4],
    "accepted":    [0, 1, 0, 1, 1, 1, 1, 1],
    "default":     [None, 1, None, 0, 0, 0, 0, 1],
})
observed = applicants.loc[applicants.accepted == 1]
print("accepted-sample default rate:", round(observed.default.mean(), 3))
print("outcomes unavailable for rejected applicants:", int(applicants.default.isna().sum()))
print("identified quantity: P(default | accepted, observed features)")
```

### Executed result

```output
accepted-sample default rate: 0.333
outcomes unavailable for rejected applicants: 2
identified quantity: P(default | accepted, observed features)
```

### Interpretation

The observed default rate of 0.333 applies only to accepted applicants. Two rejected applicants have no outcome, so population default risk is not identified from this table alone.

**Validation:** State which conditional quantity is identified and report sensitivity to explicit reject assumptions.

### Exercises

1. Repeat the calculation with **Credit Approval data and a synthetic accepted/rejected population** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

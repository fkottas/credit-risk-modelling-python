## Worked calculation — How do consumer, discrimination, privacy, and AI rules affect model design?

Predictive accuracy does not establish lawful use or sufficient reasons for an adverse action.

**Companion case:** `synthetic_retail`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
\Delta_g=\Pr(A=1\mid G=g)-\Pr(A=1)
\]


### Python implementation

```python
import pandas as pd


def group_decision_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for group, part in frame.groupby("group", observed=True):
        rows.append({
            "group": group, "n": len(part), "approval_rate": part["approved"].mean(),
            "true_positive_rate": part.loc[part["creditworthy"] == 1, "approved"].mean(),
            "false_positive_rate": part.loc[part["creditworthy"] == 0, "approved"].mean(),
        })
    return pd.DataFrame(rows)


decisions = pd.DataFrame({
    "group": ["reference"] * 6 + ["comparison"] * 6,
    "creditworthy": [1, 1, 1, 0, 0, 0] * 2,
    "approved": [1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
})
metrics = group_decision_metrics(decisions)
print(metrics.round(3).to_string(index=False))
print("Approval-rate gap:", round(metrics.loc[0, "approval_rate"] - metrics.loc[1, "approval_rate"], 3))
```

### Executed result

```output
group  n  approval_rate  true_positive_rate  false_positive_rate
comparison  6          0.167               0.333                0.000
 reference  6          0.500               0.667                0.333
Approval-rate gap: -0.333
```

### Interpretation

Approval and classification rates differ between the two small groups. These are descriptive sample differences; they do not establish discrimination or its cause without design, uncertainty and legal analysis.

**Validation:** Trace each model input and decision reason to purpose, legal review, and customer-facing explanation.

### Exercises

1. Repeat the calculation with **HMDA decision data and a synthetic application portfolio** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

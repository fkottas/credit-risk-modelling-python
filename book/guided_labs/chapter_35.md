## Worked calculation — How should explanations and group outcomes be evaluated?

Local attribution describes a model computation; it does not establish causality, fairness, or a lawful adverse-action reason.

**Companion case:** `synthetic_retail`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
\phi_j=\sum_{S\subseteq F\setminus j}\frac{|S|!(M-|S|-1)!}{M!}[v(S\cup j)-v(S)]
\]


### Python implementation

```python
import pandas as pd


data = pd.DataFrame({
    "group": ["A", "A", "A", "A", "B", "B", "B", "B"],
    "default": [0, 0, 1, 1, 0, 1, 1, 1],
    "approved": [1, 1, 1, 0, 1, 1, 0, 0],
})
rows = []
for group, frame in data.groupby("group"):
    rows.append({
        "group": group,
        "approval_rate": frame["approved"].mean(),
        "tpr_nondefault": frame.loc[frame.default == 0, "approved"].mean(),
        "default_rate_approved": frame.loc[frame.approved == 1, "default"].mean(),
    })
print(pd.DataFrame(rows).to_string(index=False, float_format=lambda x: f"{x:.3f}"))
```

### Executed result

```output
group  approval_rate  tpr_nondefault  default_rate_approved
    A          0.750           1.000                  0.333
    B          0.500           1.000                  0.500
```

### Interpretation

The groups differ in approval and approved-account default rates in this fixture. Attribution to the model, policy or population requires separate counterfactual and legal analysis.

**Validation:** Test explanation stability, faithfulness, subgroup support, calibration, and decision outcomes separately.

### Exercises

1. Repeat the calculation with **synthetic retail data and HMDA decision data** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

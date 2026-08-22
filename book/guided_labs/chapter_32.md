## Worked calculation — What do discrimination metrics and decision costs measure?

AUC, KS, lift, and confusion costs answer different ranking and action questions.

**Companion case:** `synthetic_retail`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
AUC=\Pr(\widehat p_D>\widehat p_N),\quad KS=\max_c|F_D(c)-F_N(c)|
\]


### Python implementation

```python
import numpy as np


y = np.array([0, 0, 1, 0, 1, 1])
pd_hat = np.array([0.05, 0.10, 0.20, 0.30, 0.60, 0.80])
default_scores = pd_hat[y == 1]
nondefault_scores = pd_hat[y == 0]
auc = np.mean(default_scores[:, None] > nondefault_scores[None, :])
thresholds = np.unique(pd_hat)
ks = max(abs(np.mean(default_scores <= c) - np.mean(nondefault_scores <= c)) for c in thresholds)
cutoff = 0.25
approve = pd_hat < cutoff
false_approval_cost = 4500 * np.sum(approve & (y == 1))
false_decline_cost = 400 * np.sum((~approve) & (y == 0))
print({"AUC": round(float(auc), 4), "KS": round(float(ks), 4),
       "decision_cost": int(false_approval_cost + false_decline_cost)})
```

### Executed result

```output
{'AUC': 0.8889, 'KS': 0.6667, 'decision_cost': 4900}
```

### Interpretation

AUC 0.8889 and KS 0.6667 indicate strong ranking in the miniature sample, while the EUR 4,900 decision cost depends on the selected threshold and cost assumptions.

**Validation:** Recompute each metric from ordered predictions and show sensitivity to the decision threshold.

### Exercises

1. Repeat the calculation with **Taiwan credit-card data and South German Credit** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

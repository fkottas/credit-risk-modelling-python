## Worked calculation — Which monitoring evidence is available immediately and which requires mature outcomes?

Input and score drift are leading indicators; calibration and default performance are observed only after the outcome horizon matures.

**Companion case:** `synthetic_retail`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
PSI=\sum_{j=1}^{J}(a_j-e_j)\log(a_j/e_j)
\]


![Figure 64.1 — Input and score evidence are immediate; calibration and defaults require mature outcomes.](book/figures/part-11-monitoring-layers.png)

### Python implementation

```python
import numpy as np


expected = np.array([0.50, 0.30, 0.15, 0.05])
actual = np.array([0.40, 0.32, 0.20, 0.08])
epsilon = 1e-6
psi = np.sum((actual - expected) * np.log((actual + epsilon) / (expected + epsilon)))
monitor = {"input_PSI": round(float(psi), 4), "score_shift_available": True,
           "12m_calibration_available": False, "reason": "outcomes not yet mature"}
print(monitor)
```

### Executed result

```output
{'input_PSI': 0.0521, 'score_shift_available': True, '12m_calibration_available': False, 'reason': 'outcomes not yet mature'}
```

### Interpretation

Input drift is measurable immediately, but 12-month calibration is unavailable because outcomes have not matured. Reporting it early would undercount defaults by construction.

**Validation:** Report data, prediction, decision, outcome, calibration, and group metrics with their own denominators and dates.

### Exercises

1. Repeat the calculation with **synthetic time-shifted portfolios and mature outcome vintages** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

## Worked calculation — How do macroeconomic paths enter PD, LGD, EAD, and scenario weights?

Forward-looking ECL requires internally coherent parameter paths rather than independent multipliers.

**Companion case:** `synthetic_ifrs9_schedule`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
\sum_{s=1}^{S}w_s=1,\quad ECL=\sum_{s=1}^{S}w_sECL_s
\]


### Python implementation

```python
import numpy as np


unemployment = np.array([4.0, 5.0, 7.0])
gdp_growth = np.array([2.0, 1.0, -1.5])
logit_pd = -4.2 + 0.22 * unemployment - 0.18 * gdp_growth
pd_path = 1 / (1 + np.exp(-logit_pd))
weights = np.array([0.20, 0.55, 0.25])
print("scenario PDs:", np.round(pd_path, 5))
print("probability-weighted PD:", round(float(weights @ pd_path), 5))
```

### Executed result

```output
scenario PDs: [0.0246  0.03626 0.08394]
probability-weighted PD: 0.04585
```

### Interpretation

The three scenario PDs are 2.46%, 3.626% and 8.394%; their probability-weighted value is 4.585%. The ordering reflects the stated macroeconomic coefficients, not an accounting judgement about weights.

**Validation:** Test coefficient signs, scenario ordering, weights, forecast vintage, and nonlinear weighting effects.

### Exercises

1. Repeat the calculation with **World Bank, Eurostat, ECB, or FRED series and the synthetic ECL schedule** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

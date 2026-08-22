## Worked calculation — How are LGD, EAD, ECL, and stress models validated in their natural units?

Percentage accuracy can hide monetary concentration and component errors can offset in aggregate ECL.

**Companion case:** `synthetic_recovery`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
e_i=actual_i-predicted_i
\]


### Python implementation

```python
import numpy as np


actual = np.array([0.20, 0.35, 0.70, 0.50])
predicted = np.array([0.25, 0.30, 0.60, 0.55])
exposure = np.array([100, 400, 50, 200]) * 1000
error = actual - predicted
account_bias = error.mean()
exposure_weighted_bias = np.average(error, weights=exposure)
currency_error = np.sum(error * exposure)
print({"account_bias": round(float(account_bias), 4),
       "exposure_weighted_bias": round(float(exposure_weighted_bias), 4),
       "currency_error": round(float(currency_error), 2)})
```

### Executed result

```output
{'account_bias': 0.0125, 'exposure_weighted_bias': 0.0133, 'currency_error': 10000.0}
```

### Interpretation

Account-weighted bias is 1.25 percentage points, exposure-weighted bias 1.33 points and the monetary error EUR 10,000. The measures differ because large accounts receive different weight.

**Validation:** Validate account- and exposure-weighted bias, tails, segments, and reconciliation separately.

### Exercises

1. Repeat the calculation with **synthetic recovery, revolving, and IFRS 9 datasets** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

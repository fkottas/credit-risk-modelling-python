## Worked calculation — How are counterparty exposure, netting, collateral, and CVA connected?

Future exposure is market-dependent and legally valid netting determines which positive and negative values may offset.

**Companion case:** `synthetic_counterparty_profiles`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
CVA\approx(1-RR)\sum_{t=1}^{T}EE_t\,\Delta PD_t\,DF_t
\]


### Python implementation

```python
import numpy as np


months = np.array([6, 12, 18, 24])
expected_exposure = np.array([1.2, 1.0, 0.7, 0.3]) * 1_000_000
marginal_counterparty_pd = np.array([0.002, 0.003, 0.004, 0.005])
discount_factor = np.array([0.99, 0.98, 0.97, 0.96])
recovery_rate = 0.40
cva_terms = (1 - recovery_rate) * expected_exposure * marginal_counterparty_pd * discount_factor
print("CVA by period:", np.round(cva_terms, 2))
print("Approximate unilateral CVA:", round(float(cva_terms.sum()), 2))
```

### Executed result

```output
CVA by period: [1425.6 1764.  1629.6  864. ]
Approximate unilateral CVA: 5683.2
```

### Interpretation

Period CVA contributions sum to EUR 5,683.20. The result is conditional on the supplied expected exposures, marginal PDs, recovery and independence approximation.

**Validation:** Reconcile trade, netting-set, collateral, expected-exposure, marginal-PD, and CVA totals.

### Exercises

1. Repeat the calculation with **synthetic counterparty profiles and Basel SA-CCR reference cases** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

## Worked calculation — How are conditional hazards converted into marginal and cumulative PD?

Period ECL requires first-default probability in each period rather than repeated cumulative probability.

**Companion case:** `synthetic_ifrs9_schedule`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
CumPD_t=1-\prod_{k=1}^{t}(1-h_k)
\]


![Figure 38.1 — Conditional hazard generates marginal first-default probabilities and cumulative PD.](book/figures/hazard-marginal-cumulative-pd.png)

### Python implementation

```python
import numpy as np
import pandas as pd


hazard = np.array([0.02, 0.03, 0.04, 0.05])
survival_start = np.r_[1.0, np.cumprod(1.0 - hazard[:-1])]
marginal_pd = survival_start * hazard
cumulative_pd = np.cumsum(marginal_pd)
result = pd.DataFrame({"month": range(1, 5), "hazard": hazard,
                       "marginal_pd": marginal_pd, "cumulative_pd": cumulative_pd})
print(result.to_string(index=False, float_format=lambda x: f"{x:.5f}"))
print("reconciliation:", round(float(cumulative_pd[-1]), 5),
      round(float(1 - np.prod(1 - hazard)), 5))
```

### Executed result

```output
month  hazard  marginal_pd  cumulative_pd
     1 0.02000      0.02000        0.02000
     2 0.03000      0.02940        0.04940
     3 0.04000      0.03802        0.08742
     4 0.05000      0.04563        0.13305
reconciliation: 0.13305 0.13305
```

### Interpretation

Marginal PD equals surviving probability times current hazard. The cumulative curve grows without summing hazards directly, so first-default probability is not counted twice.

**Validation:** Confirm that cumulative PD equals one minus the product of period survival probabilities.

### Exercises

1. Repeat the calculation with **the synthetic IFRS 9 schedule and rating-transition simulations** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

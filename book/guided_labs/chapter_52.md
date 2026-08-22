## Worked calculation — How are downturn LGD, CCF, floors, and defaulted-asset treatments applied?

Regulatory parameters have a different purpose from point-in-time accounting estimates.

**Companion case:** `synthetic_corporate_irb`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
\theta_{final}=\max(\theta_{raw}+MoC+Downturn,Floor)
\]


### Python implementation

```python
import numpy as np


raw_lgd = np.array([0.18, 0.30, 0.55])
downturn_addon = np.array([0.05, 0.08, 0.10])
moc = np.array([0.02, 0.02, 0.03])
floor = 0.25
final_lgd = np.maximum(raw_lgd + downturn_addon + moc, floor)
raw_ccf = np.array([0.25, 0.55, 0.90])
ccf_floor = 0.50
final_ccf = np.maximum(raw_ccf, ccf_floor)
print("final LGD:", np.round(final_lgd, 3))
print("final CCF:", np.round(final_ccf, 3))
```

### Executed result

```output
final LGD: [0.25 0.4  0.68]
final CCF: [0.5  0.55 0.9 ]
```

### Interpretation

The final LGD and CCF arrays show the effect of adjustment and floors on each raw parameter. A reviewer must reconcile each step rather than validate only the final value.

**Validation:** Show raw estimate, downturn adjustment, MoC, floor, and final parameter as separate columns.

### Exercises

1. Repeat the calculation with **synthetic recovery and revolving datasets** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

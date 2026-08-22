## Worked calculation — How are grade PDs aligned with long-run average default experience?

Raw estimates can be cyclically or compositionally biased and require approved calibration and conservatism.

**Companion case:** `synthetic_corporate_irb`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
\sum_{g=1}^{G}w_g\widehat{PD}_g=LRA
\]


### Python implementation

```python
import numpy as np


grade_weight = np.array([0.50, 0.30, 0.20])
raw_pd = np.array([0.010, 0.025, 0.070])
long_run_average = 0.035
scale = long_run_average / float(grade_weight @ raw_pd)
calibrated = np.minimum(raw_pd * scale, 1.0)
moc = np.array([0.001, 0.002, 0.004])
final_pd = np.minimum(calibrated + moc, 1.0)
print("calibrated weighted PD:", round(float(grade_weight @ calibrated), 6))
print("final grade PDs after MoC:", np.round(final_pd, 6))
```

### Executed result

```output
calibrated weighted PD: 0.035
final grade PDs after MoC: [0.014208 0.035019 0.096453]
```

### Interpretation

The calibrated grade PDs reproduce the 3.5% weighted target before named margins of conservatism are added. The final figures therefore retain both calibration and conservatism effects.

**Validation:** Reconcile exposure-weighted calibrated PD to the stated target before adding MoC.

### Exercises

1. Repeat the calculation with **synthetic corporate grades and EBA disclosure aggregates** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

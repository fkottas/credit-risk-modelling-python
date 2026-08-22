## Worked calculation — When are provision matrices or CECL methods appropriate, and how are overlays separated?

Method choice follows data and portfolio behaviour; management adjustments address specified gaps outside the base estimate.

**Companion case:** `synthetic_ifrs9_schedule`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
LossRate_b=\frac{historical\ credit\ losses_b}{exposure_b}
\]


### Python implementation

```python
import pandas as pd


matrix = pd.DataFrame({
    "age_band": ["current", "1-30", "31-60", "61-90"],
    "exposure": [800000, 120000, 50000, 30000],
    "historical_loss_rate": [0.005, 0.025, 0.12, 0.35],
    "forward_factor": [1.10, 1.15, 1.20, 1.25],
})
matrix["adjusted_loss_rate"] = matrix.historical_loss_rate * matrix.forward_factor
matrix["model_ecl"] = matrix.exposure * matrix.adjusted_loss_rate
overlay = 15000.0
print(matrix.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print("Model ECL:", round(matrix.model_ecl.sum(), 2), "Overlay:", overlay,
      "Reported allowance:", round(matrix.model_ecl.sum() + overlay, 2))
```

### Executed result

```output
age_band  exposure  historical_loss_rate  forward_factor  adjusted_loss_rate  model_ecl
 current    800000                 0.005           1.100               0.006   4400.000
    1-30    120000                 0.025           1.150               0.029   3450.000
   31-60     50000                 0.120           1.200               0.144   7200.000
   61-90     30000                 0.350           1.250               0.438  13125.000
Model ECL: 28175.0 Overlay: 15000.0 Reported allowance: 43175.0
```

### Interpretation

Each provision-matrix amount reconciles exposure, historical loss rate, forward factor and adjusted loss rate. The calculation makes the forward adjustment observable instead of embedding it in the history.

**Validation:** Reconcile historical rates, forward adjustments, model ECL, overlay, and final allowance.

### Exercises

1. Repeat the calculation with **a synthetic trade-receivables matrix and a synthetic CECL loan schedule** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

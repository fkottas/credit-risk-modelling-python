## Worked calculation — Which statistical formulation matches the credit question?

Classification, regression, survival, and multi-state models estimate different quantities and cannot be exchanged by changing an algorithm name.

**Companion case:** `synthetic_retail`. **Implementation level:** From first principles: scalar values, lists, and the Python standard library; intermediate quantities remain visible.

### Method

The calculation follows

\[
\widehat{f}=\arg\min_f\sum_{i=1}^{n}\ell(y_i,f(x_i))+\lambda\Omega(f)
\]


### Python implementation

```python
from math import exp


def sigmoid(value):
    return 1.0 / (1.0 + exp(-value))


def cumulative_pd(hazards):
    survival = 1.0
    result = []
    for hazard in hazards:
        if not 0.0 <= hazard <= 1.0:
            raise ValueError("Each hazard must lie between zero and one")
        survival *= 1.0 - hazard
        result.append(1.0 - survival)
    return result


classification_pd = [round(sigmoid(value), 4) for value in (-2.0, -0.5, 1.0)]
regression_lgd = [0.18, 0.42, 0.77]
lifetime_pd = [round(value, 4) for value in cumulative_pd([0.02, 0.03, 0.05, 0.08])]
print("Classification PD:", classification_pd)
print("Regression LGD:", regression_lgd)
print("Cumulative lifetime PD:", lifetime_pd)
```

### Executed result

```output
Classification PD: [0.1192, 0.3775, 0.7311]
Regression LGD: [0.18, 0.42, 0.77]
Cumulative lifetime PD: [0.02, 0.0494, 0.0969, 0.1692]
```

### Interpretation

The three outputs have different meanings: account default probability, conditional loss severity and cumulative time-to-default probability. Similar numeric ranges do not make them interchangeable targets.

**Validation:** State the unit, event, horizon, censoring rule, and output domain for each formulation.

### Exercises

1. Repeat the calculation with **the Taiwan credit-card data and a synthetic recovery dataset** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

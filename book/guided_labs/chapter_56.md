## Worked calculation — How are assigned PDs backtested without reducing validation to one test?

Calibration, discrimination, stability, and benchmark performance are distinct properties.

**Companion case:** `synthetic_retail`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
Brier=\frac1n\sum_{i=1}^{n}(y_i-\widehat p_i)^2
\]


### Python implementation

```python
from scipy.stats import binomtest


grades = [("A", 500, 4, 0.010), ("B", 300, 12, 0.035), ("C", 120, 14, 0.090)]
for grade, n, defaults, assigned_pd in grades:
    observed = defaults / n
    test = binomtest(defaults, n, assigned_pd)
    print(grade, "observed", round(observed, 4), "assigned", assigned_pd,
          "two-sided p-value", round(test.pvalue, 4))
```

### Executed result

```output
A observed 0.008 assigned 0.01 two-sided p-value 0.8236
B observed 0.04 assigned 0.035 two-sided p-value 0.6351
C observed 0.1167 assigned 0.09 two-sided p-value 0.3354
```

### Interpretation

None of the grade tests rejects its assigned PD in this small sample, but the large p-values also reflect limited power. Non-rejection is not proof of correct calibration.

**Validation:** Report sample size, defaults, uncertainty interval, test assumptions, and economic materiality by grade and time.

### Exercises

1. Repeat the calculation with **synthetic corporate grades and Taiwan credit-card data** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

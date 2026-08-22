## Worked calculation — How do tree ensembles capture nonlinear credit relationships?

Trees partition the feature space by impurity reduction; ensembles reduce variance or sequentially correct errors.

**Companion case:** `synthetic_retail`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
F_M(x)=\sum_{m=1}^{M}\eta_m h_m(x)
\]


### Python implementation

```python
def gini(good, bad):
    total = good + bad
    if total == 0:
        return 0.0
    p_good, p_bad = good / total, bad / total
    return 1.0 - p_good ** 2 - p_bad ** 2


def weighted_child_gini(left, right):
    n_left, n_right = sum(left), sum(right)
    return (n_left * gini(*left) + n_right * gini(*right)) / (n_left + n_right)


parent = (6, 4)
for threshold, left, right in [(5, (5, 0), (1, 4)), (6, (6, 0), (0, 4))]:
    gain = gini(*parent) - weighted_child_gini(left, right)
    print("threshold", threshold, "weighted Gini", round(weighted_child_gini(left, right), 3),
          "gain", round(gain, 3))
```

### Executed result

```output
threshold 5 weighted Gini 0.16 gain 0.32
threshold 6 weighted Gini 0.0 gain 0.48
```

### Interpretation

Threshold 6 produces pure child nodes and the largest displayed Gini gain of 0.48. A single pure split can still overfit and must be tested on later data.

**Validation:** Recalculate candidate split gain and compare out-of-time calibration as well as AUC.

### Exercises

1. Repeat the calculation with **Taiwan credit-card data and Polish bankruptcy data** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

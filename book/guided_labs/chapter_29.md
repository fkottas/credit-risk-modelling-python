## Worked calculation — How does penalised logistic regression estimate scorecard coefficients?

The likelihood connects WOE inputs to probability, while the penalty controls unstable coefficients under sparse or correlated data.

**Companion case:** `synthetic_retail`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
\beta^{(k+1)}=\beta^{(k)}+\left(\frac{X^\top W^{(k)}X}{n}+\Lambda\right)^{-1}\left[\frac{X^\top(y-p^{(k)})}{n}-\Lambda\beta^{(k)}\right]
\]


![Figure 29.1 — The penalised negative log-likelihood decreases over the displayed IRLS iterations.](book/figures/irls-objective-convergence.png)

### Python implementation

```python
import numpy as np


def sigmoid(z):
    return np.where(z >= 0, 1 / (1 + np.exp(-z)), np.exp(z) / (1 + np.exp(z)))


def irls(X, y, l2=0.1, iterations=4):
    X = np.column_stack([np.ones(len(X)), np.asarray(X, dtype=float)])
    y = np.asarray(y, dtype=float)
    beta = np.zeros(X.shape[1])
    penalty = np.diag([0.0] + [l2] * (X.shape[1] - 1))
    for step in range(iterations):
        probability = sigmoid(X @ beta)
        weight = np.clip(probability * (1 - probability), 1e-9, 0.25)
        gradient = -(X.T @ (y - probability)) / len(y) + penalty @ beta
        hessian = (X.T * weight) @ X / len(y) + penalty
        delta = np.linalg.solve(hessian, gradient)
        beta -= delta
        print(step + 1, np.round(beta, 6), "max step", round(abs(delta).max(), 6))
    return beta


irls([[-1.0], [1.0]], [0, 1], iterations=1)
```

### Executed result

```output
1 [0.       1.428571] max step 1.428571
```

### Interpretation

The first ridge-penalised IRLS step leaves the symmetric intercept at zero and moves the slope to 1.428571. Subsequent iterations, convergence and objective reduction still require testing.

**Validation:** Track the objective, gradient, coefficient step, and probability bounds at every IRLS iteration.

### Exercises

1. Repeat the calculation with **synthetic retail data and South German Credit** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

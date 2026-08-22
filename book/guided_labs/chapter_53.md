## Worked calculation — How do systematic dependence and concentration affect portfolio tail loss?

Expected loss may remain similar while a common factor or large exposure raises extreme outcomes.

**Companion case:** `synthetic_corporate_irb`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
L_q=LGD\,N\left(\frac{G(PD)+\sqrt{R}\,G(q)}{\sqrt{1-R}}\right)
\]


### Python implementation

```python
import numpy as np
from scipy.stats import norm


rng = np.random.default_rng(53)
n_obligors, simulations = 1000, 5000
pd, lgd, correlation = 0.02, 0.45, 0.12
systematic = rng.normal(size=simulations)
conditional_pd = norm.cdf((norm.ppf(pd) - np.sqrt(correlation) * systematic) /
                          np.sqrt(1 - correlation))
defaults = rng.binomial(n_obligors, conditional_pd)
loss_rate = defaults / n_obligors * lgd
print({"mean_loss": round(float(loss_rate.mean()), 5),
       "loss_99_9": round(float(np.quantile(loss_rate, 0.999)), 5),
       "unexpected_loss_99_9": round(float(np.quantile(loss_rate, 0.999) - loss_rate.mean()), 5)})
```

### Executed result

```output
{'mean_loss': 0.00901, 'loss_99_9': 0.0612, 'unexpected_loss_99_9': 0.05219}
```

### Interpretation

Mean simulated loss is about 0.9%, whereas the 99.9th percentile is 6.12%. Dependence and finite-portfolio concentration affect tail loss far more than the mean.

**Validation:** Compare mean, tail quantile, expected shortfall, HHI, and largest-obligor contribution.

### Exercises

1. Repeat the calculation with **the synthetic corporate portfolio under granular and concentrated weights** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

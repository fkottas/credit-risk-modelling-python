## Worked calculation — How should PD be estimated when very few defaults are observed?

Sparse events create wide uncertainty; zero observed defaults do not imply zero underlying PD.

**Companion case:** `synthetic_corporate_irb`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
PD\mid D\sim Beta(a+D,b+n-D)
\]


### Python implementation

```python
from scipy.stats import beta


defaults, observations = 1, 80
prior_a, prior_b = 1.0, 19.0
posterior_a = prior_a + defaults
posterior_b = prior_b + observations - defaults
mean = posterior_a / (posterior_a + posterior_b)
lower, upper = beta.ppf([0.025, 0.975], posterior_a, posterior_b)
print({"observed_rate": defaults / observations, "posterior_mean": round(mean, 5),
       "credible_interval_95": (round(float(lower), 5), round(float(upper), 5))})
```

### Executed result

```output
{'observed_rate': 0.0125, 'posterior_mean': 0.02, 'credible_interval_95': (0.00246, 0.055)}
```

### Interpretation

Five defaults in 400 observations give a 1.25% raw rate; the stated prior moves the posterior mean to 2.0% and leaves a wide credible interval. Prior sensitivity is therefore material.

**Validation:** Report posterior sensitivity to prior choice and compare credible intervals with frequentist bounds.

### Exercises

1. Repeat the calculation with **Polish bankruptcy data and a synthetic low-default portfolio** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

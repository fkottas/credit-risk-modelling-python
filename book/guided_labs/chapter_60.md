## Worked calculation — How can sequential methods be studied without experimenting on real borrowers?

Credit limits and collections create delayed, censored feedback and customer consequences.

**Companion case:** `synthetic_revolving`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
Q(s,a)=r(s,a)+\gamma\max_{a'}Q(s',a')
\]


### Python implementation

```python
import numpy as np


rng = np.random.default_rng(60)
true_rewards = np.array([8.0, 11.0, 9.0])
counts = np.zeros(3, dtype=int)
estimates = np.zeros(3)
epsilon = 0.10
for _ in range(500):
    action = int(rng.integers(3)) if rng.random() < epsilon else int(np.argmax(estimates))
    reward = rng.normal(true_rewards[action], 4.0)
    counts[action] += 1
    estimates[action] += (reward - estimates[action]) / counts[action]
print("action counts:", counts.tolist())
print("estimated rewards:", np.round(estimates, 2).tolist())
print("simulation only: no customer limit is changed")
```

### Executed result

```output
action counts: [30, 448, 22]
estimated rewards: [9.16, 10.66, 7.67]
simulation only: no customer limit is changed
```

### Interpretation

The middle action is selected most often and has the highest estimated reward in the simulation. The output explicitly remains a simulation and does not authorise a customer limit change.

**Validation:** Use simulation or historical policy evaluation, enforce action constraints, and report off-policy uncertainty.

### Exercises

1. Repeat the calculation with **the synthetic revolving and synthetic collections datasets** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

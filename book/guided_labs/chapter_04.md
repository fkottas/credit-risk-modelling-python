## Worked calculation — How should credit events be represented through time?

Cohort age, calendar conditions, censoring, and competing exits change the denominator of every rate.

**Companion case:** `synthetic_behavioral_history`. **Implementation level:** From first principles: scalar values, lists, and the Python standard library; intermediate quantities remain visible.

### Method

The calculation follows

\[
P_{ij}(h)=\Pr(S_{t+h}=j\mid S_t=i)
\]


### Python implementation

```python
from collections import Counter, defaultdict

histories = {
    "A": ["current", "current", "30_dpd", "60_dpd"],
    "B": ["current", "30_dpd", "current", "current"],
    "C": ["current", "current", "prepaid", "prepaid"],
}
transition_counts = defaultdict(Counter)

for states in histories.values():
    for current_state, next_state in zip(states, states[1:], strict=False):
        transition_counts[current_state][next_state] += 1

for current_state, counts in transition_counts.items():
    row_total = sum(counts.values())
    probabilities = {
        next_state: round(count / row_total, 3)
        for next_state, count in sorted(counts.items())
    }
    print(current_state, probabilities, "row sum=", round(sum(probabilities.values()), 3))
```

### Executed result

```output
current {'30_dpd': 0.333, 'current': 0.5, 'prepaid': 0.167} row sum= 1.0
30_dpd {'60_dpd': 0.5, 'current': 0.5} row sum= 1.0
prepaid {'prepaid': 1.0} row sum= 1.0
```

### Interpretation

Every displayed transition row sums to one. The absorbing prepaid state remains prepaid, while delinquent accounts can cure or worsen under the stated transition rules.

**Validation:** Reconcile the risk set and confirm that each transition row sums to one.

### Exercises

1. Repeat the calculation with **the synthetic behavioural history and synthetic IFRS 9 schedule** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

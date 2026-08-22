## Worked calculation — How do mean loss and tail loss differ?

Expected loss supports central-tendency decisions, whereas solvency and concentration questions depend on the loss distribution.

**Companion case:** `synthetic_corporate_irb`. **Implementation level:** From first principles: scalar values, lists, and the Python standard library; intermediate quantities remain visible.

### Method

The calculation follows

\[
EL=\mathbb{E}[L],\quad UL_\alpha=Q_\alpha(L)-EL
\]


![Figure 2.1 — Realised loss is right-skewed; the mean does not describe the upper tail.](book/figures/part-01-loss-distribution.png)

### Python implementation

```python
from itertools import product

pd = [0.10, 0.20]
loss_if_default = [500.0, 800.0]  # LGD times EAD
distribution = []

for defaults in product((0, 1), repeat=2):
    probability = 1.0
    loss = 0.0
    for default, probability_of_default, amount in zip(
        defaults, pd, loss_if_default, strict=True
    ):
        probability *= probability_of_default if default else 1.0 - probability_of_default
        loss += default * amount
    distribution.append((loss, probability, defaults))

expected_loss = sum(loss * probability for loss, probability, _ in distribution)
cumulative_probability = 0.0
loss_quantile_95 = None
for loss, probability, defaults in sorted(distribution):
    cumulative_probability += probability
    print(defaults, "loss=", loss, "probability=", round(probability, 3))
    if loss_quantile_95 is None and cumulative_probability >= 0.95:
        loss_quantile_95 = loss

print("Expected loss:", expected_loss)
print("95% loss quantile:", loss_quantile_95)
print("Unexpected loss at 95%:", loss_quantile_95 - expected_loss)
```

### Executed result

```output
(0, 0) loss= 0.0 probability= 0.72
(1, 0) loss= 500.0 probability= 0.08
(0, 1) loss= 800.0 probability= 0.18
(1, 1) loss= 1300.0 probability= 0.02
Expected loss: 210.00000000000003
95% loss quantile: 800.0
Unexpected loss at 95%: 590.0
```

### Interpretation

The zero-loss state is the most likely individual outcome, while low-probability default states create the upper tail. This is why the mean alone does not describe portfolio loss severity.

**Validation:** Verify that state probabilities sum to one and that their probability-weighted losses reproduce expected loss.

### Exercises

1. Repeat the calculation with **the exact two-account case and the synthetic corporate portfolio** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

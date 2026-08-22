## Worked calculation — How is an unpaid contractual cash flow converted into present-value loss?

Loss depends on amount, timing, recoveries, and workout costs; a default flag alone cannot measure it.

**Companion case:** `synthetic_recovery`. **Implementation level:** From first principles: scalar values, lists, and the Python standard library; intermediate quantities remain visible.

### Method

The calculation follows

\[
L=\sum_{t=1}^{T}(1+r)^{-t/12}\left[(C_t-P_t)-Rec_t+K_t\right]
\]


![Figure 1.1 — Contractual amounts, receipts, recoveries, and discounted shortfalls in the worked example.](book/figures/cash-flow-loss-decomposition.png)

### Python implementation

```python
schedule = [
    # month, contractual, received, recovery, workout cost
    (1, 350.0, 350.0, 0.0, 0.0),
    (2, 350.0, 200.0, 0.0, 5.0),
    (3, 350.0, 0.0, 120.0, 15.0),
]
eir = 0.12
total_pv_loss = 0.0

print("month  shortfall  discount  pv_loss")
for month, contractual, received, recovery, cost in schedule:
    shortfall = contractual - received - recovery + cost
    discount = (1.0 + eir) ** (-month / 12.0)
    pv_loss = shortfall * discount
    total_pv_loss += pv_loss
    print(f"{month:>5}  {shortfall:>9.2f}  {discount:>8.4f}  {pv_loss:>7.2f}")

print("Total PV loss:", round(total_pv_loss, 2))
```

### Executed result

```output
month  shortfall  discount  pv_loss
    1       0.00    0.9906     0.00
    2     155.00    0.9813   152.10
    3     245.00    0.9721   238.16
Total PV loss: 390.26
```

### Interpretation

The present-value loss is EUR 390.26. Month 1 contributes zero because the contractual payment was received; months 2 and 3 contribute positive shortfalls after recoveries and costs.

**Validation:** Recalculate every discounted period and test the signs of recoveries and costs.

### Exercises

1. Repeat the calculation with **the miniature cash-flow schedule and the synthetic retail portfolio** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

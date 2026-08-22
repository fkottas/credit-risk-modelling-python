## Worked calculation — How is workout LGD reconstructed from post-default cash flows?

Recovery amount, timing, workout costs, cure, and incomplete resolution all affect economic loss.

**Companion case:** `synthetic_recovery`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
LGD=1-\frac{\sum_{t=1}^{T} CF_t(1+EIR)^{-u_t}}{EAD_0}
\]


### Python implementation

```python
cashflows = [
    # months after default, recovery, direct workout cost
    (3, 1500.0, 100.0),
    (9, 800.0, 150.0),
    (15, 400.0, 200.0),
]
ead_at_default, eir = 5000.0, 0.10
pv_net_recovery = sum((recovery - cost) * (1 + eir) ** (-month / 12)
                      for month, recovery, cost in cashflows)
lgd = 1 - pv_net_recovery / ead_at_default
print("PV net recovery:", round(pv_net_recovery, 2))
print("Workout LGD:", round(lgd, 4))
```

### Executed result

```output
PV net recovery: 2149.73
Workout LGD: 0.5701
```

### Interpretation

Discounted net recoveries of EUR 2,149.73 against EUR 5,000 EAD produce workout LGD of 0.5701. Later recovery timing would reduce present value and increase LGD.

**Validation:** Independently rebuild one account and reconcile discounted cash flows to account and portfolio totals.

### Exercises

1. Repeat the calculation with **the synthetic recovery dataset and student-supplied lawful recovery data** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

## Worked calculation — How do contractual timing, EIR discounting, and prepayment affect cash shortfalls?

The same undiscounted shortfall has a different present value when its timing changes, and prepayment changes the exposure path.

**Companion case:** `synthetic_ifrs9_schedule`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
DF_t=(1+EIR)^{-t/12}
\]


### Python implementation

```python
contractual = [1000.0, 1000.0, 1000.0]
expected = [1000.0, 700.0, 0.0]
eir = 0.12
shortfalls = []
for month, (contract, receipt) in enumerate(zip(contractual, expected), start=1):
    discount = (1 + eir) ** (-month / 12)
    shortfalls.append((contract - receipt) * discount)
    print(month, "discount", round(discount, 6), "PV shortfall", round(shortfalls[-1], 2))
print("Cash-flow ECL:", round(sum(shortfalls), 2))
```

### Executed result

```output
1 discount 0.9906 PV shortfall 0.0
2 discount 0.981289 PV shortfall 294.39
3 discount 0.972065 PV shortfall 972.07
Cash-flow ECL: 1266.45
```

### Interpretation

Later shortfalls receive smaller discount factors under the 12% annual effective rate. The month-3 EUR 1,000 shortfall has present value EUR 972.07, confirming the year-fraction convention.

**Validation:** Reconcile contractual and expected cash flows period by period and test day-count conventions.

### Exercises

1. Repeat the calculation with **the synthetic IFRS 9 schedule and a synthetic revolving schedule** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

## Worked calculation — How are stress effects and ECL movements reconciled and explained?

A scenario result is credible only when scope, drivers, and accounting movements reconcile.

**Companion case:** `synthetic_ifrs9_schedule`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
A_{close}=A_{open}+\sum_k\Delta A_k-WriteOffs
\]


### Python implementation

```python
opening_allowance = 720000.0
movements = {"new_business": 85000.0, "repayments": -62000.0, "stage_change": 110000.0,
             "scenario_change": 45000.0, "write_off": -30000.0, "overlay_change": 12000.0}
closing = opening_allowance + sum(movements.values())
posted_ledger_balance = 880000.0
print("calculated closing allowance:", closing)
print("posted ledger balance:", posted_ledger_balance)
print("unreconciled difference:", posted_ledger_balance - closing)
```

### Executed result

```output
calculated closing allowance: 880000.0
posted ledger balance: 880000.0
unreconciled difference: 0.0
```

### Interpretation

The movement components produce a closing allowance of EUR 880,000, exactly equal to the posted balance in the fixture. Zero difference proves arithmetic reconciliation only.

**Validation:** Attribute changes to volume, stage, parameters, scenario, write-off, and overlay under a stated ordering.

### Exercises

1. Repeat the calculation with **the synthetic IFRS 9 schedule and Federal Reserve stress paths** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

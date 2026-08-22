## Worked calculation — Which risks are distinct in BNPL and embedded credit?

Credit loss, affordability, fraud, merchant disputes, and repeat use have different outcomes and controls.

**Companion case:** `synthetic_retail`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
EL_i=PD_i\,LGD_i\,EAD_i
\]


### Python implementation

```python
import pandas as pd


def bnpl_schedule(purchase: float, instalments: int, monthly_income: float) -> pd.DataFrame:
    if purchase <= 0 or instalments < 2 or monthly_income <= 0:
        raise ValueError("Positive purchase, income, and at least two instalments are required")
    payment = purchase / instalments
    burden = payment / monthly_income
    return pd.DataFrame({"instalment": range(1, instalments + 1), "payment": payment,
                         "payment_to_income": burden})


schedule = bnpl_schedule(480.0, 4, 2_000.0)
print(schedule.round(3).to_string(index=False))
print("Total payments:", schedule["payment"].sum(), "monthly burden:", schedule["payment_to_income"].iloc[0])
```

### Executed result

```output
instalment  payment  payment_to_income
          1    120.0               0.06
          2    120.0               0.06
          3    120.0               0.06
          4    120.0               0.06
Total payments: 480.0 monthly burden: 0.06
```

### Interpretation

Each instalment consumes 6% of monthly income in the simplified schedule. Repeated use must be aggregated because an individually small payment can still create a material total burden.

**Validation:** Keep each target and its denominator separate and inspect repeat-borrowing exposure.

### Exercises

1. Repeat the calculation with **the synthetic retail and synthetic fraud datasets** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

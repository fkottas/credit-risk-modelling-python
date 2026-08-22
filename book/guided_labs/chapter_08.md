## Worked calculation — How should obligor and facility risk be separated in SME and corporate lending?

Financial strength belongs primarily to the obligor, while collateral, seniority, and utilisation belong to facilities.

**Companion case:** `synthetic_corporate_irb`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
PD_i=\Pr(D_i=1\mid x_i,\mathcal{I}_t)
\]


### Python implementation

```python
import pandas as pd


def corporate_ratios(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["debt_to_ebitda"] = out["debt"] / out["ebitda"].replace(0, pd.NA)
    out["interest_cover"] = out["ebit"] / out["interest_expense"].replace(0, pd.NA)
    out["dscr"] = out["cash_available_for_debt_service"] / out["debt_service"].replace(0, pd.NA)
    out["equity_ratio"] = out["equity"] / out["assets"].replace(0, pd.NA)
    return out


companies = pd.DataFrame({
    "company": ["StableCo", "GrowthCo", "StressedCo"], "debt": [200, 450, 600],
    "ebitda": [120, 90, 40], "ebit": [95, 55, 10], "interest_expense": [20, 30, 35],
    "cash_available_for_debt_service": [100, 70, 20], "debt_service": [55, 65, 70],
    "equity": [500, 250, 80], "assets": [900, 850, 780],
})
print(corporate_ratios(companies).round(2).to_string(index=False))
```

### Executed result

```output
company  debt  ebitda  ebit  interest_expense  cash_available_for_debt_service  debt_service  equity  assets  debt_to_ebitda  interest_cover  dscr  equity_ratio
  StableCo   200     120    95                20                              100            55     500     900            1.67            4.75  1.82          0.56
  GrowthCo   450      90    55                30                               70            65     250     850            5.00            1.83  1.08          0.29
StressedCo   600      40    10                35                               20            70      80     780           15.00            0.29  0.29          0.10
```

### Interpretation

The table computes obligor ratios from financial statements while retaining facility-level amounts separately. Changing a denominator changes the economic interpretation, not merely the displayed number.

**Validation:** Check consolidation perimeter, statement date, currency, and ratio denominators.

### Exercises

1. Repeat the calculation with **the synthetic corporate IRB and Polish bankruptcy datasets** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

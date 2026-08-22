## Worked calculation — How are marginal PD, LGD, EAD, discounting, and scenarios combined in an ECL engine?

Component definitions must share account, period, scenario, currency, and horizon before multiplication.

**Companion case:** `synthetic_ifrs9_schedule`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
ECL_{acct}=\sum_{s=1}^{S} w_s\sum_{t=1}^{T} MPD_{s,t}LGD_{s,t}EAD_{s,t}DF_t
\]


![Figure 43.1 — Scenario-specific ECL is calculated before applying scenario probabilities.](book/figures/part-08-scenario-ecl.png)

### Python implementation

```python
import pandas as pd


schedule = pd.DataFrame({
    "scenario": ["base", "base", "downside", "downside"],
    "weight": [0.7, 0.7, 0.3, 0.3],
    "month": [1, 2, 1, 2],
    "marginal_pd": [0.01, 0.015, 0.025, 0.035],
    "lgd": [0.40, 0.40, 0.50, 0.50],
    "ead": [10000, 9000, 10000, 9000],
    "discount_factor": [0.995, 0.990, 0.995, 0.990],
})
schedule["weighted_ecl"] = schedule.eval(
    "weight * marginal_pd * lgd * ead * discount_factor"
)
print(schedule.groupby("scenario")["weighted_ecl"].sum())
print("Total ECL:", round(schedule.weighted_ecl.sum(), 2))
```

### Executed result

```output
scenario
base        65.282
downside    84.090
Name: weighted_ecl, dtype: float64
Total ECL: 149.37
```

### Interpretation

The base scenario contributes EUR 65.282 and the downside EUR 84.090 after their weights, for total ECL of EUR 149.37. Weighting occurs after each scenario calculation.

**Validation:** Reconcile period, scenario, account, portfolio, and posted totals.

### Exercises

1. Repeat the calculation with **the synthetic IFRS 9 schedule and official macroeconomic series** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

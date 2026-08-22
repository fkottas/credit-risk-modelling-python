## Worked calculation — How does IFRS 9 change the loss horizon after significant credit deterioration?

Stage assignment determines whether twelve-month or lifetime ECL is measured.

**Companion case:** `synthetic_ifrs9_schedule`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
ECL=\sum_{s=1}^{S} w_s\sum_{t=1}^{T} MPD_{s,t}LGD_{s,t}EAD_{s,t}DF_t
\]


![Figure 16.1 — Account counts by IFRS 9 stage in the synthetic calculation case.](book/figures/part-03-stages.png)

### Python implementation

```python
import pandas as pd


def assign_ifrs9_stage(origination_pd, current_pd, dpd, watchlist, default):
    if default or dpd >= 90:
        return 3, "credit_impaired_or_default"
    pd_ratio = current_pd / origination_pd if origination_pd > 0 else float("inf")
    if dpd >= 30 or watchlist or pd_ratio >= 2.0:
        return 2, "significant_increase_in_credit_risk"
    return 1, "performing_without_sicr"


accounts = pd.DataFrame({
    "account": ["A", "B", "C"], "orig_pd": [0.02, 0.02, 0.03],
    "current_pd": [0.025, 0.055, 0.30], "dpd": [0, 35, 95],
    "watchlist": [False, False, True], "default": [False, False, True],
})
accounts[["stage", "reason"]] = accounts.apply(
    lambda r: pd.Series(assign_ifrs9_stage(r.orig_pd, r.current_pd, r.dpd, r.watchlist, r.default)), axis=1
)
print(accounts[["account", "stage", "reason"]].to_string(index=False))
```

### Executed result

```output
account  stage                              reason
      A      1             performing_without_sicr
      B      2 significant_increase_in_credit_risk
      C      3          credit_impaired_or_default
```

### Interpretation

The accounts enter Stages 1, 2 and 3 for distinct stated reasons. Stage assignment changes the measurement horizon; it is not a relabelling of the same ECL calculation.

**Validation:** Recalculate an account under Stage 1, Stage 2, and Stage 3 assumptions while retaining all stage reasons.

### Exercises

1. Repeat the calculation with **the synthetic IFRS 9 schedule and official macroeconomic series** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

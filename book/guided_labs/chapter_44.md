## Worked calculation — How is significant credit deterioration translated into stage assignment?

Stage 2 depends on multiple quantitative and qualitative indicators, while Stage 3 follows credit-impaired/default criteria.

**Companion case:** `synthetic_ifrs9_schedule`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
Stage_i=g(PD\ ratio,DPD,watchlist,default)
\]


### Python implementation

```python
def assign_stage(default, dpd, watchlist, pd_origination, pd_current):
    reasons = []
    if default or dpd >= 90:
        return 3, ("default_or_90_dpd",)
    if dpd >= 30:
        reasons.append("30_dpd_backstop")
    if watchlist:
        reasons.append("watchlist")
    if pd_current >= max(0.01, 2 * pd_origination):
        reasons.append("quantitative_sicr")
    return (2, tuple(reasons)) if reasons else (1, ())


cases = [(False, 0, False, 0.02, 0.025), (False, 35, False, 0.02, 0.03),
         (False, 5, True, 0.02, 0.05), (True, 95, True, 0.02, 0.40)]
print([assign_stage(*case) for case in cases])
```

### Executed result

```output
[(1, ()), (2, ('30_dpd_backstop',)), (2, ('watchlist', 'quantitative_sicr')), (3, ('default_or_90_dpd',))]
```

### Interpretation

The four accounts show Stage 1, two distinct Stage 2 paths and Stage 3. Retaining all trigger flags reveals precedence when delinquency, watchlist and quantitative criteria overlap.

**Validation:** Preserve all trigger reasons and test precedence, cure, probation, and backstop cases.

### Exercises

1. Repeat the calculation with **the synthetic IFRS 9 schedule and a synthetic watchlist history** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

## Worked calculation — How is time to default estimated with censoring?

Survival analysis uses the changing risk set rather than treating every censored account as a non-default.

**Companion case:** `synthetic_behavioral_history`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
\widehat S(t)=\prod_{u=1}^{t}\left(1-\frac{d_u}{n_u}\right)
\]


![Figure 37.1 — Illustrative lifetime cumulative PD curves derived from different 12-month levels.](book/figures/part-07-lifetime-pd.png)

### Python implementation

```python
import pandas as pd


events = pd.DataFrame({"time": [1, 2, 2, 3, 4], "event": [1, 1, 0, 1, 0]})
survival = 1.0
rows = []
for time in sorted(events.loc[events.event == 1, "time"].unique()):
    at_risk = int((events.time >= time).sum())
    defaults = int(((events.time == time) & (events.event == 1)).sum())
    survival *= 1 - defaults / at_risk
    rows.append((time, at_risk, defaults, survival))
print(pd.DataFrame(rows, columns=["time", "at_risk", "defaults", "survival"]).to_string(index=False))
```

### Executed result

```output
time  at_risk  defaults  survival
    1        5         1       0.8
    2        4         1       0.6
    3        2         1       0.3
```

### Interpretation

Survival falls from 1.0 to 0.8 and then 0.6 as defaults occur in the changing risk set. Censored observations reduce later risk sets without being counted as non-defaults forever.

**Validation:** Reconstruct risk sets, event counts, and survival products at each event time.

### Exercises

1. Repeat the calculation with **synthetic lifetime data and an independently generated mortgage-performance panel** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

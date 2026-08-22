## Worked calculation — How are calibrated odds translated into an additive score and reason codes?

Score scaling changes units rather than risk ordering; bin points must reconcile exactly to model log odds.

**Companion case:** `synthetic_retail`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
Score=Offset+Factor\log\frac{1-p}{p},\quad Factor=\frac{PDO}{\log2}
\]


![Figure 30.1 — With PDO equal to 20, doubling good-to-bad odds increases score by 20 points.](book/figures/pdo-score-scale.png)

### Python implementation

```python
import math


pdo, base_score, base_odds = 20.0, 600.0, 50.0
factor = pdo / math.log(2.0)
offset = base_score - factor * math.log(base_odds)


def score_from_pd(pd):
    odds = (1.0 - pd) / pd
    return offset + factor * math.log(odds)


for odds in (25, 50, 100):
    pd = 1.0 / (1.0 + odds)
    print(f"odds={odds:>3}:1  PD={pd:.4%}  score={score_from_pd(pd):.1f}")
```

### Executed result

```output
odds= 25:1  PD=3.8462%  score=580.0
odds= 50:1  PD=1.9608%  score=600.0
odds=100:1  PD=0.9901%  score=620.0
```

### Interpretation

Doubling good-to-bad odds from 25:1 to 50:1 and again to 100:1 adds exactly 20 points each time, confirming the specified PDO scale.

**Validation:** Verify base odds, points-to-double-the-odds, rounding, grade boundaries, and top adverse contributions.

### Exercises

1. Repeat the calculation with **the fitted synthetic scorecard and a fitted South German scorecard** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

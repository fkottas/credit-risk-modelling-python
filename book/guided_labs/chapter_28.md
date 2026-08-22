## Worked calculation — How do WOE and IV summarise the relationship between a characteristic and default?

WOE compares conditional distributions; IV aggregates their separation and is not a causal or universal selection criterion.

**Companion case:** `synthetic_retail`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
WOE_j=\log\frac{p_j^G}{p_j^B},\quad IV=\sum_{j=1}^{J}(p_j^G-p_j^B)WOE_j
\]


![Figure 28.1 — WOE compares conditional distributions; bad rate is the within-bin event proportion.](book/figures/woe-logodds-characteristic.png)

### Python implementation

```python
import math


rows = [("low", 180, 20), ("medium", 120, 50), ("high", 40, 80)]
total_good = sum(good for _, good, _ in rows)
total_bad = sum(bad for _, _, bad in rows)
iv = 0.0
for label, good, bad in rows:
    good_share = good / total_good
    bad_share = bad / total_bad
    woe = math.log(good_share / bad_share)
    contribution = (good_share - bad_share) * woe
    iv += contribution
    print(label, "WOE=", round(woe, 4), "IV contribution=", round(contribution, 4))
print("Total IV:", round(iv, 4))
```

### Executed result

```output
low WOE= 1.3789 IV contribution= 0.5462
medium WOE= 0.0572 IV contribution= 0.0011
high WOE= -1.5115 IV contribution= 0.6283
Total IV: 1.1756
```

### Interpretation

Under the book's good-to-bad convention, the low-risk bin has positive WOE and the high-risk bin negative WOE. Their IV contributions dominate the nearly neutral middle bin.

**Validation:** Reconcile goods and bads, test the sign convention, and perform smoothing sensitivity for zero cells.

### Exercises

1. Repeat the calculation with **South German Credit and the synthetic retail portfolio** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

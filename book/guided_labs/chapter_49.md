## Worked calculation — How is corporate or SME IRB capital calculated from PD, LGD, EAD, and maturity?

The formula converts long-run parameters and systematic dependence into a stressed conditional loss measure.

**Companion case:** `synthetic_corporate_irb`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
K=LGD[N(z)-PD]MA
\]


![Figure 49.1 — Corporate IRB risk weight increases nonlinearly with PD under fixed LGD and maturity.](book/figures/part-09-irb-sensitivity.png)

### Python implementation

```python
import numpy as np
from scipy.stats import norm


pd, lgd, ead, maturity = 0.02, 0.45, 1_000_000.0, 2.5
correlation = 0.12 * (1 - np.exp(-50 * pd)) / (1 - np.exp(-50)) + 0.24 * (
    1 - (1 - np.exp(-50 * pd)) / (1 - np.exp(-50))
)
b = (0.11852 - 0.05478 * np.log(pd)) ** 2
maturity_adjustment = (1 + (maturity - 2.5) * b) / (1 - 1.5 * b)
conditional_pd = norm.cdf((norm.ppf(pd) + np.sqrt(correlation) * norm.ppf(0.999)) /
                          np.sqrt(1 - correlation))
capital_rate = lgd * (conditional_pd - pd) * maturity_adjustment
print({"correlation": round(float(correlation), 6), "conditional_PD": round(float(conditional_pd), 6),
       "capital_rate": round(float(capital_rate), 6), "RWA": round(12.5 * capital_rate * ead, 2)})
```

### Executed result

```output
{'correlation': 0.164146, 'conditional_PD': 0.190259, 'capital_rate': 0.091883, 'RWA': np.float64(1148542.29)}
```

### Interpretation

For the stated inputs, correlation is 0.164146 and the stressed conditional PD is 0.190259, producing a 9.1883% capital rate before any additional jurisdictional treatment.

**Validation:** Reproduce correlation, stressed PD, maturity adjustment, capital rate, and RWA independently.

### Exercises

1. Repeat the calculation with **the synthetic corporate IRB portfolio and Basel reference inputs** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

## Worked calculation — Why do mortgage, qualifying revolving retail, and other retail exposures use different IRB correlations?

Different prescribed correlation functions change capital even when PD, LGD, and EAD are identical.

**Companion case:** `synthetic_corporate_irb`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
K_{retail}=LGD[N(z)-PD]
\]


### Python implementation

```python
import numpy as np
from scipy.stats import norm


pd, lgd, ead = 0.02, 0.35, 250000.0


def retail_capital(correlation):
    stressed_pd = norm.cdf((norm.ppf(pd) + np.sqrt(correlation) * norm.ppf(0.999)) /
                           np.sqrt(1 - correlation))
    return lgd * (stressed_pd - pd)


for asset_class, correlation in [("residential mortgage", 0.15), ("QRRE", 0.04)]:
    capital = retail_capital(correlation)
    print(asset_class, "capital rate", round(float(capital), 6),
          "RWA", round(float(12.5 * capital * ead), 2))
```

### Executed result

```output
residential mortgage capital rate 0.054715 RWA 170984.78
QRRE capital rate 0.017996 RWA 56238.98
```

### Interpretation

Identical PD, LGD and EAD produce different capital rates for mortgage and QRRE because the prescribed correlations differ. This numerical comparison does not establish asset-class eligibility.

**Validation:** Hold parameters constant and isolate the asset-class formula effect.

### Exercises

1. Repeat the calculation with **synthetic retail exposures and Basel reference inputs** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

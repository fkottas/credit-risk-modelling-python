## Worked calculation — Which model represents the mass points and continuous part of LGD?

LGD often combines cure or full recovery with continuous severity and may require downturn calibration for regulatory use.

**Companion case:** `synthetic_recovery`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
\widehat{LGD}=\Pr(LGD>0\mid x)\,\mathbb{E}[LGD\mid LGD>0,x]
\]


### Python implementation

```python
import numpy as np


probability_positive_lgd = np.array([0.20, 0.55, 0.80])
severity_if_positive = np.array([0.25, 0.40, 0.60])
expected_lgd = probability_positive_lgd * severity_if_positive
downturn_multiplier = 1.20
downturn_lgd = np.minimum(expected_lgd * downturn_multiplier, 1.0)
for p, severity, base, downturn in zip(
    probability_positive_lgd, severity_if_positive, expected_lgd, downturn_lgd
):
    print(f"P(LGD>0)={p:.2f}  E[LGD|LGD>0]={severity:.2f}  base={base:.3f}  downturn={downturn:.3f}")
```

### Executed result

```output
P(LGD>0)=0.20  E[LGD|LGD>0]=0.25  base=0.050  downturn=0.060
P(LGD>0)=0.55  E[LGD|LGD>0]=0.40  base=0.220  downturn=0.264
P(LGD>0)=0.80  E[LGD|LGD>0]=0.60  base=0.480  downturn=0.576
```

### Interpretation

The two-part calculation multiplies the probability of positive loss by conditional severity. The downturn multiplier raises each combined estimate while preserving the displayed component structure.

**Validation:** Evaluate component probabilities, conditional severity, monetary bias, bounds, and segment calibration.

### Exercises

1. Repeat the calculation with **synthetic recovery cash flows and corporate bankruptcy indicators** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

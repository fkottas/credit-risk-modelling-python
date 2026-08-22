## Worked calculation — How do the standardised and IRB approaches translate exposure into regulatory capital?

The approaches use different inputs and permissions, so their outputs cannot be compared without the same regulatory perimeter.

**Companion case:** `synthetic_corporate_irb`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
RWA=12.5\,K\,EAD
\]


### Python implementation

```python
import pandas as pd


def standardised_rwa(exposure: float, risk_weight: float) -> dict:
    if exposure < 0 or risk_weight < 0:
        raise ValueError("Exposure and risk weight cannot be negative")
    rwa = exposure * risk_weight
    return {"exposure": exposure, "risk_weight": risk_weight, "rwa": rwa,
            "minimum_capital_8pct": 0.08 * rwa}


rows = [standardised_rwa(1_000_000, rw) for rw in (0.20, 0.50, 1.00, 1.50)]
print(pd.DataFrame(rows).to_string(index=False))
```

### Executed result

```output
exposure  risk_weight       rwa  minimum_capital_8pct
  1000000          0.2  200000.0               16000.0
  1000000          0.5  500000.0               40000.0
  1000000          1.0 1000000.0               80000.0
  1000000          1.5 1500000.0              120000.0
```

### Interpretation

RWA increases in direct proportion to the stated risk weight and exposure in this standardised illustration; minimum capital is 8% of RWA. Eligibility for a risk weight is a separate regulatory question.

**Validation:** Reconcile exposure, risk weight, RWA, and the corresponding capital amount.

### Exercises

1. Repeat the calculation with **the synthetic corporate IRB portfolio and EBA Pillar 3 aggregates** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

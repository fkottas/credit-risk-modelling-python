## Worked calculation — Why are default and IRB asset class determined before parameter estimation?

Definitions determine the event population and the regulatory formula branch.

**Companion case:** `synthetic_corporate_irb`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
D_i=\mathbf{1}\{\text{default criteria hold}\}
\]


### Python implementation

```python
import pandas as pd


def regulatory_default(days_past_due, unlikely_to_pay, distressed_restructure=False):
    reasons = []
    if days_past_due >= 90:
        reasons.append("90_dpd_backstop")
    if unlikely_to_pay:
        reasons.append("unlikely_to_pay")
    if distressed_restructure:
        reasons.append("distressed_restructure")
    return bool(reasons), tuple(reasons)


cases = pd.DataFrame({"dpd": [0, 65, 92], "utp": [False, True, False], "restructure": [False, False, True]})
cases[["default", "reasons"]] = cases.apply(
    lambda r: pd.Series(regulatory_default(r.dpd, r.utp, r.restructure)), axis=1
)
print(cases.to_string(index=False))
```

### Executed result

```output
dpd   utp  restructure  default                                   reasons
   0 False        False    False                                        ()
  65  True        False     True                        (unlikely_to_pay,)
  92 False         True     True (90_dpd_backstop, distressed_restructure)
```

### Interpretation

The output retains both the binary default flag and the criteria that triggered it. This prevents a downstream model target from losing the original default rationale.

**Validation:** Reclassify one exposure and show every downstream change in target, parameter, and capital output.

### Exercises

1. Repeat the calculation with **the synthetic corporate portfolio and Basel worked classifications** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

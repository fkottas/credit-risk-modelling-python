## Worked calculation — How does CECL differ from IFRS 9 despite a shared expected-loss objective?

CECL generally recognises lifetime expected loss from initial recognition, whereas IFRS 9 changes horizon by stage.

**Companion case:** `synthetic_ifrs9_schedule`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
CECL=\mathbb{E}[\text{contractual cash shortfalls over life}]
\]


![Figure 17.1 — IFRS 9 changes the measurement horizon by stage; the CECL illustration begins with lifetime loss.](book/figures/ifrs9-cecl-horizon.png)

### Python implementation

```python
import pandas as pd


def cecl_loss_rate(exposure, historical_loss_rate, qualitative_adjustment=0.0):
    adjusted = historical_loss_rate + qualitative_adjustment
    if exposure < 0 or not 0 <= adjusted <= 1:
        raise ValueError("Invalid exposure or adjusted loss rate")
    return exposure * adjusted


pools = pd.DataFrame({
    "pool": ["prime", "near_prime", "subprime"], "exposure": [1_000_000, 600_000, 250_000],
    "historical_loss_rate": [0.008, 0.035, 0.110], "qualitative_adjustment": [0.002, 0.005, 0.010],
})
pools["lifetime_cecl"] = pools.apply(
    lambda r: cecl_loss_rate(r.exposure, r.historical_loss_rate, r.qualitative_adjustment), axis=1
)
print(pools.to_string(index=False))
print("Total CECL:", pools["lifetime_cecl"].sum())
```

### Executed result

```output
pool  exposure  historical_loss_rate  qualitative_adjustment  lifetime_cecl
     prime   1000000                 0.008                   0.002        10000.0
near_prime    600000                 0.035                   0.005        24000.0
  subprime    250000                 0.110                   0.010        30000.0
Total CECL: 64000.0
```

### Interpretation

The calculated lifetime allowance is exposure multiplied by the historically based rate plus the stated qualitative adjustment. The adjustment is displayed separately so it can be challenged and removed.

**Validation:** Keep the same contractual schedule and isolate the effect of horizon, staging, forecast, and reversion assumptions.

### Exercises

1. Repeat the calculation with **a synthetic receivables schedule and a synthetic staged-loan schedule** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

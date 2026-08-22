## Worked calculation — What data are generated at each stage of a credit account?

Application, servicing, delinquency, default, and recovery records have different observation units and time stamps.

**Companion case:** `synthetic_behavioral_history`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
L_i=\sum_{t=1}^{T} d_t\left[(C_{it}-P_{it})-Rec_{it}+K_{it}\right]
\]


### Python implementation

```python
import pandas as pd

ALLOWED = {
    "application": {"approved", "declined"}, "approved": {"current"},
    "current": {"delinquent", "prepaid"}, "delinquent": {"current", "default"},
    "default": {"recovery", "closed"}, "recovery": {"closed"}, "declined": set(),
    "prepaid": set(), "closed": set(),
}


def validate_lifecycle(events: pd.DataFrame) -> pd.DataFrame:
    ordered = events.sort_values(["account_id", "event_time"]).copy()
    ordered["previous_state"] = ordered.groupby("account_id")["state"].shift()
    ordered["valid_transition"] = ordered.apply(
        lambda r: True if pd.isna(r.previous_state) else r.state in ALLOWED.get(r.previous_state, set()), axis=1
    )
    return ordered


events = pd.DataFrame({
    "account_id": ["A"] * 5, "event_time": pd.date_range("2025-01-01", periods=5, freq="30D"),
    "state": ["application", "approved", "current", "delinquent", "default"],
})
audit = validate_lifecycle(events)
print(audit[["event_time", "previous_state", "state", "valid_transition"]].to_string(index=False))
```

### Executed result

```output
event_time previous_state       state  valid_transition
2025-01-01            NaN application              True
2025-01-31    application    approved              True
2025-03-02       approved     current              True
2025-04-01        current  delinquent              True
2025-05-01     delinquent     default              True
```

### Interpretation

Each event follows an allowed predecessor in the miniature lifecycle. A valid state sequence is necessary before durations, migrations or cure rates can be estimated.

**Validation:** Test permitted state transitions and reconcile event-level balances to account-level outcomes.

### Exercises

1. Repeat the calculation with **synthetic behavioural history and synthetic recovery cash flows** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

## Worked calculation — How are application, facility, monthly performance, and bureau records joined as of a decision date?

An unrestricted join can introduce future information or duplicate exposure.

**Companion case:** `synthetic_behavioral_history`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
X_t=\operatorname{join}_{\tau\le t}(A_t,B_\tau)
\]


### Python implementation

```python
import pandas as pd


def point_in_time_join(decisions: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for decision in decisions.itertuples(index=False):
        known = events.loc[
            (events.customer_id == decision.customer_id)
            & (events.effective_time <= decision.decision_time)
            & (events.processing_time <= decision.decision_time)
        ].sort_values(["effective_time", "processing_time"])
        chosen = known.tail(1)
        rows.append({
            "customer_id": decision.customer_id, "decision_time": decision.decision_time,
            "selected_value": None if chosen.empty else float(chosen.iloc[0]["value"]),
            "selected_effective_time": None if chosen.empty else chosen.iloc[0]["effective_time"],
        })
    return pd.DataFrame(rows)


decisions = pd.DataFrame({"customer_id": ["A", "B"], "decision_time": pd.to_datetime(["2025-03-15", "2025-03-15"])})
events = pd.DataFrame({
    "customer_id": ["A", "A", "B"], "effective_time": pd.to_datetime(["2025-02-01", "2025-04-01", "2025-02-20"]),
    "processing_time": pd.to_datetime(["2025-02-02", "2025-04-02", "2025-03-20"]), "value": [10, 999, 20],
})
result = point_in_time_join(decisions, events)
print(result.to_string(index=False))
```

### Executed result

```output
customer_id decision_time  selected_value selected_effective_time
          A    2025-03-15            10.0              2025-02-01
          B    2025-03-15             NaN                     NaT
```

### Interpretation

Customer A receives the value effective before the decision date, not the later database value. Customer B remains missing because no eligible historical record exists.

**Validation:** Verify join cardinality, source availability time, and account totals before and after the join.

### Exercises

1. Repeat the calculation with **synthetic behavioural history and an independently generated mortgage panel** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

"""Chapter 21: Relational Credit Data, Lineage, and Point-in-Time Joins.

Standalone construction code: no creditriskbook imports.
"""

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
        rows.append(
            {
                "customer_id": decision.customer_id,
                "decision_time": decision.decision_time,
                "selected_value": None if chosen.empty else float(chosen.iloc[0]["value"]),
                "selected_effective_time": None
                if chosen.empty
                else chosen.iloc[0]["effective_time"],
            }
        )
    return pd.DataFrame(rows)


decisions = pd.DataFrame(
    {"customer_id": ["A", "B"], "decision_time": pd.to_datetime(["2025-03-15", "2025-03-15"])}
)
events = pd.DataFrame(
    {
        "customer_id": ["A", "A", "B"],
        "effective_time": pd.to_datetime(["2025-02-01", "2025-04-01", "2025-02-20"]),
        "processing_time": pd.to_datetime(["2025-02-02", "2025-04-02", "2025-03-20"]),
        "value": [10, 999, 20],
    }
)
result = point_in_time_join(decisions, events)
print(result.to_string(index=False))

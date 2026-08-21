"""Chapter 11: Origination, Account Management, Default, and Recovery.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd

ALLOWED = {
    "application": {"approved", "declined"},
    "approved": {"current"},
    "current": {"delinquent", "prepaid"},
    "delinquent": {"current", "default"},
    "default": {"recovery", "closed"},
    "recovery": {"closed"},
    "declined": set(),
    "prepaid": set(),
    "closed": set(),
}


def validate_lifecycle(events: pd.DataFrame) -> pd.DataFrame:
    ordered = events.sort_values(["account_id", "event_time"]).copy()
    ordered["previous_state"] = ordered.groupby("account_id")["state"].shift()
    ordered["valid_transition"] = ordered.apply(
        lambda r: (
            True if pd.isna(r.previous_state) else r.state in ALLOWED.get(r.previous_state, set())
        ),
        axis=1,
    )
    return ordered


events = pd.DataFrame(
    {
        "account_id": ["A"] * 5,
        "event_time": pd.date_range("2025-01-01", periods=5, freq="30D"),
        "state": ["application", "approved", "current", "delinquent", "default"],
    }
)
audit = validate_lifecycle(events)
print(audit[["event_time", "previous_state", "state", "valid_transition"]].to_string(index=False))

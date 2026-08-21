"""Chapter 1: Credit Risk as Uncertain Cash Flows.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def discounted_cash_shortfall(schedule: pd.DataFrame) -> pd.DataFrame:
    """Calculate period and present-value loss without hiding intermediates."""
    required = {"month", "contractual", "received", "recovery", "workout_cost", "eir"}
    missing = required - set(schedule)
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")
    out = schedule.copy(deep=True)
    out["cash_shortfall"] = (
        out["contractual"] - out["received"] - out["recovery"] + out["workout_cost"]
    )
    out["discount_factor"] = (1.0 + out["eir"]) ** (-out["month"] / 12.0)
    out["pv_loss"] = out["cash_shortfall"] * out["discount_factor"]
    return out


cashflows = pd.DataFrame(
    {
        "month": [1, 2, 3],
        "contractual": [350.0, 350.0, 350.0],
        "received": [350.0, 200.0, 0.0],
        "recovery": [0.0, 0.0, 120.0],
        "workout_cost": [0.0, 5.0, 15.0],
        "eir": [0.12, 0.12, 0.12],
    }
)
audit = discounted_cash_shortfall(cashflows)
print(
    audit[["month", "cash_shortfall", "discount_factor", "pv_loss"]].round(2).to_string(index=False)
)
print("Total PV loss:", round(audit["pv_loss"].sum(), 2))

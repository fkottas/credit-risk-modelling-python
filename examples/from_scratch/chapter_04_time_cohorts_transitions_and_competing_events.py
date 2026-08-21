"""Chapter 4: Time, Cohorts, Transitions, and Competing Events.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def transition_matrix(history: pd.DataFrame) -> pd.DataFrame:
    """Estimate one-step transition probabilities from adjacent observed states."""
    ordered = history.sort_values(["account_id", "month"]).copy()
    ordered["next_state"] = ordered.groupby("account_id")["state"].shift(-1)
    pairs = ordered.dropna(subset=["next_state"])
    counts = pd.crosstab(pairs["state"], pairs["next_state"])
    return counts.div(counts.sum(axis=1), axis=0).fillna(0.0)


history = pd.DataFrame(
    {
        "account_id": ["A"] * 4 + ["B"] * 4 + ["C"] * 4,
        "month": [1, 2, 3, 4] * 3,
        "state": ["C", "C", "30", "60", "C", "30", "C", "C", "C", "C", "P", "P"],
    }
)
matrix = transition_matrix(history)
print(matrix.round(3).to_string())
print("Rows reconcile:", matrix.sum(axis=1).round(8).eq(1).all())

"""Chapter 18: Consumer Protection, Fair Lending, Privacy, and High-Risk AI.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def group_decision_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for group, part in frame.groupby("group", observed=True):
        rows.append(
            {
                "group": group,
                "n": len(part),
                "approval_rate": part["approved"].mean(),
                "true_positive_rate": part.loc[part["creditworthy"] == 1, "approved"].mean(),
                "false_positive_rate": part.loc[part["creditworthy"] == 0, "approved"].mean(),
            }
        )
    return pd.DataFrame(rows)


decisions = pd.DataFrame(
    {
        "group": ["reference"] * 6 + ["comparison"] * 6,
        "creditworthy": [1, 1, 1, 0, 0, 0] * 2,
        "approved": [1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    }
)
metrics = group_decision_metrics(decisions)
print(metrics.round(3).to_string(index=False))
print(
    "Approval-rate gap:",
    round(metrics.loc[0, "approval_rate"] - metrics.loc[1, "approval_rate"], 3),
)

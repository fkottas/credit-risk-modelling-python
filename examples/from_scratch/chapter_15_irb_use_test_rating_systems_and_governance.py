"""Chapter 15: IRB Use Test, Rating Systems, and Governance.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def grade_backtest(frame: pd.DataFrame) -> pd.DataFrame:
    grouped = frame.groupby("grade", observed=True)
    result = grouped.agg(
        observations=("default", "size"),
        predicted_pd=("pd", "mean"),
        observed_rate=("default", "mean"),
        defaults=("default", "sum"),
    )
    result["observed_to_expected"] = result["observed_rate"] / result["predicted_pd"]
    return result.reset_index()


portfolio = pd.DataFrame(
    {
        "grade": ["A"] * 5 + ["B"] * 5,
        "pd": [0.02] * 5 + [0.10] * 5,
        "default": [0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
    }
)
print(grade_backtest(portfolio).round(3).to_string(index=False))

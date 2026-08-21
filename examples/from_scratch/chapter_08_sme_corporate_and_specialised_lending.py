"""Chapter 8: SME, Corporate, and Specialised Lending.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def corporate_ratios(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["debt_to_ebitda"] = out["debt"] / out["ebitda"].replace(0, pd.NA)
    out["interest_cover"] = out["ebit"] / out["interest_expense"].replace(0, pd.NA)
    out["dscr"] = out["cash_available_for_debt_service"] / out["debt_service"].replace(0, pd.NA)
    out["equity_ratio"] = out["equity"] / out["assets"].replace(0, pd.NA)
    return out


companies = pd.DataFrame(
    {
        "company": ["StableCo", "GrowthCo", "StressedCo"],
        "debt": [200, 450, 600],
        "ebitda": [120, 90, 40],
        "ebit": [95, 55, 10],
        "interest_expense": [20, 30, 35],
        "cash_available_for_debt_service": [100, 70, 20],
        "debt_service": [55, 65, 70],
        "equity": [500, 250, 80],
        "assets": [900, 850, 780],
    }
)
print(corporate_ratios(companies).round(2).to_string(index=False))

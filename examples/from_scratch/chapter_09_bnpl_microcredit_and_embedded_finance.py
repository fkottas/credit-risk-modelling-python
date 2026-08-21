"""Chapter 9: BNPL, Microcredit, and Embedded Finance.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def bnpl_schedule(purchase: float, instalments: int, monthly_income: float) -> pd.DataFrame:
    if purchase <= 0 or instalments < 2 or monthly_income <= 0:
        raise ValueError("Positive purchase, income, and at least two instalments are required")
    payment = purchase / instalments
    burden = payment / monthly_income
    return pd.DataFrame(
        {"instalment": range(1, instalments + 1), "payment": payment, "payment_to_income": burden}
    )


schedule = bnpl_schedule(480.0, 4, 2_000.0)
print(schedule.round(3).to_string(index=False))
print(
    "Total payments:",
    schedule["payment"].sum(),
    "monthly burden:",
    schedule["payment_to_income"].iloc[0],
)

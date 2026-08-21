"""Chapter 7: Retail Loans, Credit Cards, and Mortgages.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def product_exposure(product: str, drawn: float, limit: float, ccf: float) -> float:
    if drawn < 0 or limit < drawn or not 0 <= ccf <= 1:
        raise ValueError("Invalid drawn amount, limit, or CCF")
    if product in {"credit_card", "overdraft"}:
        return drawn + ccf * (limit - drawn)
    return drawn


facilities = pd.DataFrame(
    {
        "product": ["term_loan", "credit_card", "overdraft"],
        "drawn": [18_000.0, 2_000.0, 7_000.0],
        "limit": [18_000.0, 8_000.0, 10_000.0],
        "ccf": [0.0, 0.65, 0.40],
    }
)
facilities["ead"] = [
    product_exposure(*row) for row in facilities.itertuples(index=False, name=None)
]
print(facilities.to_string(index=False))

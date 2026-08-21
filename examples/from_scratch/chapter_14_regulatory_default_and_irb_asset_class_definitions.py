"""Chapter 14: Regulatory Default and IRB Asset-Class Definitions.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def regulatory_default(days_past_due, unlikely_to_pay, distressed_restructure=False):
    reasons = []
    if days_past_due >= 90:
        reasons.append("90_dpd_backstop")
    if unlikely_to_pay:
        reasons.append("unlikely_to_pay")
    if distressed_restructure:
        reasons.append("distressed_restructure")
    return bool(reasons), tuple(reasons)


cases = pd.DataFrame(
    {"dpd": [0, 65, 92], "utp": [False, True, False], "restructure": [False, False, True]}
)
cases[["default", "reasons"]] = cases.apply(
    lambda r: pd.Series(regulatory_default(r.dpd, r.utp, r.restructure)), axis=1
)
print(cases.to_string(index=False))

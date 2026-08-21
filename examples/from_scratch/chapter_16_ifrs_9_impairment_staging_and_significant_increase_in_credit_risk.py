"""Chapter 16: IFRS 9 Impairment, Staging, and Significant Increase in Credit Risk.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def assign_ifrs9_stage(origination_pd, current_pd, dpd, watchlist, default):
    if default or dpd >= 90:
        return 3, "credit_impaired_or_default"
    pd_ratio = current_pd / origination_pd if origination_pd > 0 else float("inf")
    if dpd >= 30 or watchlist or pd_ratio >= 2.0:
        return 2, "significant_increase_in_credit_risk"
    return 1, "performing_without_sicr"


accounts = pd.DataFrame(
    {
        "account": ["A", "B", "C"],
        "orig_pd": [0.02, 0.02, 0.03],
        "current_pd": [0.025, 0.055, 0.30],
        "dpd": [0, 35, 95],
        "watchlist": [False, False, True],
        "default": [False, False, True],
    }
)
accounts[["stage", "reason"]] = accounts.apply(
    lambda r: pd.Series(assign_ifrs9_stage(r.orig_pd, r.current_pd, r.dpd, r.watchlist, r.default)),
    axis=1,
)
print(accounts[["account", "stage", "reason"]].to_string(index=False))

"""Chapter 12: Risk Appetite, Affordability, Overrides, and Policy Rules.

Standalone construction code: no creditriskbook imports.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyDecision:
    result: str
    reasons: tuple[str, ...]
    human_review: bool


def apply_credit_policy(pd, debt_service, verified_income, requested_amount, max_amount=25_000):
    reasons = []
    if verified_income <= 0:
        reasons.append("income_not_verified")
    elif debt_service / verified_income > 0.40:
        reasons.append("affordability_limit")
    if pd > 0.15:
        reasons.append("pd_above_appetite")
    if requested_amount > max_amount:
        reasons.append("amount_outside_delegation")
    if reasons:
        return PolicyDecision("refer_or_decline", tuple(reasons), requested_amount > max_amount)
    return PolicyDecision("eligible_for_human_approval", (), True)


for case in [(0.04, 600, 2_500, 10_000), (0.20, 1_200, 2_000, 35_000)]:
    print(apply_credit_policy(*case))

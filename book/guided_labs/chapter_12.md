## Worked calculation — How are model estimates combined with affordability and credit policy?

PD estimates expected risk; it does not encode delegated authority, affordability, or risk appetite.

**Companion case:** `synthetic_retail`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
\max_c\;\mathbb{E}[\Pi(c)]\quad\text{s.t. affordability and risk constraints}
\]


### Python implementation

```python
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
```

### Executed result

```output
PolicyDecision(result='eligible_for_human_approval', reasons=(), human_review=True)
PolicyDecision(result='refer_or_decline', reasons=('affordability_limit', 'pd_above_appetite', 'amount_outside_delegation'), human_review=True)
```

### Interpretation

The same calculation can return human-review eligibility or referral when affordability, PD appetite and delegated amount change. The reasons show which policy condition determined the result.

**Validation:** Hold PD constant while varying policy inputs and confirm that the reason codes identify the changed rule.

### Exercises

1. Repeat the calculation with **the synthetic retail portfolio and BLS household expenditure microdata** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

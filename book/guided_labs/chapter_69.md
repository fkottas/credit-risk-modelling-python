## Worked calculation — How can an LLM draft a credit memorandum without treating generated prose as evidence?

Language-model probability is not truth, policy compliance, or PD.

**Companion case:** `synthetic_credit_documents`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
p(w_{1:T}\mid x)=\prod_{t=1}^{T}p(w_t\mid w_{<t},x),\quad SupportRate=\frac{1}{|C|}\sum_{c\in C}s(c)
\]


### Python implementation

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceMemo:
    application_id: str
    evidence_ids: tuple[str, ...]
    policy_citations: tuple[str, ...]
    recommendation: str


ALLOWED = {"request_missing_evidence", "refer_for_human_review", "no_automated_action"}


def validate_memo(memo, evidence_ids, policy_ids):
    if memo.recommendation not in ALLOWED:
        raise ValueError("recommendation is not authorised")
    if set(memo.evidence_ids) - set(evidence_ids):
        raise ValueError("invented evidence citation")
    if set(memo.policy_citations) - set(policy_ids):
        raise ValueError("invented policy citation")
    return True


memo = EvidenceMemo("APP-1", ("EV-1",), ("POL-1",), "request_missing_evidence")
print({"valid": validate_memo(memo, {"EV-1"}, {"POL-1"}), "recommendation": memo.recommendation})
```

### Executed result

```output
{'valid': True, 'recommendation': 'request_missing_evidence'}
```

### Interpretation

The memorandum passes schema and citation-identifier checks and recommends requesting evidence. Validation confirms contract compliance, not the truth of the cited content.

**Validation:** Validate structured fields, citations, missing evidence, unsupported claims, and permitted recommendation values.

### Exercises

1. Repeat the calculation with **synthetic application packets and approved policy documents** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

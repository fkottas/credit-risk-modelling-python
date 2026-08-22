## Worked calculation — How are an agent’s tools, memory, evidence, and authority restricted?

The final answer is insufficient for safety assessment because tool calls and data access occur throughout the workflow.

**Companion case:** `synthetic_credit_documents`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
\tau=(s_0,a_0,o_1,\ldots,s_T),\quad Allowed(a)=Policy(action,role,scope,evidence,approval,time)
\]


![Figure 70.1 — Evidence, analysis, policy evaluation, and human authority remain separate.](book/figures/part-12-agent-governance.png)

### Python implementation

```python
DENIED = {"approve_customer_credit", "decline_customer_credit", "deploy_model", "post_ledger"}
READ_ONLY = {"retrieve_policy", "read_quality_report"}


def permission(action, role, evidence_ids, approved=False):
    if action in DENIED:
        return "DENY"
    if not evidence_ids:
        return "DENY_MISSING_EVIDENCE"
    if action in READ_ONLY:
        return "ALLOW_READ_ONLY"
    if action == "request_human_validation":
        return "PENDING_HUMAN_APPROVAL" if not approved else "APPROVED_PROPOSAL_ONLY"
    return "DENY_UNKNOWN_ACTION"


attempts = ["retrieve_policy", "request_human_validation", "approve_customer_credit"]
print([(action, permission(action, "document_assistant", ("EV-1",))) for action in attempts])
```

### Executed result

```output
[('retrieve_policy', 'ALLOW_READ_ONLY'), ('request_human_validation', 'PENDING_HUMAN_APPROVAL'), ('approve_customer_credit', 'DENY')]
```

### Interpretation

Policy retrieval is read-only, human validation remains pending and customer approval is denied. The language component cannot convert evidence into decision authority.

**Validation:** Evaluate every action against deterministic role, scope, evidence, approval, and time rules.

### Exercises

1. Repeat the calculation with **synthetic documents and synthetic model-review records** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

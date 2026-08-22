## Worked calculation — How can document review be automated while retaining human credit authority?

Automation can reduce clerical work, but missing or inconsistent evidence requires an authorised reviewer.

**Companion case:** `synthetic_credit_documents`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
RECEIVED\rightarrow EXTRACTED\rightarrow RECONCILED\rightarrow RETRIEVED\rightarrow VALIDATED\rightarrow HUMAN\_REVIEW
\]


### Python implementation

```python
from creditriskbook.data import make_synthetic_credit_document_case
from creditriskbook.nlp import DocumentUnderwritingAssistant


case = make_synthetic_credit_document_case(n_applications=16, seed=7801)
assistant = DocumentUnderwritingAssistant()
result = assistant.run(case.applications.iloc[0], case.documents, case.policy_documents)
print({
    "application_id": result.memo.application_id,
    "recommendation": result.memo.recommendation,
    "missing_evidence": result.memo.missing_evidence,
    "policy_decision": result.policy_decision.decision,
})
print(result.trace)
```

### Executed result

```output
{'application_id': 'DOCAPP-00001', 'recommendation': 'request_missing_evidence', 'missing_evidence': ('payslip',), 'policy_decision': 'PENDING_HUMAN_APPROVAL'}
('packet_selected', 'facts_extracted', 'facts_reconciled', 'approved_policy_retrieved', 'structured_output_validated', 'permission_policy_evaluated')
```

### Interpretation

The assistant identifies a missing payslip, recommends requesting evidence and stops at pending human approval. The trace shows the ordered steps that produced that result.

**Validation:** Trace each extracted fact and proposed action to source spans, policy, and the recorded human decision.

### Exercises

1. Repeat the calculation with **synthetic credit packets and synthetic policy documents** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

## Mathematics-to-code laboratory — construction and controlled promotion

### 1. Start with the decision, observation unit, and estimand

This laboratory does not begin by importing a finished modelling function. The class first states what **Document Underwriting Agents and Human Workflow Automation** must estimate, which record is one observation, when information becomes available, and which decision or control will consume the result. We begin with `synthetic_credit_documents`. Before calculating anything, inspect the unit of observation, time index, target or outcome field, currency and percentage conventions, licence statement, generator seed or publisher checksum, and limitations. A mathematically correct formula applied to the wrong horizon or population is still a wrong model.

The chapter's principal mathematical object is

\[
RECEIVED\rightarrow EXTRACTED\rightarrow RECONCILED\rightarrow RETRIEVED\rightarrow VALIDATED\rightarrow HUMAN\_REVIEW
\]

Write every symbol next to its business definition and unit. Conditional probabilities must identify the information set; monetary quantities must identify currency and reference date; rates must distinguish proportions from percentages; and time must identify whether it is calendar, contractual, behavioural or default-workout time. This notation contract becomes the first object in the library rather than an undocumented convention hidden in code.

### 2. Derive before implementing

Reconstruct the expression from elementary operations. Identify the random variable, conditioning information, aggregation rule and any approximation. Then separate estimand, estimator and implementation. The estimand is the population quantity the institution needs. The estimator is the statistical rule learned from available observations. The implementation is a versioned algorithm with finite precision, boundary handling and controls. For every transformation, state which assumptions make it valid and how the result changes if those assumptions fail. This step prevents students from treating a library call as a definition.

For a hand audit, select five records, retain the raw values, and calculate every intermediate column. Reconcile the individual rows to the reported total. Repeat after changing one input while holding the others fixed. The direction need not always be monotonic, but any non-monotonic response must be explained by the mathematics rather than accepted because software returned it. Missing, impossible or temporally unavailable values are reported and quarantined; they are not silently imputed or winsorised.

### 3. Implement the first transparent component

The chapter keeps the estimator visible. Reusable data access may now be imported, while the method being taught is derived, implemented, tested, and reviewed before promotion. Students preserve the source values, expose intermediate quantities, validate boundaries, and print an auditable result. The code below is a construction step, not an illustration of a library that appeared before the course.

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

### 4. Inspect the executed output

The output below is produced by the displayed code during the book build. Recalculate at least one row manually before accepting it. A student submission must retain both code and output; an unexplained screenshot is not reproducible evidence.

```output
{'application_id': 'DOCAPP-00001', 'recommendation': 'request_missing_evidence', 'missing_evidence': ('payslip',), 'policy_decision': 'PENDING_HUMAN_APPROVAL'}
('packet_selected', 'facts_extracted', 'facts_reconciled', 'approved_policy_retrieved', 'structured_output_validated', 'permission_policy_evaluated')
```

### 5. Test mathematics, data, and policy separately

Add three kinds of tests. A mathematical invariant checks an identity, bound or reconciliation implied by the formula. A data test checks schema, units, missingness, dates, duplicates, permitted categories and source identity. A policy test checks that the calculation is not silently converted into authority it does not possess. Use at least one ordinary case, one boundary case, one missing-value case, one temporally invalid case and one deliberately corrupted case. Record expected outputs before running the implementation so that the test is not merely a copy of the code.

### 6. Extend, compare datasets, and document

After the simple component is understood, replace the audit statistic with the full chapter method, retaining the same input contract and evidence fields. Compare the result across at least two compatible datasets or across synthetic segments. Explain differences using population, product, horizon and data-generation mechanisms rather than only performance metrics. The student deliverable is a source module, tests, a notebook, a characteristic or parameter table, a short validation note and an explicit statement of what the component is not allowed to decide. This staged build is how the final scorecard, IFRS 9, IRB and governed-agent libraries emerge during the book.

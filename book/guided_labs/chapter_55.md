## Worked calculation — What constitutes independent and proportionate model validation?

Validation evaluates conceptual soundness, data, performance, implementation, use, and governance rather than repeating development output.

**Companion case:** `synthetic_retail`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
Unresolved=\sum_j\mathbf{1}\{test_j=fail\}
\]


### Python implementation

```python
criteria = {
    "conceptual_soundness": True,
    "data_reconstruction": True,
    "independent_benchmark": False,
    "implementation_reconciliation": True,
}
findings = [name for name, passed in criteria.items() if not passed]
opinion = "conditional" if findings else "satisfactory"
print({"validation_opinion": opinion, "open_findings": findings})
```

### Executed result

```output
{'validation_opinion': 'conditional', 'open_findings': ['independent_benchmark']}
```

### Interpretation

The validation opinion is conditional because an independent benchmark remains open. Recording the finding prevents a qualified conclusion from being read as unconditional approval.

**Validation:** Trace every conclusion to independent evidence and record scope, severity, owner, and due date.

### Exercises

1. Repeat the calculation with **a synthetic corporate model and a synthetic retail scorecard** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

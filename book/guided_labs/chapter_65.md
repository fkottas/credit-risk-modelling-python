## Worked calculation — How are incidents contained and models recalibrated, redeveloped, rolled back, or retired?

The appropriate response depends on customer, accounting, capital, security, and operational impact.

**Companion case:** `synthetic_retail`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
Trigger=\mathbf{1}\{metric>threshold\}\times severity
\]


### Python implementation

```python
incidents = [
    {"issue": "scoring service unavailable", "customer_effect": True, "financial_effect": False},
    {"issue": "wrong model version", "customer_effect": True, "financial_effect": True},
    {"issue": "late monitoring report", "customer_effect": False, "financial_effect": False},
]
for incident in incidents:
    severity = "critical" if incident["customer_effect"] and incident["financial_effect"] else (
        "high" if incident["customer_effect"] else "moderate"
    )
    response = "stop and rollback" if severity == "critical" else "investigate under incident procedure"
    print(incident["issue"], "->", severity, "->", response)
```

### Executed result

```output
scoring service unavailable -> high -> investigate under incident procedure
wrong model version -> critical -> stop and rollback
late monitoring report -> moderate -> investigate under incident procedure
```

### Interpretation

The severity mapping distinguishes service unavailability, a wrong model version and a late report. The wrong version receives the strongest response because continuing scores may be invalid.

**Validation:** Record detection, severity, containment, correction, customer impact, approval, and post-incident review.

### Exercises

1. Repeat the calculation with **synthetic service incidents and synthetic calibration deterioration** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

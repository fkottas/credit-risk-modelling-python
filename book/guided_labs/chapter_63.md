## Worked calculation — Which technical and governance conditions precede production deployment?

Testing, security, approval, reconciliation, and rollback address different failure modes.

**Companion case:** `synthetic_retail`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
Release=I_{tests}I_{approval}I_{security}I_{reconciliation}
\]


### Python implementation

```python
checks = {
    "unit_tests": True,
    "integration_tests": True,
    "security_scan": True,
    "validation_approval": True,
    "uat_reconciliation": False,
    "rollback_test": True,
}
failed = [name for name, passed in checks.items() if not passed]
print({"deployment_status": "BLOCKED" if failed else "ELIGIBLE",
       "failed_requirements": failed})
```

### Executed result

```output
{'deployment_status': 'BLOCKED', 'failed_requirements': ['uat_reconciliation']}
```

### Interpretation

Deployment is blocked solely because UAT reconciliation failed. This demonstrates that mandatory conditions are conjunctive rather than a weighted quality score.

**Validation:** Block deployment whenever a mandatory condition fails and test rollback with compatible schema and model versions.

### Exercises

1. Repeat the calculation with **the complete repository test suite and synthetic production requests** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

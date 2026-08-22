## Worked calculation — How does user acceptance testing establish implementation correctness?

A statistically valid model can be implemented incorrectly at boundaries, rounding rules, or service transformations.

**Companion case:** `synthetic_retail`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
\Delta_i=implementation_i-reference_i
\]


### Python implementation

```python
reference = {"PD": 0.034821, "score": 612, "grade": "B", "reason": "high_utilisation"}
implementation = {"PD": 0.0348211, "score": 611, "grade": "B", "reason": "high_utilisation"}
tolerance = 1e-6
checks = {
    "PD": abs(reference["PD"] - implementation["PD"]) <= tolerance,
    "score": reference["score"] == implementation["score"],
    "grade": reference["grade"] == implementation["grade"],
    "reason": reference["reason"] == implementation["reason"],
}
print(checks)
print("UAT result:", "PASS" if all(checks.values()) else "FAIL")
```

### Executed result

```output
{'PD': True, 'score': False, 'grade': True, 'reason': True}
UAT result: FAIL
```

### Interpretation

UAT fails because the score reconciliation is false even though PD, grade and reason checks pass. A material failed requirement cannot be averaged away.

**Validation:** Compare reference and production outputs at every intermediate step and retain signed exceptions.

### Exercises

1. Repeat the calculation with **golden synthetic scorecard cases and synthetic IFRS 9 accounts** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

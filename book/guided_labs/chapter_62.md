## Worked calculation — How should batch and real-time scoring preserve the approved calculation?

Different service architectures must produce the same transformations, probability, score, grade, and reasons.

**Companion case:** `synthetic_retail`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
\widehat p_i=f_{version}(x_i)
\]


### Python implementation

```python
REQUEST_FIELDS = {"application_id", "income", "debt_to_income", "model_version"}


def validate_request(request):
    missing = REQUEST_FIELDS - request.keys()
    if missing:
        return {"status": 422, "error": "missing fields", "fields": sorted(missing)}
    if request["income"] < 0 or not 0 <= request["debt_to_income"] <= 2:
        return {"status": 422, "error": "value outside contract"}
    return {"status": 200, "application_id": request["application_id"],
            "model_version": request["model_version"]}


print(validate_request({"application_id": "A-1", "income": 42000,
                        "debt_to_income": 0.31, "model_version": "pd-2.1"}))
print(validate_request({"application_id": "A-2", "income": 42000, "model_version": "pd-2.1"}))
```

### Executed result

```output
{'status': 200, 'application_id': 'A-1', 'model_version': 'pd-2.1'}
{'status': 422, 'error': 'missing fields', 'fields': ['debt_to_income']}
```

### Interpretation

The valid request returns a versioned score response, while the missing debt-to-income field returns status 422. Explicit rejection prevents silent production imputation.

**Validation:** Run golden cases through development and serving paths and compare every intermediate value.

### Exercises

1. Repeat the calculation with **the synthetic retail scorecard and boundary-case requests** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

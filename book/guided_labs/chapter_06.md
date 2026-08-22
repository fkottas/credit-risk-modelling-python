## Worked calculation — How do data, estimation, policy, implementation, and monitoring form one model lifecycle?

A sound estimator can still fail when definitions or transformations change between development and use.

**Companion case:** `synthetic_retail`. **Implementation level:** From first principles: scalar values, lists, and the Python standard library; intermediate quantities remain visible.

### Method

The calculation follows

\[
\text{model output}=g(\text{versioned data},\text{code},\text{policy})
\]


### Python implementation

```python
import hashlib
import json


def reproducible_run_id(data_hash: str, code_hash: str, policy: dict) -> str:
    """Hash canonical evidence; never hash an unordered string representation."""
    payload = {"data_hash": data_hash, "code_hash": code_hash, "policy": policy}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


policy = {"horizon_months": 12, "default_dpd": 90, "version": "1.0"}
run_id = reproducible_run_id("data-9f2a", "code-31bc", policy)
print("Run ID:", run_id)
print("Length:", len(run_id), "hexadecimal:", all(c in "0123456789abcdef" for c in run_id))
```

### Executed result

```output
Run ID: 99553058d99b08b749c617a6329f475bf854e41a7d5f757bbd70a34f277262be
Length: 64 hexadecimal: True
```

### Interpretation

The run identifier contains 64 hexadecimal characters, as expected for SHA-256. It identifies the stated inputs; it does not prove that those inputs or the model are appropriate.

**Validation:** Change one versioned input and confirm that the run identifier and documented output change together.

### Exercises

1. Repeat the calculation with **a synthetic retail run and a synthetic IFRS 9 close** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

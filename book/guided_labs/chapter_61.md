## Worked calculation — What information is needed to reproduce an approved model run?

Coefficients alone omit data, code, configuration, environment, and policy versions.

**Companion case:** `synthetic_retail`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
run\_id=SHA256(data\ hash\Vert code\ hash\Vert config)
\]


### Python implementation

```python
import hashlib
import json


record = {
    "data_sha256": "ab12",
    "code_commit": "c34d",
    "configuration": {"target": "default_12m", "seed": 61},
}
canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
run_id = hashlib.sha256(canonical.encode()).hexdigest()
print("canonical record:", canonical)
print("run identifier:", run_id[:20])
```

### Executed result

```output
canonical record: {"code_commit":"c34d","configuration":{"seed":61,"target":"default_12m"},"data_sha256":"ab12"}
run identifier: eb53fead36caa93b2cac
```

### Interpretation

Canonical serialisation produces one repeatable run identifier from the recorded inputs. Changing field order outside the canonical representation would otherwise create an irrelevant hash difference.

**Validation:** Reproduce the result from a clean environment and verify all recorded hashes.

### Exercises

1. Repeat the calculation with **a synthetic retail scoring run and a synthetic IFRS 9 close** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

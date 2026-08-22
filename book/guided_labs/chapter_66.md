## Worked calculation — How does the model inventory support ownership, change control, and audit?

An inventory connects each model to purpose, data, version, validation, deployment, dependencies, findings, and retirement status.

**Companion case:** `synthetic_retail`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
ChangeHash=SHA256(previous\ hash\Vert change\ record)
\]


### Python implementation

```python
import hashlib
import json


changes = [
    {"version": "1.0", "change": "initial approval", "approver": "committee-A"},
    {"version": "1.1", "change": "calibration update", "approver": "committee-B"},
]
previous = "0" * 64
for change in changes:
    payload = json.dumps(change, sort_keys=True, separators=(",", ":"))
    current = hashlib.sha256((previous + payload).encode()).hexdigest()
    print(change["version"], current[:20])
    previous = current
```

### Executed result

```output
1.0 f72c19052824fe70487a
1.1 1685c7c41f78a2fd0de5
```

### Interpretation

Versions 1.0 and 1.1 have different linked hashes. Verification detects a changed record, while ownership and approval still require independent access and identity controls.

**Validation:** Follow one change from request through testing, approval, implementation, monitoring, and immutable history.

### Exercises

1. Repeat the calculation with **a synthetic model inventory and hash-linked change records** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

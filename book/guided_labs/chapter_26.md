## Worked calculation — How are expert-defined numeric and categorical bins implemented reproducibly?

Manual bins can encode business structure, but boundary and missing-value rules must be explicit.

**Companion case:** `synthetic_retail`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
b(x)=\sum_{j=1}^{J}j\,\mathbf{1}\{c_{j-1}<x\le c_j\}
\]


### Python implementation

```python
from math import inf


EDGES = [-inf, 0.30, 0.60, inf]
LABELS = ["low", "medium", "high"]


def manual_bin(value):
    if value is None:
        return "missing"
    for left, right, label in zip(EDGES[:-1], EDGES[1:], LABELS):
        if left < value <= right:
            return label
    raise ValueError("value was not assigned")


values = [None, 0.10, 0.30, 0.31, 0.60, 0.61]
print(list(zip(values, map(manual_bin, values))))
```

### Executed result

```output
[(None, 'missing'), (0.1, 'low'), (0.3, 'low'), (0.31, 'medium'), (0.6, 'medium'), (0.61, 'high')]
```

### Interpretation

Values exactly equal to 0.30 and 0.60 follow the declared closed-right boundaries, and missing values receive their own label. These cases determine production reproducibility.

**Validation:** Test every cut point, special value, missing value, and unseen category.

### Exercises

1. Repeat the calculation with **synthetic retail data and South German Credit** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

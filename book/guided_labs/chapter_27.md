## Worked calculation — How do automated binning methods balance fit, support, monotonicity, and stability?

Maximising development IV can create small and unstable bins.

**Companion case:** `synthetic_retail`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
\chi^2=\sum_{r=1}^{R}\sum_{c=1}^{C}\frac{(O_{rc}-E_{rc})^2}{E_{rc}}
\]


### Python implementation

```python
import numpy as np
from scipy.stats import chi2_contingency


bins = [
    {"left": 0, "right": 20, "good": 90, "bad": 10},
    {"left": 20, "right": 40, "good": 84, "bad": 16},
    {"left": 40, "right": 60, "good": 60, "bad": 40},
    {"left": 60, "right": 80, "good": 55, "bad": 45},
]


def adjacent_p_value(first, second):
    table = np.array([[first["good"], first["bad"]], [second["good"], second["bad"]]])
    return float(chi2_contingency(table, correction=False).pvalue)


p_values = [adjacent_p_value(bins[i], bins[i + 1]) for i in range(len(bins) - 1)]
merge_at = int(np.argmax(p_values))
merged = {"left": bins[merge_at]["left"], "right": bins[merge_at + 1]["right"],
          "good": bins[merge_at]["good"] + bins[merge_at + 1]["good"],
          "bad": bins[merge_at]["bad"] + bins[merge_at + 1]["bad"]}
print("adjacent p-values:", [round(value, 4) for value in p_values])
print("merge:", merge_at, "and", merge_at + 1, "->", merged)
```

### Executed result

```output
adjacent p-values: [0.2071, 0.0002, 0.4745]
merge: 2 and 3 -> {'left': 40, 'right': 80, 'good': 115, 'bad': 85}
```

### Interpretation

The largest adjacent p-value occurs for bins 2 and 3, so that pair is the next merge under the demonstrated ChiMerge rule. Other objectives can select different merges.

**Validation:** Repeat bin fitting across time and bootstrap samples and compare cut stability.

### Exercises

1. Repeat the calculation with **synthetic retail data and Taiwan credit-card data** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

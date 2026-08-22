## Worked calculation — Which data source is suitable for a particular credit-risk estimand?

Source usefulness depends on observation unit, timing, target meaning, population, and permitted use.

**Companion case:** `dataset_registry.yml`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
x_{i,t}^{PTI}=x_i(\tau\le t)
\]


### Python implementation

```python
import pandas as pd


def source_fit_table() -> pd.DataFrame:
    """Map each empirical question to data that can actually answer it."""
    return pd.DataFrame([
        ("application PD", "UCI Taiwan card", "default outcome, no dates", "benchmark only"),
        ("fair-lending decisions", "HMDA", "application outcomes", "not a PD dataset"),
        ("SME loan performance", "SBA 7(a)/504 FOIA", "loan outcomes", "definitions and vintages required"),
        ("complaint NLP", "CFPB complaints", "narratives and responses", "not underwriting evidence"),
        ("lifetime mortgage", "Fannie/Freddie", "monthly performance", "provider terms; not bundled"),
    ], columns=["question", "candidate_source", "useful_content", "boundary"])


table = source_fit_table()
print(table.to_string(index=False))
```

### Executed result

```output
question  candidate_source            useful_content                          boundary
        application PD   UCI Taiwan card default outcome, no dates                    benchmark only
fair-lending decisions              HMDA      application outcomes                  not a PD dataset
  SME loan performance SBA 7(a)/504 FOIA             loan outcomes definitions and vintages required
         complaint NLP   CFPB complaints  narratives and responses         not underwriting evidence
     lifetime mortgage    Fannie/Freddie       monthly performance       provider terms; not bundled
```

### Interpretation

The suitability table assigns different sources to PD, fairness and macroeconomic questions. It demonstrates that dataset selection begins with the estimand rather than with file availability.

**Validation:** Complete the suitability record before modelling and reject target substitutions such as approval for default.

### Exercises

1. Repeat the calculation with **multiple UCI datasets and the project synthetic cases** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

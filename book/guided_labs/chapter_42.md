## Worked calculation — How are revolving exposure and CCF estimated?

A borrower may draw available credit before default, so current balance alone can understate exposure.

**Companion case:** `synthetic_revolving`. **Implementation level:** Reference implementation: the code evaluates the displayed expression directly and provides expected intermediate values for later library tests.

### Method

The calculation follows

\[
CCF=\frac{EAD-D}{L-D}
\]


### Python implementation

```python
facilities = [
    # drawn at reference, limit at reference, exposure at default
    (4000.0, 10000.0, 7000.0),
    (8000.0, 10000.0, 9500.0),
    (10000.0, 10000.0, 10500.0),
]
for drawn, limit, ead in facilities:
    undrawn = limit - drawn
    ccf = None if undrawn == 0 else (ead - drawn) / undrawn
    print({"drawn": drawn, "undrawn": undrawn, "EAD": ead, "raw_CCF": ccf})
```

### Executed result

```output
{'drawn': 4000.0, 'undrawn': 6000.0, 'EAD': 7000.0, 'raw_CCF': 0.5}
{'drawn': 8000.0, 'undrawn': 2000.0, 'EAD': 9500.0, 'raw_CCF': 0.75}
{'drawn': 10000.0, 'undrawn': 0.0, 'EAD': 10500.0, 'raw_CCF': None}
```

### Interpretation

Facilities with undrawn capacity have defined CCFs of 0.50 and 0.75. The fully drawn account has no valid CCF denominator, although its EAD remains measurable.

**Validation:** Separate zero-undrawn and line-change cases and validate both CCF and currency EAD.

### Exercises

1. Repeat the calculation with **synthetic revolving facilities and student-supplied longitudinal card data** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.

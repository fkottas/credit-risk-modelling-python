## Mathematics-to-code laboratory — construction and controlled promotion

### 1. Start with the decision, observation unit, and estimand

This laboratory does not begin by importing a finished modelling function. The class first states what **Counterparty Exposure, Netting, Collateral, CVA, and SA-CCR** must estimate, which record is one observation, when information becomes available, and which decision or control will consume the result. We begin with `synthetic_counterparty_profiles`. Before calculating anything, inspect the unit of observation, time index, target or outcome field, currency and percentage conventions, licence statement, generator seed or publisher checksum, and limitations. A mathematically correct formula applied to the wrong horizon or population is still a wrong model.

The chapter's principal mathematical object is

\[
CVA\approx(1-RR)\sum_{t=1}^{T}EE_t\,\Delta PD_t\,DF_t
\]

Write every symbol next to its business definition and unit. Conditional probabilities must identify the information set; monetary quantities must identify currency and reference date; rates must distinguish proportions from percentages; and time must identify whether it is calendar, contractual, behavioural or default-workout time. This notation contract becomes the first object in the library rather than an undocumented convention hidden in code.

### 2. Derive before implementing

Reconstruct the expression from elementary operations. Identify the random variable, conditioning information, aggregation rule and any approximation. Then separate estimand, estimator and implementation. The estimand is the population quantity the institution needs. The estimator is the statistical rule learned from available observations. The implementation is a versioned algorithm with finite precision, boundary handling and controls. For every transformation, state which assumptions make it valid and how the result changes if those assumptions fail. This step prevents students from treating a library call as a definition.

For a hand audit, select five records, retain the raw values, and calculate every intermediate column. Reconcile the individual rows to the reported total. Repeat after changing one input while holding the others fixed. The direction need not always be monotonic, but any non-monotonic response must be explained by the mathematics rather than accepted because software returned it. Missing, impossible or temporally unavailable values are reported and quarantined; they are not silently imputed or winsorised.

### 3. Implement the first transparent component

The chapter keeps the estimator visible. Reusable data access may now be imported, while the method being taught is derived, implemented, tested, and reviewed before promotion. Students preserve the source values, expose intermediate quantities, validate boundaries, and print an auditable result. The code below is a construction step, not an illustration of a library that appeared before the course.

```python
from __future__ import annotations

import numpy as np
import pandas as pd

from creditriskbook.data import load_case_dataset


def chapter_54_audit_table(seed: int = 854) -> pd.DataFrame:
    """Return hand-auditable summaries; never impute or winsorise silently."""
    bundle = load_case_dataset("synthetic_counterparty_profiles", n_rows=500, seed=seed)
    frame = bundle.frame.copy(deep=True)
    numeric = frame.select_dtypes(include="number")
    if numeric.empty:
        raise ValueError("The chapter requires at least one numeric field")
    rows = []
    for column in numeric.columns[:8]:
        observed = numeric[column].dropna()
        rows.append({
            "variable": column,
            "n": int(observed.size),
            "missing": int(numeric[column].isna().sum()),
            "mean": float(observed.mean()),
            "std": float(observed.std(ddof=1)),
            "p05": float(observed.quantile(0.05)),
            "p50": float(observed.quantile(0.50)),
            "p95": float(observed.quantile(0.95)),
        })
    result = pd.DataFrame(rows)
    assert result["n"].gt(0).all()
    assert result[["mean", "p05", "p50", "p95"]].notna().all().all()
    return result


audit = chapter_54_audit_table()
print(audit.to_string(index=False))
```

### 4. Inspect the executed output

The output below is produced by the displayed code during the book build. Recalculate at least one row manually before accepting it. A student submission must retain both code and output; an unexplained screenshot is not reproducible evidence.

```output
variable    n  missing         mean          std          p05           p50          p95
    horizon_years 2630        0 9.083650e-01 9.304792e-01     0.000000      0.500000 3.000000e+00
expected_exposure 2630        0 3.151909e+04 1.563716e+05     0.000000      0.000000 1.846417e+05
          pfe_975 2630        0 7.416774e+04 2.903557e+05     0.000000      0.000000 3.907968e+05
       collateral 2630        0 1.034572e+06 1.733680e+06 30695.300500 510105.810000 3.178539e+06
  counterparty_pd 2630        0 3.796381e-02 2.294698e-02     0.004278      0.034908 7.656385e-02
 counterparty_lgd 2630        0 4.954913e-01 8.741916e-02     0.362917      0.497152 6.343590e-01
```

### 5. Test mathematics, data, and policy separately

Add three kinds of tests. A mathematical invariant checks an identity, bound or reconciliation implied by the formula. A data test checks schema, units, missingness, dates, duplicates, permitted categories and source identity. A policy test checks that the calculation is not silently converted into authority it does not possess. Use at least one ordinary case, one boundary case, one missing-value case, one temporally invalid case and one deliberately corrupted case. Record expected outputs before running the implementation so that the test is not merely a copy of the code.

### 6. Extend, compare datasets, and document

After the simple component is understood, replace the audit statistic with the full chapter method, retaining the same input contract and evidence fields. Compare the result across at least two compatible datasets or across synthetic segments. Explain differences using population, product, horizon and data-generation mechanisms rather than only performance metrics. The student deliverable is a source module, tests, a notebook, a characteristic or parameter table, a short validation note and an explicit statement of what the component is not allowed to decide. This staged build is how the final scorecard, IFRS 9, IRB and governed-agent libraries emerge during the book.

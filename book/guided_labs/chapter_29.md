## Mathematics-to-code laboratory — construction and controlled promotion

### 1. Start with the decision, observation unit, and estimand

This laboratory does not begin by importing a finished modelling function. The class first states what **Logistic Regression by Maximum Likelihood and IRLS** must estimate, which record is one observation, when information becomes available, and which decision or control will consume the result. We begin with `synthetic_retail`. Before calculating anything, inspect the unit of observation, time index, target or outcome field, currency and percentage conventions, licence statement, generator seed or publisher checksum, and limitations. A mathematically correct formula applied to the wrong horizon or population is still a wrong model.

The chapter's principal mathematical object is

\[
\beta^{(k+1)}=\beta^{(k)}+\left(\frac{X^\top W^{(k)}X}{n}+\Lambda\right)^{-1}\left[\frac{X^\top(y-p^{(k)})}{n}-\Lambda\beta^{(k)}\right]
\]

Write every symbol next to its business definition and unit. Conditional probabilities must identify the information set; monetary quantities must identify currency and reference date; rates must distinguish proportions from percentages; and time must identify whether it is calendar, contractual, behavioural or default-workout time. This notation contract becomes the first object in the library rather than an undocumented convention hidden in code.

### 2. Derive before implementing

Reconstruct the expression from elementary operations. Identify the random variable, conditioning information, aggregation rule and any approximation. Then separate estimand, estimator and implementation. The estimand is the population quantity the institution needs. The estimator is the statistical rule learned from available observations. The implementation is a versioned algorithm with finite precision, boundary handling and controls. For every transformation, state which assumptions make it valid and how the result changes if those assumptions fail. This step prevents students from treating a library call as a definition.

For a hand audit, select five records, retain the raw values, and calculate every intermediate column. Reconcile the individual rows to the reported total. Repeat after changing one input while holding the others fixed. The direction need not always be monotonic, but any non-monotonic response must be explained by the mathematics rather than accepted because software returned it. Missing, impossible or temporally unavailable values are reported and quarantined; they are not silently imputed or winsorised.

![Figure 29.1 — Original teaching visual generated from repository data.](book/figures/irls-objective-convergence.png)

### 3. Implement the first transparent component

The chapter keeps the estimator visible. Reusable data access may now be imported, while the method being taught is derived, implemented, tested, and reviewed before promotion. Students preserve the source values, expose intermediate quantities, validate boundaries, and print an auditable result. The code below is a construction step, not an illustration of a library that appeared before the course.

```python
from __future__ import annotations

import numpy as np
import pandas as pd

from creditriskbook.data import load_dataset


def chapter_29_audit_table(seed: int = 829) -> pd.DataFrame:
    """Return hand-auditable summaries; never impute or winsorise silently."""
    bundle = load_dataset("synthetic_retail", n_rows=1_500, seed=seed)
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


audit = chapter_29_audit_table()
print(audit.to_string(index=False))
```

### 4. Inspect the executed output

The output below is produced by the displayed code during the book build. Recalculate at least one row manually before accepting it. A student submission must retain both code and output; an unexplained screenshot is not reproducible evidence.

```output
variable    n  missing         mean          std          p05         p50          p95
                 age 1500        0    42.953333    12.060796    22.000000    43.00000    62.000000
              income 1500        0 43720.666553 26154.671791 15257.328500 37670.16500 93820.472000
    employment_years 1500        0     6.516907     4.572907     0.988500     5.52500    15.391000
      debt_to_income 1500        0     0.419960     0.218841     0.106600     0.39710     0.828300
         utilisation 1500        0     0.438037     0.207646     0.109195     0.43335     0.784245
credit_history_years 1500        0     7.178827     4.793655     1.109500     6.23500    16.371000
        enquiries_6m 1500        0     1.359333     1.147355     0.000000     1.00000     3.000000
         loan_amount 1500        0  8784.118967  8476.973100   411.239000  6908.62500 24593.646000
```

### 5. Test mathematics, data, and policy separately

Add three kinds of tests. A mathematical invariant checks an identity, bound or reconciliation implied by the formula. A data test checks schema, units, missingness, dates, duplicates, permitted categories and source identity. A policy test checks that the calculation is not silently converted into authority it does not possess. Use at least one ordinary case, one boundary case, one missing-value case, one temporally invalid case and one deliberately corrupted case. Record expected outputs before running the implementation so that the test is not merely a copy of the code.

### 6. Extend, compare datasets, and document

After the simple component is understood, replace the audit statistic with the full chapter method, retaining the same input contract and evidence fields. Compare the result across at least two compatible datasets or across synthetic segments. Explain differences using population, product, horizon and data-generation mechanisms rather than only performance metrics. The student deliverable is a source module, tests, a notebook, a characteristic or parameter table, a short validation note and an explicit statement of what the component is not allowed to decide. This staged build is how the final scorecard, IFRS 9, IRB and governed-agent libraries emerge during the book.

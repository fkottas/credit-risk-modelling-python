## Mathematics-to-code laboratory — standalone construction: no project-library imports

### 1. Start with the decision, observation unit, and estimand

This laboratory does not begin by importing a finished modelling function. The class first states what **IFRS 9 Impairment, Staging, and Significant Increase in Credit Risk** must estimate, which record is one observation, when information becomes available, and which decision or control will consume the result. We begin with an original miniature fixture whose values are visible in the Python window. The extension exercise then repeats the calculation on `synthetic_retail`. Before calculating anything, inspect the unit of observation, time index, target or outcome field, currency and percentage conventions, licence statement, generator seed or publisher checksum, and limitations. A mathematically correct formula applied to the wrong horizon or population is still a wrong model.

The chapter's principal mathematical object is

\[
ECL=\sum_{s=1}^{S} w_s\sum_{t=1}^{T} MPD_{s,t}LGD_{s,t}EAD_{s,t}DF_t
\]

Write every symbol next to its business definition and unit. Conditional probabilities must identify the information set; monetary quantities must identify currency and reference date; rates must distinguish proportions from percentages; and time must identify whether it is calendar, contractual, behavioural or default-workout time. This notation contract becomes the first object in the library rather than an undocumented convention hidden in code.

### 2. Derive before implementing

Reconstruct the expression from elementary operations. Identify the random variable, conditioning information, aggregation rule and any approximation. Then separate estimand, estimator and implementation. The estimand is the population quantity the institution needs. The estimator is the statistical rule learned from available observations. The implementation is a versioned algorithm with finite precision, boundary handling and controls. For every transformation, state which assumptions make it valid and how the result changes if those assumptions fail. This step prevents students from treating a library call as a definition.

For a hand audit, select five records, retain the raw values, and calculate every intermediate column. Reconcile the individual rows to the reported total. Repeat after changing one input while holding the others fixed. The direction need not always be monotonic, but any non-monotonic response must be explained by the mathematics rather than accepted because software returned it. Missing, impossible or temporally unavailable values are reported and quarantined; they are not silently imputed or winsorised.

### 3. Implement the first transparent component

The complete calculation is written in the chapter. It may import Python, NumPy, or pandas, but it must not import `creditriskbook`. This is enforced by the pedagogy audit. Students preserve the source values, expose intermediate quantities, validate boundaries, and print an auditable result. The code below is a construction step, not an illustration of a library that appeared before the course.

```python
import pandas as pd


def assign_ifrs9_stage(origination_pd, current_pd, dpd, watchlist, default):
    if default or dpd >= 90:
        return 3, "credit_impaired_or_default"
    pd_ratio = current_pd / origination_pd if origination_pd > 0 else float("inf")
    if dpd >= 30 or watchlist or pd_ratio >= 2.0:
        return 2, "significant_increase_in_credit_risk"
    return 1, "performing_without_sicr"


accounts = pd.DataFrame({
    "account": ["A", "B", "C"], "orig_pd": [0.02, 0.02, 0.03],
    "current_pd": [0.025, 0.055, 0.30], "dpd": [0, 35, 95],
    "watchlist": [False, False, True], "default": [False, False, True],
})
accounts[["stage", "reason"]] = accounts.apply(
    lambda r: pd.Series(assign_ifrs9_stage(r.orig_pd, r.current_pd, r.dpd, r.watchlist, r.default)), axis=1
)
print(accounts[["account", "stage", "reason"]].to_string(index=False))
```

### 4. Inspect the executed output

The output below is produced by the displayed code during the book build. Recalculate at least one row manually before accepting it. A student submission must retain both code and output; an unexplained screenshot is not reproducible evidence.

```output
account  stage                              reason
      A      1             performing_without_sicr
      B      2 significant_increase_in_credit_risk
      C      3          credit_impaired_or_default
```

### 5. Test mathematics, data, and policy separately

Add three kinds of tests. A mathematical invariant checks an identity, bound or reconciliation implied by the formula. A data test checks schema, units, missingness, dates, duplicates, permitted categories and source identity. A policy test checks that the calculation is not silently converted into authority it does not possess. Use at least one ordinary case, one boundary case, one missing-value case, one temporally invalid case and one deliberately corrupted case. Record expected outputs before running the implementation so that the test is not merely a copy of the code.

### 6. Extend, compare datasets, and document

After the simple component is understood, replace the audit statistic with the full chapter method, retaining the same input contract and evidence fields. Compare the result across at least two compatible datasets or across synthetic segments. Explain differences using population, product, horizon and data-generation mechanisms rather than only performance metrics. The student deliverable is a source module, tests, a notebook, a characteristic or parameter table, a short validation note and an explicit statement of what the component is not allowed to decide. This staged build is how the final scorecard, IFRS 9, IRB and governed-agent libraries emerge during the book.

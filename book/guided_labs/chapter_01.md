## Mathematics-to-code laboratory — standalone construction: no project-library imports

### 1. Start with the decision, observation unit, and estimand

This laboratory does not begin by importing a finished modelling function. The class first states what **Credit Risk as Uncertain Cash Flows** must estimate, which record is one observation, when information becomes available, and which decision or control will consume the result. We begin with an original miniature fixture whose values are visible in the Python window. The extension exercise then repeats the calculation on `synthetic_retail`. Before calculating anything, inspect the unit of observation, time index, target or outcome field, currency and percentage conventions, licence statement, generator seed or publisher checksum, and limitations. A mathematically correct formula applied to the wrong horizon or population is still a wrong model.

The chapter's principal mathematical object is

\[
L=\sum_{t=1}^{T}d_t(C_t-R_t+K_t)
\]

Write every symbol next to its business definition and unit. Conditional probabilities must identify the information set; monetary quantities must identify currency and reference date; rates must distinguish proportions from percentages; and time must identify whether it is calendar, contractual, behavioural or default-workout time. This notation contract becomes the first object in the library rather than an undocumented convention hidden in code.

### 2. Derive before implementing

Reconstruct the expression from elementary operations. Identify the random variable, conditioning information, aggregation rule and any approximation. Then separate estimand, estimator and implementation. The estimand is the population quantity the institution needs. The estimator is the statistical rule learned from available observations. The implementation is a versioned algorithm with finite precision, boundary handling and controls. For every transformation, state which assumptions make it valid and how the result changes if those assumptions fail. This step prevents students from treating a library call as a definition.

For a hand audit, select five records, retain the raw values, and calculate every intermediate column. Reconcile the individual rows to the reported total. Repeat after changing one input while holding the others fixed. The direction need not always be monotonic, but any non-monotonic response must be explained by the mathematics rather than accepted because software returned it. Missing, impossible or temporally unavailable values are reported and quarantined; they are not silently imputed or winsorised.

![Figure 1.1 — Original teaching visual generated from repository data.](book/figures/part-01-loss-distribution.png)

### 3. Implement the first transparent component

The complete calculation is written in the chapter. It may import Python, NumPy, or pandas, but it must not import `creditriskbook`. This is enforced by the pedagogy audit. Students preserve the source values, expose intermediate quantities, validate boundaries, and print an auditable result. The code below is a construction step, not an illustration of a library that appeared before the course.

```python
import pandas as pd


def discounted_cash_shortfall(schedule: pd.DataFrame) -> pd.DataFrame:
    """Calculate period and present-value loss without hiding intermediates."""
    required = {"month", "contractual", "received", "recovery", "workout_cost", "eir"}
    missing = required - set(schedule)
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")
    out = schedule.copy(deep=True)
    out["cash_shortfall"] = (
        out["contractual"] - out["received"] - out["recovery"] + out["workout_cost"]
    )
    out["discount_factor"] = (1.0 + out["eir"]) ** (-out["month"] / 12.0)
    out["pv_loss"] = out["cash_shortfall"] * out["discount_factor"]
    return out


cashflows = pd.DataFrame({
    "month": [1, 2, 3], "contractual": [350.0, 350.0, 350.0],
    "received": [350.0, 200.0, 0.0], "recovery": [0.0, 0.0, 120.0],
    "workout_cost": [0.0, 5.0, 15.0], "eir": [0.12, 0.12, 0.12],
})
audit = discounted_cash_shortfall(cashflows)
print(audit[["month", "cash_shortfall", "discount_factor", "pv_loss"]].round(2).to_string(index=False))
print("Total PV loss:", round(audit["pv_loss"].sum(), 2))
```

### 4. Inspect the executed output

The output below is produced by the displayed code during the book build. Recalculate at least one row manually before accepting it. A student submission must retain both code and output; an unexplained screenshot is not reproducible evidence.

```output
month  cash_shortfall  discount_factor  pv_loss
     1             0.0             0.99     0.00
     2           155.0             0.98   152.10
     3           245.0             0.97   238.16
Total PV loss: 390.26
```

### 5. Test mathematics, data, and policy separately

Add three kinds of tests. A mathematical invariant checks an identity, bound or reconciliation implied by the formula. A data test checks schema, units, missingness, dates, duplicates, permitted categories and source identity. A policy test checks that the calculation is not silently converted into authority it does not possess. Use at least one ordinary case, one boundary case, one missing-value case, one temporally invalid case and one deliberately corrupted case. Record expected outputs before running the implementation so that the test is not merely a copy of the code.

### 6. Extend, compare datasets, and document

After the simple component is understood, replace the audit statistic with the full chapter method, retaining the same input contract and evidence fields. Compare the result across at least two compatible datasets or across synthetic segments. Explain differences using population, product, horizon and data-generation mechanisms rather than only performance metrics. The student deliverable is a source module, tests, a notebook, a characteristic or parameter table, a short validation note and an explicit statement of what the component is not allowed to decide. This staged build is how the final scorecard, IFRS 9, IRB and governed-agent libraries emerge during the book.

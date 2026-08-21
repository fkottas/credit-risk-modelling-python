## Mathematics-to-code laboratory — standalone construction: no project-library imports

### 1. Start with the decision, observation unit, and estimand

This laboratory does not begin by importing a finished modelling function. The class first states what **Time, Cohorts, Transitions, and Competing Events** must estimate, which record is one observation, when information becomes available, and which decision or control will consume the result. We begin with an original miniature fixture whose values are visible in the Python window. The extension exercise then repeats the calculation on `synthetic_retail`. Before calculating anything, inspect the unit of observation, time index, target or outcome field, currency and percentage conventions, licence statement, generator seed or publisher checksum, and limitations. A mathematically correct formula applied to the wrong horizon or population is still a wrong model.

The chapter's principal mathematical object is

\[
P_{ij}(h)=\Pr(S_{t+h}=j\mid S_t=i)
\]

Write every symbol next to its business definition and unit. Conditional probabilities must identify the information set; monetary quantities must identify currency and reference date; rates must distinguish proportions from percentages; and time must identify whether it is calendar, contractual, behavioural or default-workout time. This notation contract becomes the first object in the library rather than an undocumented convention hidden in code.

### 2. Derive before implementing

Reconstruct the expression from elementary operations. Identify the random variable, conditioning information, aggregation rule and any approximation. Then separate estimand, estimator and implementation. The estimand is the population quantity the institution needs. The estimator is the statistical rule learned from available observations. The implementation is a versioned algorithm with finite precision, boundary handling and controls. For every transformation, state which assumptions make it valid and how the result changes if those assumptions fail. This step prevents students from treating a library call as a definition.

For a hand audit, select five records, retain the raw values, and calculate every intermediate column. Reconcile the individual rows to the reported total. Repeat after changing one input while holding the others fixed. The direction need not always be monotonic, but any non-monotonic response must be explained by the mathematics rather than accepted because software returned it. Missing, impossible or temporally unavailable values are reported and quarantined; they are not silently imputed or winsorised.

### 3. Implement the first transparent component

The complete calculation is written in the chapter. It may import Python, NumPy, or pandas, but it must not import `creditriskbook`. This is enforced by the pedagogy audit. Students preserve the source values, expose intermediate quantities, validate boundaries, and print an auditable result. The code below is a construction step, not an illustration of a library that appeared before the course.

```python
import pandas as pd


def transition_matrix(history: pd.DataFrame) -> pd.DataFrame:
    """Estimate one-step transition probabilities from adjacent observed states."""
    ordered = history.sort_values(["account_id", "month"]).copy()
    ordered["next_state"] = ordered.groupby("account_id")["state"].shift(-1)
    pairs = ordered.dropna(subset=["next_state"])
    counts = pd.crosstab(pairs["state"], pairs["next_state"])
    return counts.div(counts.sum(axis=1), axis=0).fillna(0.0)


history = pd.DataFrame({
    "account_id": ["A"] * 4 + ["B"] * 4 + ["C"] * 4,
    "month": [1, 2, 3, 4] * 3,
    "state": ["C", "C", "30", "60", "C", "30", "C", "C", "C", "C", "P", "P"],
})
matrix = transition_matrix(history)
print(matrix.round(3).to_string())
print("Rows reconcile:", matrix.sum(axis=1).round(8).eq(1).all())
```

### 4. Inspect the executed output

The output below is produced by the displayed code during the book build. Recalculate at least one row manually before accepting it. A student submission must retain both code and output; an unexplained screenshot is not reproducible evidence.

```output
next_state     30   60    C      P
state
30          0.000  0.5  0.5  0.000
C           0.333  0.0  0.5  0.167
P           0.000  0.0  0.0  1.000
Rows reconcile: True
```

### 5. Test mathematics, data, and policy separately

Add three kinds of tests. A mathematical invariant checks an identity, bound or reconciliation implied by the formula. A data test checks schema, units, missingness, dates, duplicates, permitted categories and source identity. A policy test checks that the calculation is not silently converted into authority it does not possess. Use at least one ordinary case, one boundary case, one missing-value case, one temporally invalid case and one deliberately corrupted case. Record expected outputs before running the implementation so that the test is not merely a copy of the code.

### 6. Extend, compare datasets, and document

After the simple component is understood, replace the audit statistic with the full chapter method, retaining the same input contract and evidence fields. Compare the result across at least two compatible datasets or across synthetic segments. Explain differences using population, product, horizon and data-generation mechanisms rather than only performance metrics. The student deliverable is a source module, tests, a notebook, a characteristic or parameter table, a short validation note and an explicit statement of what the component is not allowed to decide. This staged build is how the final scorecard, IFRS 9, IRB and governed-agent libraries emerge during the book.

## Mathematics-to-code laboratory — standalone construction: no project-library imports

### 1. Start with the decision, observation unit, and estimand

This laboratory does not begin by importing a finished modelling function. The class first states what **Expected Loss, Unexpected Loss, and the Loss Distribution** must estimate, which record is one observation, when information becomes available, and which decision or control will consume the result. We begin with an original miniature fixture whose values are visible in the Python window. The extension exercise then repeats the calculation on `synthetic_retail`. Before calculating anything, inspect the unit of observation, time index, target or outcome field, currency and percentage conventions, licence statement, generator seed or publisher checksum, and limitations. A mathematically correct formula applied to the wrong horizon or population is still a wrong model.

The chapter's principal mathematical object is

\[
EL=\mathbb{E}[L],\quad UL_\alpha=Q_\alpha(L)-EL
\]

Write every symbol next to its business definition and unit. Conditional probabilities must identify the information set; monetary quantities must identify currency and reference date; rates must distinguish proportions from percentages; and time must identify whether it is calendar, contractual, behavioural or default-workout time. This notation contract becomes the first object in the library rather than an undocumented convention hidden in code.

### 2. Derive before implementing

Reconstruct the expression from elementary operations. Identify the random variable, conditioning information, aggregation rule and any approximation. Then separate estimand, estimator and implementation. The estimand is the population quantity the institution needs. The estimator is the statistical rule learned from available observations. The implementation is a versioned algorithm with finite precision, boundary handling and controls. For every transformation, state which assumptions make it valid and how the result changes if those assumptions fail. This step prevents students from treating a library call as a definition.

For a hand audit, select five records, retain the raw values, and calculate every intermediate column. Reconcile the individual rows to the reported total. Repeat after changing one input while holding the others fixed. The direction need not always be monotonic, but any non-monotonic response must be explained by the mathematics rather than accepted because software returned it. Missing, impossible or temporally unavailable values are reported and quarantined; they are not silently imputed or winsorised.

### 3. Implement the first transparent component

The complete calculation is written in the chapter. It may import Python, NumPy, or pandas, but it must not import `creditriskbook`. This is enforced by the pedagogy audit. Students preserve the source values, expose intermediate quantities, validate boundaries, and print an auditable result. The code below is a construction step, not an illustration of a library that appeared before the course.

```python
import numpy as np


def loss_distribution(pd, lgd, ead, *, simulations=20_000, seed=802):
    """Simulate Bernoulli defaults and expose EL, quantile loss, and unexpected loss."""
    pd, lgd, ead = map(lambda x: np.asarray(x, dtype=float), (pd, lgd, ead))
    if not (pd.shape == lgd.shape == ead.shape):
        raise ValueError("PD, LGD, and EAD must have the same shape")
    if np.any((pd < 0) | (pd > 1)) or np.any((lgd < 0) | (lgd > 1)):
        raise ValueError("PD and LGD must be proportions")
    rng = np.random.default_rng(seed)
    defaults = rng.random((simulations, len(pd))) < pd
    simulated = (defaults * lgd * ead).sum(axis=1)
    analytical_el = float(np.sum(pd * lgd * ead))
    q99 = float(np.quantile(simulated, 0.99, method="higher"))
    return {"analytical_el": analytical_el, "simulated_mean": simulated.mean(),
            "q99": q99, "unexpected_loss_99": q99 - analytical_el}


result = loss_distribution([0.02, 0.05, 0.10], [0.35, 0.45, 0.60], [10_000, 8_000, 5_000])
print({key: round(value, 2) for key, value in result.items()})
```

### 4. Inspect the executed output

The output below is produced by the displayed code during the book build. Recalculate at least one row manually before accepting it. A student submission must retain both code and output; an unexplained screenshot is not reproducible evidence.

```output
{'analytical_el': 550.0, 'simulated_mean': np.float64(567.68), 'q99': 3600.0, 'unexpected_loss_99': 3050.0}
```

### 5. Test mathematics, data, and policy separately

Add three kinds of tests. A mathematical invariant checks an identity, bound or reconciliation implied by the formula. A data test checks schema, units, missingness, dates, duplicates, permitted categories and source identity. A policy test checks that the calculation is not silently converted into authority it does not possess. Use at least one ordinary case, one boundary case, one missing-value case, one temporally invalid case and one deliberately corrupted case. Record expected outputs before running the implementation so that the test is not merely a copy of the code.

### 6. Extend, compare datasets, and document

After the simple component is understood, replace the audit statistic with the full chapter method, retaining the same input contract and evidence fields. Compare the result across at least two compatible datasets or across synthetic segments. Explain differences using population, product, horizon and data-generation mechanisms rather than only performance metrics. The student deliverable is a source module, tests, a notebook, a characteristic or parameter table, a short validation note and an explicit statement of what the component is not allowed to decide. This staged build is how the final scorecard, IFRS 9, IRB and governed-agent libraries emerge during the book.

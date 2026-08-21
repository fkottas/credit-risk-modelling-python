## Mathematics-to-code laboratory — foundational arithmetic in plain Python

### 1. Start with the decision, observation unit, and estimand

This laboratory does not begin by importing a finished modelling function. The class first states what **Expected Loss, Unexpected Loss, and the Loss Distribution** must estimate, which record is one observation, when information becomes available, and which decision or control will consume the result. We begin with a deliberately tiny, hand-checkable fixture whose values are visible in the Python window. The extension exercise then repeats the calculation on `synthetic_retail`. Before calculating anything, inspect the unit of observation, time index, target or outcome field, currency and percentage conventions, licence statement, generator seed or publisher checksum, and limitations. A mathematically correct formula applied to the wrong horizon or population is still a wrong model.

The chapter's principal mathematical object is

\[
EL=\mathbb{E}[L],\quad UL_\alpha=Q_\alpha(L)-EL
\]

Write every symbol next to its business definition and unit. Conditional probabilities must identify the information set; monetary quantities must identify currency and reference date; rates must distinguish proportions from percentages; and time must identify whether it is calendar, contractual, behavioural or default-workout time. This notation contract becomes the first object in the library rather than an undocumented convention hidden in code.

### 2. Derive before implementing

Reconstruct the expression from elementary operations. Identify the random variable, conditioning information, aggregation rule and any approximation. Then separate estimand, estimator and implementation. The estimand is the population quantity the institution needs. The estimator is the statistical rule learned from available observations. The implementation is a versioned algorithm with finite precision, boundary handling and controls. For every transformation, state which assumptions make it valid and how the result changes if those assumptions fail. This step prevents students from treating a library call as a definition.

For a hand audit, select five records, retain the raw values, and calculate every intermediate column. Reconcile the individual rows to the reported total. Repeat after changing one input while holding the others fixed. The direction need not always be monotonic, but any non-monotonic response must be explained by the mathematics rather than accepted because software returned it. Missing, impossible or temporally unavailable values are reported and quarantined; they are not silently imputed or winsorised.

### 3. Implement the first transparent component

The first six chapters use scalar arithmetic, lists, loops, and only Python's standard library. NumPy, pandas, modelling packages, and `creditriskbook` are intentionally absent so that every intermediate value can be checked by hand. Students preserve the source values, expose intermediate quantities, validate boundaries, and print an auditable result. The code below is a construction step, not an illustration of a library that appeared before the course.

```python
from itertools import product

pd = [0.10, 0.20]
loss_if_default = [500.0, 800.0]  # LGD times EAD
distribution = []

for defaults in product((0, 1), repeat=2):
    probability = 1.0
    loss = 0.0
    for default, probability_of_default, amount in zip(
        defaults, pd, loss_if_default, strict=True
    ):
        probability *= probability_of_default if default else 1.0 - probability_of_default
        loss += default * amount
    distribution.append((loss, probability, defaults))

expected_loss = sum(loss * probability for loss, probability, _ in distribution)
cumulative_probability = 0.0
loss_quantile_95 = None
for loss, probability, defaults in sorted(distribution):
    cumulative_probability += probability
    print(defaults, "loss=", loss, "probability=", round(probability, 3))
    if loss_quantile_95 is None and cumulative_probability >= 0.95:
        loss_quantile_95 = loss

print("Expected loss:", expected_loss)
print("95% loss quantile:", loss_quantile_95)
print("Unexpected loss at 95%:", loss_quantile_95 - expected_loss)
```

### 4. Inspect the executed output

The output below is produced by the displayed code during the book build. Recalculate at least one row manually before accepting it. A student submission must retain both code and output; an unexplained screenshot is not reproducible evidence.

```output
(0, 0) loss= 0.0 probability= 0.72
(1, 0) loss= 500.0 probability= 0.08
(0, 1) loss= 800.0 probability= 0.18
(1, 1) loss= 1300.0 probability= 0.02
Expected loss: 210.00000000000003
95% loss quantile: 800.0
Unexpected loss at 95%: 590.0
```

### 5. Test mathematics, data, and policy separately

Add three kinds of tests. A mathematical invariant checks an identity, bound or reconciliation implied by the formula. A data test checks schema, units, missingness, dates, duplicates, permitted categories and source identity. A policy test checks that the calculation is not silently converted into authority it does not possess. Use at least one ordinary case, one boundary case, one missing-value case, one temporally invalid case and one deliberately corrupted case. Record expected outputs before running the implementation so that the test is not merely a copy of the code.

### 6. Extend, compare datasets, and document

After the simple component is understood, replace the audit statistic with the full chapter method, retaining the same input contract and evidence fields. Compare the result across at least two compatible datasets or across synthetic segments. Explain differences using population, product, horizon and data-generation mechanisms rather than only performance metrics. The student deliverable is a source module, tests, a notebook, a characteristic or parameter table, a short validation note and an explicit statement of what the component is not allowed to decide. This staged build is how the final scorecard, IFRS 9, IRB and governed-agent libraries emerge during the book.

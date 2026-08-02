# Chapter 5 — From-Scratch Binning, WOE and Characteristic Analysis

## Why bin at all?

Binning replaces a raw variable with intervals or category groups. It can reveal nonlinear risk, isolate missingness, reduce sensitivity to tails and yield a stable, reviewable scorecard. It also throws away information and can manufacture attractive patterns. Binning is a modelling decision that must be estimated on development data, challenged out of time and frozen for production.

The project implements its own binning rather than calling a scorecard library. `NumericBinner` supports quantile, equal-width, ChiMerge and monotonic methods. `manual_numeric_spec` records expert cut points. `CategoricalBinner` orders categories by event rate, separates rare categories and forms deterministic groups. Missing and special values are explicit bins. `BinningProcess` stores one contract and applies it identically at scoring time.

## Manual numeric and categorical bins

Manual bins are appropriate when policy, measurement, affordability or clear economic thresholds matter. They are also the easiest to misuse by searching the outcome repeatedly. A manual decision log should show the original distribution, proposed cut points, event rates, sample sizes, rationale, sensitivity and approver.

```python
from creditriskbook.scorecard import manual_categorical_spec, manual_numeric_spec

manual = {
    "enquiries_6m": manual_numeric_spec("enquiries_6m", [0, 1, 3, 6]),
    "product": manual_categorical_spec(
        "product",
        [["personal_loan"], ["credit_card"], ["bnpl"]],
    ),
}
```

Numeric cut points are converted into `(-inf, c1] ... (ck, inf]`. The exact closed side is part of the contract. Special values such as `-999` are handled before regular intervals; missing has its own label. Categories not seen in training map to `__OTHER__`, never to an arbitrary observed bin.

## Quantile and equal-width pre-bins

Quantile bins aim for similar counts. They are useful when variables are skewed, but repeated values can collapse cut points. Equal-width bins preserve numerical distance but can leave almost empty tails. Both are unsupervised: they do not use the target. The implementation calculates unique internal cut points and always adds infinite endpoints.

Supervised methods begin with more pre-bins than the final maximum. Pre-binning limits computation and reduces single-value overfit. Every pre-bin must still be inspected; if a variable has only a few values, it should usually be treated as ordered categorical rather than pretending to be continuous.

## ChiMerge from first principles

ChiMerge starts with adjacent numeric intervals. For each neighbouring pair, it constructs a two-by-two table of good and bad counts and calculates Pearson's chi-square statistic. The pair with the smallest evidence of different event composition is merged. This repeats until the maximum bin count is reached.

The repository computes the statistic directly:

`χ² = Σ (observed − expected)² / expected`.

It does not rely on a scorecard package. Before ChiMerge, bins violating minimum fraction, minimum events or minimum non-events are merged with the adjacent interval having the closest bad rate. These constraints reduce infinite or unstable WOE. They do not guarantee stability: a minimum of five events can still be far too small for a material model.

ChiMerge is greedy. It does not globally optimise predictive power and can produce non-monotonic risk. Its result depends on pre-bins, sample and constraints. Compare multiple configurations and out-of-time behaviour, not only development IV.

## Monotonic merging

For variables expected to have ordered risk, the monotonic method fits ChiMerge bins, chooses an increasing or decreasing direction from the empirical trend when `auto` is requested, then merges adjacent violations. The closest violation is merged first until the sequence is monotonic or only two bins remain.

Automatic monotonicity can hide U-shaped risk. Age, income, account tenure and utilisation can have genuine non-monotonic relationships. The modeller should choose monotonicity because of economic expectation, data support and operational robustness—not because the resulting plot is easy to present.

```python
from creditriskbook.scorecard import BinningProcess

binning = BinningProcess(
    numeric_method="monotonic",
    max_bins=6,
    prebins=20,
    min_bin_fraction=0.05,
    min_events=5,
    manual_specs=manual,
)
binned_train = binning.fit_transform(X_train, y_train)
binned_test = binning.transform(X_test)
```

The fit/transform split is a leakage control. Re-estimating test bins answers a different question and can make a deteriorating feature look stable.

## Weight of evidence

With event coded 1, this book defines

`WOE_j = ln(distribution_good_j / distribution_bad_j)`.

A positive WOE is safer than the portfolio average; a negative WOE is riskier. Some organisations use the opposite convention. Either is valid if coefficients, points and documentation are consistent. State the convention in every report.

Zero good or bad counts create infinite WOE. The encoder adds a positive smoothing amount to each bin before normalising class distributions. With smoothing `s` and `K` observed bins,

`dist_good_j = (good_j + s) / (total_good + sK)`

and similarly for bad. Smoothing stabilises arithmetic but does not create evidence. A zero-event bin remains a warning about sparse data.

Information value is

`IV = Σ (dist_good_j − dist_bad_j) × WOE_j`.

IV is an in-sample separation measure, not a universal variable-selection law. High IV can signal leakage, tiny bins, sampling artefacts or a policy variable that will change when the model is deployed. Threshold labels such as “weak” and “strong” should never replace stability and business review.

## Characteristic analysis

A characteristic table needs more than WOE. The project exports feature, bin label, count, event and non-event distributions, bad rate, WOE, IV contribution, fitted coefficient and score points. The summary reports bin count, total observations, IV, event-rate range and point range. HTML and CSV outputs are generated without proprietary tooling.

```python
from creditriskbook.scorecard import export_characteristic_report

paths = export_characteristic_report(scorecard, "artifacts/characteristic_report")
```

Review each characteristic across development, validation and out-of-time samples. Add population share, missing share, event count, bad-rate confidence interval and PSI by bin. A characteristic is acceptable when its pattern is plausible, supported, stable, implementable and non-prohibited—not because the chart is smooth.

## Student investigations

1. Compare quantile, ChiMerge and monotonic bins for utilisation.
2. Force an implausibly high number of pre-bins and explain the IV change.
3. Add 10% missingness associated with default and compare missing-bin WOE.
4. Shift income in the test set and calculate score and bin PSI.
5. Manually combine two bins and reconcile every changed point.

## Chapter deliverable

Run notebook 02. Produce a characteristic report for at least eight variables. For each, write one sentence on economic direction, one on data support, one on stability and one on production treatment of missing/unseen values. Reject at least one variable and show why.


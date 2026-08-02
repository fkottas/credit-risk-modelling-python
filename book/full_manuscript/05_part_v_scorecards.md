# Chapter 25 — Exploratory and Characteristic Analysis

## Explore the process, not only distributions

Scorecard development begins after the population, target and split are frozen. Exploration should describe volumes, dates, products, channels, missingness, event rates and feature behaviour across time. A variable with a strong full-sample relationship may reverse by vintage or represent a policy rule already applied to accepted cases.

Characteristic analysis evaluates one predictor across interpretable groups. For each bin report count, population share, goods, bads, bad rate, WOE, IV component and eventual points. Add time and segment views. A summary slide should not hide zero-event bins, sparse bins or missing values.

```python
from pathlib import Path
from creditriskbook.data.datasets import load_dataset
from creditriskbook.models import split_dataset
from creditriskbook.scorecard import LogisticScorecard, export_characteristic_presentation

bundle = load_dataset("synthetic_retail", n_rows=5_000, seed=251)
train, _ = split_dataset(bundle, bundle.frame)
features = ["income", "debt_to_income", "utilisation", "enquiries_6m", "product"]
scorecard = LogisticScorecard().fit(train[features], train[bundle.target])
export_characteristic_presentation(
    scorecard,
    Path("artifacts/reports/chapter25_characteristics.pptx"),
)
```

The presentation generator creates a title, characteristic summary and one slide per feature with bad rates and a bin table. It is deliberately not a one-click approval pack. Sample dates, population, cut-point rationale, stability, exclusions, judgement and sign-off must be added.

## Univariate traps

Information value is descriptive within a chosen sample and binning. High IV may indicate useful separation, leakage, selection or overfitting. Correlated variables can each look strong but become unstable together. An apparent U-shape may be real or a sparse-tail artefact. Missing-bin performance may change when the application form changes.

Review plots by development, validation and out-of-time sample using the development cuts. Never re-bin the validation set to make its relationship attractive.

**Lab.** Produce a characteristic pack for eight variables. For each, write keep, merge, transform, investigate or exclude, with business and statistical reasons.

# Chapter 26 — Manual Numeric and Categorical Binning

## Why manual binning remains important

Manual bins encode product knowledge, operational thresholds and stable interpretation. Examples include DPD backstops, utilisation bands, term options and documented income ranges. Manual does not mean arbitrary: each cut requires evidence, minimum counts, event support, monotonicity review and validation.

Numeric bins should cover (-\infty) to (+\infty), with missing and special values explicit. Special values such as -999 must not be treated as economic numbers. Categorical grouping combines levels with similar risk and meaning; rare categories may be grouped, but protected or materially different categories should not be hidden merely to smooth bad rates. Unseen production levels require a defined `OTHER` policy.

```python
from creditriskbook.scorecard import (
    BinningProcess,
    manual_categorical_spec,
    manual_numeric_spec,
)

manual = {
    "enquiries_6m": manual_numeric_spec(
        "enquiries_6m", [0, 1, 3, 6], special_values=[-999]
    ),
    "product": manual_categorical_spec(
        "product",
        [["personal_loan"], ["credit_card"], ["bnpl"]],
        labels=["instalment", "revolving", "short_term"],
    ),
}
process = BinningProcess(manual_specs=manual, numeric_method="monotonic")
```

Intervals use right-closed semantics and labels are stored with the bin specification. Training and scoring call the same `transform`; cut points are never recomputed at scoring time.

## Manual-bin policy

The binning memo should include variable definition, available time, raw distribution, cut alternatives, final edges, special handling, missing treatment, event counts, WOE, stability, business rationale and approver. If a policy threshold changes, decide whether it is a policy update or model change; do not quietly edit a cut in production.

**Lab.** Manually bin utilisation using business bands and compare with equal-frequency bins. Apply both to an out-of-time sample. Choose based on stability and meaning, not maximum development IV.

# Chapter 27 — Automated Quantile, Equal-Width, ChiMerge, and Monotonic Binning

## Candidate algorithms

Quantile binning targets similar counts and is robust to skew, but repeated values can collapse edges. Equal-width binning preserves the measurement scale but can create sparse tails. ChiMerge begins with fine ordered intervals and repeatedly merges the adjacent pair with the smallest Pearson chi-square difference in good/bad composition. A monotonic variant continues merging violations until bad rates move in one direction.

The repository implements these algorithms without a scorecard package. It first creates pre-bins, applies minimum population and event/non-event constraints, merges by chi-square to `max_bins`, and optionally enforces a trend. Missing and special values stay outside the ordered merge.

For adjacent bins with observed table (O_{rc}), Pearson’s statistic is

\[
\chi^2=\sum_{r,c}\frac{(O_{rc}-E_{rc})^2}{E_{rc}}.
\]

A small value means the two adjacent bins have similar class composition and are candidates for merging. This is a heuristic, not proof that the final grouping is optimal or stable.

```python
from creditriskbook.scorecard import BinningProcess

process = BinningProcess(
    numeric_method="monotonic",
    max_bins=6,
    prebins=20,
    min_bin_fraction=0.04,
    min_events=5,
    monotonic_trend="auto",
)
binned_train = process.fit_transform(train[features], train[bundle.target])
binned_test = process.transform(test[features])
print(process.specs_["utilisation"])
```

Automatic trend choice can be unstable when the true relationship is flat or U-shaped. Compare increasing and decreasing alternatives, bootstrap edges, and challenge business plausibility. A monotonic variable is not necessarily causal.

## Freeze and validate

Fit bins only on training data. Persist the complete specification. Test boundary values, infinities, missing, special and unseen categories. Calculate population stability using fixed development bins. Monitor share in `OTHER`; a spike may indicate a source change.

**Lab.** Fit quantile, uniform, ChiMerge and monotonic bins to the same six variables. Compare bin counts, IV, out-of-time PSI, minimum events and interpretation. Select a specification under a written policy.

# Chapter 28 — Weight of Evidence and Information Value from First Principles

## Definition and convention

For bin (j), let (G_j) and (B_j) be goods and bads. With smoothing (a>0) and (k) bins,

\[
p^G_j=\frac{G_j+a}{\sum_jG_j+ak},\qquad
p^B_j=\frac{B_j+a}{\sum_jB_j+ak}.
\]

This book defines (WOE_j=\log(p^G_j/p^B_j)). Positive WOE therefore indicates relatively more goods. Some software uses the opposite sign. Mixing conventions reverses coefficients and points; record the convention in every artifact.

Information value is

\[
IV=\sum_j(p^G_j-p^B_j)WOE_j.
\]

Smoothing prevents infinite WOE for zero-event bins but does not make them reliable. The smoothing value affects small bins and belongs in configuration.

```python
from creditriskbook.scorecard import WOEEncoder

encoder = WOEEncoder(smoothing=0.5)
woe_train = encoder.fit_transform(binned_train, train[bundle.target])
woe_test = encoder.transform(binned_test)
print(encoder.tables_["utilisation"].table)
print(encoder.information_values)
```

WOE turns a nonlinear univariate relationship into a piecewise constant representation. A logistic coefficient then scales that characteristic after controlling for others. WOE does not solve multicollinearity, selection bias or temporal instability.

## Review standards

Investigate high IV, zero goods/bads, small bins, non-business ordering and missing-bin shifts. Compare WOE across time. Calculate bin-level PSI using fixed categories. If an unseen scoring category maps to neutral WOE, count and escalate it; neutrality is a fallback, not evidence of equal risk.

**Lab.** Calculate WOE by hand for three bins with and without smoothing. Reverse the event convention and verify how WOE changes. Explain why the final predicted PD can remain equivalent if coefficient signs change consistently.

# Chapter 29 — Logistic Regression by Maximum Likelihood and IRLS

## Model and likelihood

For WOE vector (x_i), logistic regression assumes

\[
p_i=\frac{1}{1+\exp[-(\beta_0+x_i'\beta)]}.
\]

The Bernoulli log-likelihood is

\[
\ell(\beta)=\sum_i\{y_i\log p_i+(1-y_i)\log(1-p_i)\}.
\]

Iteratively reweighted least squares is Newton’s method applied to this likelihood. At each iteration, calculate probabilities, variance weights (p_i(1-p_i)), gradient and information matrix, then update coefficients. The repository adds an L2 penalty to slopes but not the intercept, clips extreme logits for numerical stability, records convergence and retains an approximate covariance matrix.

```python
from creditriskbook.scorecard import IRLSLogisticRegression

model = IRLSLogisticRegression(
    l2=1e-3,
    max_iter=100,
    tolerance=1e-8,
).fit(woe_train, train[bundle.target])
pd_test = model.predict_proba(woe_test)[:, 1]
print(model.converged_, model.n_iter_, model.intercept_, model.coef_)
```

L2 regularisation reduces unstable magnitudes but changes inference. Approximate standard errors rely on model assumptions and do not account for bin search, repeated observations or temporal dependence. Use bootstrap or clustered methods where appropriate.

## Variable selection

Selection should combine business meaning, availability, univariate evidence, correlation, VIF, sign, stability and incremental performance. Stepwise p-values alone overfit. LASSO may select among correlated features arbitrarily. Keep a simple benchmark and document exclusions.

The expected coefficient sign depends on the WOE convention. With good-to-bad WOE and target 1=bad, a stable risk characteristic commonly receives a negative coefficient: higher WOE implies lower bad log odds.

**Lab.** Fit IRLS with L2 values from zero to 0.1. Compare convergence, coefficients, calibration and out-of-time performance. Identify unstable variables rather than choosing the smallest training loss.

# Chapter 30 — PDO Scaling, Bin Points, Ratings, and Reason Codes

## From log odds to a score

Let good-to-bad odds be (O=(1-p)/p). A conventional linear score is

\[
Score=Offset+Factor\log O,
\]

where (Factor=PDO/\log2) and (Offset=BaseScore-Factor\log(BaseOdds)). If base score is 600 at good-to-bad odds 20 and PDO is 50, doubling good odds increases score by 50.

Because the logistic model uses bad log odds (z=\log[p/(1-p)]), score equals `offset - factor*z`. The intercept contributes base points and each characteristic contributes `-factor*beta*WOE`. The repository reconciles row components to total score before rounding and clipping.

```python
from creditriskbook.scorecard import LogisticScorecard, ScoreScale

scorecard = LogisticScorecard(
    scale=ScoreScale(base_score=600, pdo=50, base_odds_good_to_bad=20),
    l2=1e-3,
).fit(train[features], train[bundle.target])

components = scorecard.score_components(test[features].head())
points = scorecard.points_table()
reasons = scorecard.reason_codes(test[features].head(), top_n=4)
print(components[["raw_total", "score", "pd", "rating"]])
print(reasons)
```

Ratings map score ranges to ordered grades. Grade boundaries should target risk differentiation, minimum population, monotonic PD, stability and business use. Calibrate grade PD separately; a label such as R1 has no universal PD.

Scorecard reason codes compare each selected bin’s points with the best observed bin for that characteristic and report the largest penalties. They are faithful to the additive scorecard. For XGBoost, the library uses sensitivity-based counterfactual reasons and labels them as such; it does not invent bin points.

## Implementation controls

Test probability-to-score round trips, PDO doubling, every bin boundary, missing/special/unseen values, row-level points reconciliation, rating boundaries and reason order. Store unrounded and final score. A policy decline reason may differ from a model reason, so preserve both.

**Lab.** Build a manual-plus-automatic scorecard, export CSV, HTML and PowerPoint characteristic packs, map scores to eight grades, and produce four reasons for twenty cases. Reconcile each score by hand for one account.

> Part V provides a complete scorecard implementation from raw variables to review presentation. Every transformation is inspectable, persisted and tested without a specialist scorecard library.

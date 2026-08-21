# Chapter 6 — Logistic Scorecards from Estimation to Reason Codes

## An additive model on WOE variables

After binning and WOE transformation, the scorecard estimates

`logit(PD) = β0 + β1 WOE1 + ... + βp WOEp`.

With this book's WOE convention, safer bins have positive WOE. A sensible risk variable often receives a negative coefficient so safer WOE reduces log-odds of default. Signs must be reviewed characteristic by characteristic; a sign reversal can indicate multicollinearity, confounding, sample noise or an incorrect convention.

The project includes an original penalised logistic solver. `IRLSLogisticRegression` maximises the Bernoulli likelihood using Newton/iteratively reweighted least squares, with optional L2 penalty and sample weights. The intercept is not penalised. Each iteration calculates probabilities, weighted curvature, gradient and Newton step. Convergence occurs when the largest coefficient step falls below tolerance.

```python
from creditriskbook.scorecard import LogisticScorecard

scorecard = LogisticScorecard(binning=binning, l2=1e-3)
scorecard.fit(X_train, y_train)
assert scorecard.model_.converged_
```

The covariance matrix is the inverse observed information approximation. It supports coefficient uncertainty diagnostics, but standard errors after supervised binning and variable selection understate total uncertainty because the transformation was learned from the same outcome.

## Regularisation and weights

L2 regularisation stabilises correlated or sparse WOE variables and reduces separation. It changes the estimand and must be tuned inside development folds, then assessed out of time. A very small default penalty provides numerical stability; larger penalties require performance and calibration challenge.

Weights can correct designed sampling, such as event oversampling, when the inclusion probabilities are known. Weights do not solve reject bias, missing populations or wrong labels. Preserve raw counts and weighted estimates in the development report.

## Scaling probability to score

The scale uses base score, points to double the good-to-bad odds (PDO), and base good-to-bad odds. Let

`factor = PDO / ln(2)`

and

`offset = base_score − factor × ln(base_good_to_bad_odds)`.

For bad probability `p`,

`score = offset − factor × ln(p / (1 − p))`.

With base score 600, PDO 50 and base odds 20:1, a PD of `1/21` maps to 600. Doubling good-to-bad odds to 40:1 adds 50 points. Higher score means lower risk. `ScoreScale` clips only the displayed score to an explicit range; predicted PD remains available.

The scorecard decomposes the logit exactly. Base points are `offset − factor × intercept`. Feature-bin points are `−factor × coefficient × WOE`. Adding base and all feature points reproduces the raw score before rounding and clipping.

```python
components = scorecard.score_components(X_test.iloc[:10])
points = scorecard.points_table()
assert (components["score"].to_numpy() == scorecard.score(X_test.iloc[:10])).all()
```

Reconciliation is a production control. For sampled requests, independently recalculate bin assignment, WOE, logit, PD, score, grade and reasons from the frozen artefact. Any difference is a release blocker.

## Rating grades

A rating grade groups a continuous score or calibrated PD into ordered risk bands. The repository provides explicit score thresholds for illustration. Production grade design should consider minimum observations and defaults, monotonic observed and predicted rates, calibration, migration, operational use and master-scale alignment.

Avoid choosing cut points solely to equalise counts. A stable grade has a clear PD range and purpose. Report migrations by prior/current grade, including new, closed, defaulted and missing. Overrides must retain model grade, final grade, direction, reason, authority, date and performance.

## Reason codes

For an additive scorecard, the best available points for each characteristic define a transparent benchmark. The penalty for a customer's bin is best points minus actual points. The largest penalties become reason codes. This is exact for the fitted points system, but legal or customer-facing language still needs review.

```python
reasons = scorecard.reason_codes(X_test.iloc[:5], top_n=4)
```

A good reason is specific, accurate, stable and actionable where possible. “High utilisation relative to available limit” is better than “model feature 17.” Correlated variables can generate redundant reasons. Missingness must be described truthfully. Reason-code selection should be tested at bin boundaries and against adverse-action requirements in each jurisdiction.

## Policies and overrides

Scorecards often coexist with hard rules: identity failure, legal ineligibility, affordability, age of applicant, sanctions, fraud or missing mandatory documents. Do not hide a deterministic policy decline inside the statistical score. Keep model score, policy rules and final decision as separate fields so validation can assess them separately.

Overrides should be rare enough to analyse. Track up and down overrides, concentrations by user or branch, performance and reason. A model with excellent discrimination can be ineffective if frequent overrides remove its ordering.

## Reject inference

Only booked accounts produce normal performance labels. Augmentation reweights observed accounts, parceling assigns assumed outcomes to rejects, and fuzzy methods spread outcomes probabilistically. All rely on untestable assumptions about selection. Treat reject inference as sensitivity analysis, not discovered truth. Compare model and policy under multiple plausible reject outcomes and consider controlled experiments where lawful and ethical.

## What can fail

- A bin edge differs between Python and production SQL.
- String normalisation maps a new category incorrectly.
- WOE convention is reversed in points generation.
- Base odds are interpreted as bad-to-good instead of good-to-bad.
- Score rounding occurs at each characteristic rather than after summing.
- Grade thresholds overlap or leave gaps.
- Reason codes use current best bins after a model update while scoring uses the old model.

Tests should target every one.

## Chapter deliverable

Implement one manual and one automatic scorecard on the same sample. Reconcile five rows by hand from raw values to grade. Write UAT cases for exact cut points, missing values, special values, unseen categories, minimum and maximum scores, and tie handling in reason codes.


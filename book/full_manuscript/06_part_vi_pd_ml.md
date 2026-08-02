# Chapter 31 — Train, Validation, Test, Out-of-Time, and Cross-Validation Design

## Validation begins with partition design

Training estimates parameters. Validation supports tuning and candidate selection. Test provides a final untouched estimate. An out-of-time sample approximates future deployment and is normally more informative for changing credit populations than a random split. A model tuned repeatedly against the test set no longer has an independent test.

Credit data add dependence: the same borrower, connected company or household may have several rows; monthly snapshots overlap in outcome windows; broker or merchant clusters share process effects. Use group-aware and time-aware partitions. All preprocessing—including binning, encoding, scaling, feature selection and calibration—must fit within training data.

```python
from creditriskbook.data.datasets import load_dataset
from creditriskbook.models import split_dataset

bundle = load_dataset("synthetic_retail", n_rows=8_000, seed=311)
train, test = split_dataset(bundle, bundle.frame, test_size=0.25)
assert train[bundle.date_column].max() <= test[bundle.date_column].min()
print(train.shape, test.shape)
```

Cross-validation estimates variation but ordinary random folds can be invalid under time or group dependence. Nested cross-validation separates hyperparameter choice from performance estimation. For low-default portfolios, folds may have too few events; use repeated temporal windows, Bayesian uncertainty and qualitative evidence.

## Partition policy

Freeze IDs, dates, event rates and hashes for every partition. Set a maturation cutoff. Report excluded incomplete outcomes. Prevent feature-store backfills from changing historical training values without versioning.

**Lab.** Compare random, group and out-of-time splits. Measure event rate, population drift and performance. Explain which split best represents the intended deployment.

# Chapter 32 — AUC, CAP, Accuracy Ratio, KS, Lift, and Cost

## Discrimination is only one dimension

ROC AUC is the probability that a randomly selected default receives higher predicted risk than a randomly selected non-default, under tie handling. It is insensitive to probability scale and therefore cannot establish calibration. The cumulative accuracy profile orders cases by risk and plots cumulative defaults captured against population. Accuracy ratio compares the model CAP with random and perfect ordering and is closely related to Gini (2AUC-1) under standard binary settings.

KS is the maximum difference between score distributions for defaults and non-defaults. Lift at a fraction compares default capture or bad rate in a selected high-risk group with the portfolio average. All depend on the sample and may shift with selection or prevalence.

```python
from creditriskbook.models import evaluate_pd, fit_pd_model, score_pd

model = fit_pd_model(bundle, train)
pd_test = score_pd(model, test)
metrics = evaluate_pd(test[bundle.target], pd_test)
print(metrics)  # AUC, Brier, log loss, KS and central tendency
```

A confusion matrix requires a cutoff. Accuracy can be misleading in low-default data because predicting no defaults may appear accurate. Precision-recall measures focus on events but still do not determine economic value. Cost and profit must reflect amount, LGD, margin and action.

## Uncertainty and comparison

Report confidence intervals and paired comparisons on the same observations. Segment and time results may reveal failure hidden by aggregate AUC. Avoid declaring a challenger superior for a negligible difference obtained after extensive tuning.

**Lab.** Calculate AUC, KS, top-decile lift, Brier score and expected value for logistic and XGBoost. Select a champion using a predeclared hierarchy of criteria.

# Chapter 33 — Calibration, Master Scales, Grades, and Migration

## From rank to probability

Calibration asks whether predicted probabilities agree with observed frequency for a defined horizon and population. Calibration-in-the-large compares mean PD with default rate; slope identifies over- or under-dispersion. Reliability plots group predictions, but bin choice and small counts matter. Brier and log loss assess probability accuracy, while AUC does not.

IRB PD calibration may target a long-run average rather than the current sample rate. The repository applies an intercept shift on odds so ordering is preserved and weighted mean PD matches a target central tendency, subject to a floor.

```python
import numpy as np
from creditriskbook.irb import calibrate_pd_to_long_run_average

raw_pd = np.array([0.005, 0.010, 0.020, 0.040, 0.080])
calibration = calibrate_pd_to_long_run_average(raw_pd, 0.03)
print(calibration.scale_factor, calibration.post_calibration_mean)
```

Platt scaling fits a logistic mapping; isotonic regression fits a monotonic step function. Calibration data must be independent enough to avoid optimism. Recalibration is a model change governed by policy, not a dashboard adjustment.

A master scale maps risk to grades with defined PD ranges and naming. Migration analysis tracks grade movement, default and override. Excessive stability can indicate stale ratings; excessive movement can indicate noise.

**Lab.** Define eight grades with minimum observations and monotonic observed default. Compare point-in-time and through-the-cycle calibration objectives. Document which is appropriate for pricing, IFRS 9 and IRB.

# Chapter 34 — Trees, Random Forests, Gradient Boosting, and XGBoost

## Nonlinear challengers

A decision tree recursively partitions features to reduce impurity or loss. It captures thresholds and interactions but is unstable and prone to overfit. Random forests average many bootstrapped trees with feature subsampling, reducing variance. Gradient boosting fits new trees to residual information; XGBoost adds regularisation, shrinkage, row and column sampling, missing-direction handling and efficient optimisation.

Credit-risk tuning should include depth, learning rate, tree count, minimum child support, subsampling, regularisation and class treatment. Class weights alter the fitted objective and often require probability recalibration. Monotonic constraints can encode directional knowledge but must be justified and tested for interaction effects.

```python
from xgboost import XGBClassifier
from creditriskbook.scorecard import ModelScoreMapper

challenger = XGBClassifier(
    n_estimators=180,
    max_depth=3,
    learning_rate=0.04,
    subsample=0.85,
    colsample_bytree=0.85,
    eval_metric="logloss",
    random_state=341,
    n_jobs=1,
)
# Fit through the tested preprocessing pipeline shown in notebook 03.
# mapper = ModelScoreMapper(fitted_pipeline).fit_reference(train[features])
```

`ModelScoreMapper` converts any `predict_proba` output to the same PDO score scale. This makes business comparisons easier but does not make the nonlinear model an additive scorecard.

## Complexity policy

Require a material, stable benefit over logistic regression. Compare calibration, fairness, reason quality, latency, security and monitoring burden. Preserve training data and library versions. Test deterministic seeds and serialization.

**Lab.** Tune a depth-limited XGBoost challenger against the scorecard. Evaluate out-of-time metrics and create a common score scale. Write a complexity justification or reject the challenger.

# Chapter 35 — Explainability, Nonlinear Reason Codes, and Fairness Diagnostics

## Different explanation questions

Global explanation asks which features influence predictions across a population. Local explanation asks why one case received a result. Counterfactual explanation asks what change would alter it. Adverse-action reasoning asks for specific, accurate and actionable principal factors under applicable policy and law. These are not interchangeable.

Coefficients and scorecard points are additive and directly auditable. Tree feature importance may be biased toward variables with many split opportunities. Permutation importance measures performance loss after shuffling but is affected by correlation. SHAP allocates prediction differences under a chosen background and dependence assumption; values are not causal.

The repository’s nonlinear reason method replaces one feature at a time with a reference value and observes score improvement. It labels the result sensitivity-based and validates actionability separately.

```python
from creditriskbook.scorecard import ModelScoreMapper

# mapper = ModelScoreMapper(fitted_model).fit_reference(train_features)
# reasons = mapper.reason_codes(test_features.head(20), top_n=4)
# print(reasons)
```

Fairness diagnostics include group approval, error, calibration and outcome measures. Conflicting criteria are common when base rates differ. Protected attributes may be needed for auditing even when excluded from prediction, subject to lawful handling. Small intersectional groups require uncertainty.

## Explanation governance

Maintain an approved feature-to-reason dictionary, suppress non-actionable or sensitive reasons where legally required, and test fidelity. Monitor reason frequencies. A reason such as “region” may be unacceptable even if predictive.

**Lab.** Compare scorecard bin reasons, SHAP-style contributions and sensitivity reasons for the same twenty cases. Assess fidelity, stability, actionability and legal review needs.

# Chapter 36 — Reject Inference and Champion-Challenger Strategy

## The missing-outcome problem

Default outcomes are generally observed for accepted and booked applicants, not for rejected applicants. The accepted sample is selected by past policy, models and manual judgement. Augmentation reweights accepted cases, parceling assigns inferred outcomes to rejected bands, and extrapolation models outcomes from accepted cases. Each relies on unverifiable assumptions about rejected performance.

Approval data alone cannot solve this. The UCI Credit Approval dataset may model decisions but contains no default outcome. Treating rejection as default trains a policy-replication model, not PD.

```python
from creditriskbook.data.datasets import load_dataset

approval = load_dataset("uci_credit_approval", cache_dir="data/raw")
assert approval.target == "approved"
print("Scope limitation:", approval.limitations)
```

Randomised exploration can identify outcomes more credibly but creates customer, capital and ethical risk and requires strict policy. Quasi-experimental cutoff designs may help locally when assumptions hold. Any reject-inference result should be sensitivity analysis, not hidden truth.

A champion-challenger framework keeps the approved production model as champion while evaluating challengers in shadow. Predefine data, metrics, duration, materiality and promotion gates. Avoid selecting a challenger on the same period used to invent it.

**Lab.** Create optimistic, neutral and pessimistic reject scenarios. Recalibrate and compare cutoff economics. Report the range rather than a single inferred AUC.

> Part VI connects statistical performance to calibration, explanation, selection and model-choice governance. Machine learning is a challenger within the system, not an exception to it.

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

For a node $N$ containing $n$ observations with default share $p$, common binary-classification impurities are

\[
Gini(N)=1-p^2-(1-p)^2=2p(1-p),
\]

\[
Entropy(N)=-p\log p-(1-p)\log(1-p).
\]

Both equal zero in a pure node and are largest near $p=0.5$. For candidate split $s$ producing left and right children, impurity reduction is

\[
Gain(s)=I(N)-\frac{n_L}{n}I(N_L)-\frac{n_R}{n}I(N_R).
\]

The tree selects the eligible split with largest gain, subject to minimum child size, depth and other constraints. Consider ten loans with outcomes $[0,0,0,0,0,0,1,1,1,1]$ ordered by utilisation. The parent has $p=0.4$ and Gini $0.48$. A split after the sixth loan gives two pure children and gain $0.48$. A split after the fifth gives a pure left child and right default share $0.8$; weighted child impurity is $0.5(0)+0.5(0.32)=0.16$, so gain is $0.32$. The first split wins on training impurity, but a minimum-child or stability rule may reject a seemingly perfect threshold when it is supported by too few or temporally concentrated observations.

For regression trees, squared-error impurity is the within-node sum of squares

\[
SSE(N)=\sum_{i\in N}(y_i-\bar y_N)^2.
\]

Other objectives include absolute-error, Poisson and survival losses. A credit model must match objective to outcome; a Gini split does not directly estimate calibrated PD.

Random forests fit trees $T_b(x)$ on bootstrap samples and average probabilities

\[
\widehat p(x)=\frac{1}{B}\sum_{b=1}^{B}T_b(x).
\]

Feature subsampling decorrelates trees; averaging reduces variance but does not automatically calibrate probabilities. Gradient boosting instead builds an additive score $F_M(x)=F_0(x)+\sum_{m=1}^{M}\eta f_m(x)$, where each new tree follows the negative gradient of the chosen loss. For Bernoulli log loss, the initial score is log odds and boosting updates the logit. XGBoost adds second-order approximations and a regularised objective. This mathematical difference explains why bagging and boosting have different tuning and failure modes.

Credit-risk tuning should include depth, learning rate, tree count, minimum child support, subsampling, regularisation and class treatment. Class weights alter the fitted objective and often require probability recalibration. Monotonic constraints can encode directional knowledge but must be justified and tested for interaction effects.

Benchmark evidence should be interpreted with the literature rather than a single leaderboard. Lessmann et al. compare a broad classifier set across multiple credit datasets [R46]; Louzada et al. and Dastile et al. review classical and machine-learning credit-scoring methods [R47–R48]. Their results motivate disciplined benchmarking, but no public benchmark determines performance, legality or governance for a new lender population.

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

![Figure 34.1 — Original impurity calculation for two candidate tree splits on the same ordered sample.](book/figures/tree-split-gain.png)

## Linear, multiclass, ordinal, neural, Bayesian, and self-organising challengers

The linear-probability model $E[Y\mid X]=X\beta$ is useful as a diagnostic because coefficients are marginal probability changes, but fitted values can fall outside $[0,1]$ and its error variance is heteroskedastic. A robust covariance estimate can improve inference; it cannot make the probability range valid. Binary logistic regression is therefore the usual transparent benchmark.

When the outcome has mutually exclusive classes—current, 30 DPD, 60 DPD, default, for example—multinomial logistic regression defines a reference class and

\[
P(Y=c\mid x)=\frac{\exp(\alpha_c+x^\top\beta_c)}{1+\sum_{k=1}^{C-1}\exp(\alpha_k+x^\top\beta_k)}.
\]

If classes are ordered, a cumulative-logit model instead assumes

\[
\log\frac{P(Y\le c\mid x)}{P(Y>c\mid x)}=\alpha_c-x^\top\beta.
\]

The shared slope is the proportional-odds assumption and must be tested. A nomogram is a graphical translation of an additive model's coefficients into points; it is a presentation, not a different estimator. For delinquency states, a transition or competing-risk model can be more faithful than forcing every state into one static label.

A multilayer perceptron composes affine transformations and nonlinear activations. With hidden layer $h=\phi(W_1x+b_1)$ and logit $z=W_2h+b_2$, the bad probability is $\sigma(z)$. Binary cross-entropy is

\[
\mathcal{L}=-\sum_i\{y_i\log p_i+(1-y_i)\log(1-p_i)\}.
\]

Back-propagation applies the chain rule to compute gradients. Width, depth, activation, initialisation, regularisation, early stopping and class treatment are model choices. Neural networks are most credible when sample size and genuinely complex inputs justify them; tabular credit data often do not provide a material advantage over well-tuned boosting. Probability calibration, explanation stability and operational reproducibility remain separate tests.

Naive Bayes uses Bayes' rule with a conditional-independence approximation,

\[
P(Y=c\mid x)\propto P(Y=c)\prod_j P(x_j\mid Y=c).
\]

It is fast and useful as a benchmark, but correlated bureau ratios violate the simplifying assumption. Bayesian networks make conditional dependencies explicit in a directed acyclic graph; causal meaning must not be inferred from a graph learned only from association. Bayesian additive regression trees place priors over an ensemble of shallow trees and integrate posterior uncertainty rather than returning one fitted tree. Markov-chain Monte Carlo approximates posterior expectations with dependent draws; variational inference optimises a tractable approximation $q(\theta)$ by minimising $KL(q\|p)$. Convergence, approximation bias, prior sensitivity and computation need validation.

A self-organising map updates the best-matching prototype $m_c$ and its neighbours,

\[
m_j^{(t+1)}=m_j^{(t)}+\eta_t h_{cj,t}(x_t-m_j^{(t)}).
\]

It can visualise borrower topology or detect unusual groups, but its map is sensitive to scale, topology and random initialisation and it does not produce a calibrated PD by itself. Use it as exploratory evidence, never as an unexplained customer-decision rule.

These families are included to teach model choice, not to encourage a leaderboard. For each challenger, the student writes the objective, identifies assumptions, constructs a simple fixture, verifies a limiting case, calibrates probabilities, maps to a common score only when meaningful, and explains why the added complexity earns its control cost.

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

Fairness diagnostics include group approval, error, calibration and outcome measures. Conflicting criteria are common when base rates differ. Protected attributes may be needed for auditing even when excluded from prediction, subject to lawful handling. Small intersectional groups require uncertainty. Kozodoi, Jacob and Lessmann analyse fairness criteria and implementation in credit scoring [R49], while Fuster et al. show why flexible prediction can have distributional effects in credit markets [R51]. These studies inform investigation; they do not replace jurisdiction-specific protected-class, adverse-impact, business-necessity and customer-remedy analysis. Supervisory practice also requires specific adverse-action reasons and management of model risk, not only parity metrics [R9, R44–R45].

Explainability literature likewise distinguishes a technically plausible attribution from an operationally valid reason. Bussmann et al. discuss explainable machine learning in credit-risk management [R50], and the EBA's follow-up report on machine learning for IRB models emphasises governance, interpretability and prudent model use [R43]. The book therefore tests fidelity, stability and actionability separately.

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

# Chapter 7 — Machine-Learning Challengers and a Common Score Scale

## Complexity must earn its controls

Trees and ensembles capture interactions, thresholds and nonlinearity without manual bins. Random forests reduce variance by averaging decorrelated trees. Gradient boosting fits weak learners sequentially to residual structure. XGBoost and LightGBM add efficient regularisation, subsampling, missing-value handling and constraints. Neural networks can represent still more complex functions. These benefits create more tuning, implementation and explanation risk.

The comparison is not “logistic is interpretable, ML is accurate.” A poorly binned logistic model can be misleading; a monotonic constrained booster with stable features can be reviewable. Compare performance, calibration, stability, reason quality, latency, reproducibility, fairness, operational fit and governance cost.

## Development pipeline

All preprocessing must be inside the model pipeline. Numeric imputation and categorical encoding are fitted on training data. Hyperparameters are selected within development folds. The out-of-time sample remains untouched until the candidate is frozen.

Notebook 03 installs a common preprocessing pipeline and uses `XGBClassifier` when the optional `ml` dependencies are installed. CI uses `HistGradientBoostingClassifier` as a deterministic fallback, ensuring the notebook remains executable without a large optional package.

```python
try:
    from xgboost import XGBClassifier
    estimator = XGBClassifier(
        n_estimators=180,
        max_depth=3,
        learning_rate=0.04,
        subsample=0.85,
        colsample_bytree=0.85,
        eval_metric="logloss",
        random_state=303,
    )
except ImportError:
    estimator = HistGradientBoostingClassifier(random_state=303)
```

Use early stopping with a validation set when supported, but do not tune on the final test period. Record the exact feature order, library version, thread settings and seed. Some parallel algorithms are not bitwise deterministic across hardware; define the acceptable reproducibility level.

## Monotonic constraints

Monotonic constraints encode directional expectations, for example that worsening delinquency should not reduce risk after holding other features constant. They can improve plausibility and stability, but constraints apply to the model's partial relationship, not every realised prediction. Correlated features can produce surprising combined effects. Document each constraint and test local counterexamples.

Do not constrain a feature merely because a scorecard was monotonic. A genuine U-shape may be economically correct. Compare unconstrained, constrained and segmented forms and evaluate uncertainty in sparse regions.

## Calibration

Tree ensembles often rank well while probabilities are biased. Assess calibration-in-the-large, slope, Brier score, log loss and calibration plots by time and segment. Platt scaling fits a logistic transformation of the raw score; isotonic regression fits a non-decreasing step function. Fit the calibrator on data independent of base-model fitting, or use nested/cross-fitted predictions. Recalibration can fix level and slope but cannot restore lost rank performance or repair leakage.

## One score scale for many models

A customer-facing or strategy system may require a familiar 300–900 scale regardless of model. `ModelScoreMapper` takes any object with `predict_proba`, `decision_function`, or a callable returning probabilities. It applies the same log-odds score transformation used by the logistic scorecard.

```python
from creditriskbook.scorecard import ModelScoreMapper

mapper = ModelScoreMapper(model, feature_names=tuple(features))
mapper.fit_reference(X_train)
pd_hat = mapper.predict_pd(X_test)
score = mapper.score(X_test)
```

This mapping preserves model ordering and probabilities up to integer score rounding. It does not make XGBoost additive in original characteristics. A nonlinear model's score is a single transformation of its final PD.

## Nonlinear explanations and reason codes

For a non-additive model, notebook 03 uses sensitivity reasons. Each feature is replaced by a training reference value while other fields remain fixed; the score change is measured. The features whose replacement most improves the score are returned as reasons.

This method is simple and model-agnostic, but it can create unrealistic combinations, is sensitive to correlated variables and is not a causal explanation. It must not be described as exact bin points. Alternatives include TreeSHAP, constrained counterfactuals, accumulated local effects and model-specific contribution outputs. Each answers a different question.

For XGBoost, contribution outputs can decompose the model margin into feature contributions. Converting contributions to points requires the same factor and sign as the log-odds scale. Even then, grouping one-hot encoded columns back to a business characteristic and producing customer-facing reasons require explicit logic and testing.

## Benchmarking protocol

Create one frozen comparison table:

| Dimension | Scorecard | Gradient booster |
|---|---|---|
| Out-of-time AUC/KS | measured | measured |
| Calibration slope/intercept | measured | measured after calibration |
| Time and segment stability | measured | measured |
| Missing/unseen behaviour | explicit bins | pipeline-specific |
| Exact global decomposition | yes | model-specific |
| Local reasons | bin penalties | sensitivity/contributions |
| Latency and package size | low | usually higher |
| Change-control burden | moderate | higher |

Add confidence intervals and materiality thresholds before viewing results. A 0.005 AUC gain may not justify a larger governance burden, while a substantial lift in a high-loss segment may.

## Neural and Bayesian challengers

An MLP can be useful with large behavioural or transactional data, embeddings and repeated observations. It needs strong regularisation, temporal validation, probability calibration and explanation testing. A neural network on a small tabular application sample is usually a benchmark, not an automatic improvement.

Bayesian models are valuable when uncertainty and partial pooling matter. A low-default portfolio can share information across grades or industries while retaining segment-level uncertainty. Prior choices become model assumptions requiring sensitivity analysis. Posterior intervals are not a substitute for representativeness or correct default definition.

## Chapter deliverable

Run notebook 03 with the fallback and with XGBoost installed. Compare out-of-time discrimination, calibration and score distribution with the Chapter 6 scorecard. Select twenty rows with the greatest difference in rank. Explain whether interaction, missingness or category treatment caused each difference.


# Chapter 8 — Evaluation, Calibration, Selection and Credit Economics

## Evaluation starts with design

Metrics cannot repair a weak split. Define development, validation and out-of-time periods before modelling. Make sure performance windows are fully matured or use censoring methods. Split by customer or connected group when repeated records would leak. Preserve product, channel, region and policy segments for diagnostics.

Cross-validation estimates development variability and supports tuning. For temporal data, use rolling or expanding windows that respect order. The final out-of-time result is one draw from a changing process; report uncertainty and prior-period backtests.

## Rank metrics

ROC AUC is the probability that a randomly selected event receives higher predicted risk than a randomly selected non-event. Gini or Accuracy Ratio is often `2 × AUC − 1` under the ROC definition. CAP compares cumulative captured events against population fraction. KS is the maximum separation between score distributions of events and non-events.

These metrics measure ordering, not probability accuracy. They are insensitive to a monotonic recalibration and can look strong in a sample whose event rate or selection differs from production. Report confidence intervals and segment results. A global AUC can hide failure in a small, material segment.

Confusion matrices require a threshold. Accuracy is usually misleading under imbalance. Precision, recall, specificity and false-positive rates depend on prevalence and policy. Show counts as well as rates, and label event orientation clearly.

## Proper scoring and calibration

Log loss rewards probability assigned to the realised outcome and strongly penalises confident errors. Brier score is mean squared probability error. Calibration-in-the-large compares mean predicted and observed event rates. Calibration slope tests whether predictions are too extreme or too compressed. Reliability plots group predictions, but bin choices and sparse tails matter.

Assess calibration by observation period, product, grade and relevant group. Use account weights only when the estimand requires them. For repeated monthly records, distinguish record-level calibration from customer or exposure-weighted loss calibration.

Platt or isotonic calibration must be estimated on data not used to fit the base model. A calibrated score should be frozen as a combined artefact. Monitoring raw and calibrated outputs separately helps diagnose whether the ranker or calibrator changed.

## Cut-offs and value

Notebook 04 evaluates approve-if-PD-below-cut-off strategies. It assigns a performing margin, default loss and decline cost to matured outcomes. The best historical cut-off maximises the chosen teaching objective.

```python
from creditriskbook.decisioning import cutoff_table

policies = cutoff_table(predicted_pd, y_test)
best = policies.loc[policies["realised_profit"].idxmax()]
```

Production decisioning is richer. Expected value includes price, amount, utilisation, prepayment, funding, operating cost, collections, capital, tax and time. Constraints include risk appetite, approval volume, affordability, fairness, concentration and operational capacity. Optimise under uncertainty and stress, not only base-case point estimates.

Profit evaluation on observed booked accounts is affected by historical approval. The model has no ordinary outcome evidence for past rejects. Changing the cut-off changes the population, borrower behaviour and possibly price. Causal policy evaluation or controlled experimentation may be required.

## Rating and migration validation

Grades should have monotonically ordered observed default rates, adequate counts and calibrated PD ranges. Backtesting compares observed events with predicted probabilities using binomial or distributional methods, but dependence and overlapping horizons can invalidate simple tests. Report deviations, uncertainty and economic materiality.

Migration analysis distinguishes score movement from grade-boundary effects. Calculate transition matrices, upgrades, downgrades, defaults, new and closed accounts. A stable grade distribution is not necessarily good if risk changed; a changing distribution is not necessarily drift if the portfolio changed as expected.

## Reject inference and selection

Historical approval creates missing-not-at-random outcomes. Common reject-inference methods impose assumptions:

- augmentation assumes accepted cases can represent rejects after weighting;
- parceling assigns event rates to rejected score bands;
- extrapolation applies the accepted model outside observed support;
- external bureau outcomes provide partial labels with different definitions;
- experimentation observes outcomes under a controlled policy where lawful.

No method identifies rejected default without information. Present a sensitivity envelope: optimistic, central and conservative reject performance. State which policy decisions remain robust.

## Fairness diagnostics

Notebook 04 calculates approval and observed default rates by a synthetic protected characteristic retained outside the model. This is a starting dashboard, not a fairness finding. Review representation, missingness, model calibration, error rates, score distribution, price, limit, reasons and outcomes. Calculate uncertainty and minimum cell sizes. Investigate intersections and process stages.

Group metrics can conflict. Equal error rates, equal calibration and equal approval are generally not simultaneously achievable when base rates differ. The institution needs an applicable legal and ethical objective, not metric shopping. Proxy and outcome bias must be considered. Human overrides and policy rules can create disparity even when model scores are similar.

## Stress and uncertainty

Bootstrap at the appropriate unit—customer, cohort or cluster—to estimate metric uncertainty. Repeat feature selection and calibration inside each bootstrap if total development uncertainty matters. Stress prevalence, macro conditions, missingness and policy mix. Track the distribution of profit-optimal cut-offs rather than one number.

## Model selection record

The selection committee should see a pre-agreed scorecard containing predictive, calibration, economic, stability, fairness, operational and governance criteria. Record material weaknesses and compensating controls. A challenger is not selected only because it tops one leaderboard.

## Chapter deliverable

Using notebook 04, produce an out-of-time model comparison with AUC, KS, Brier, log loss, calibration by decile, profit by cut-off and group diagnostics. Bootstrap customer-level confidence intervals. Recommend a cut-off range and list the assumptions that would invalidate it.


# Chapter 18 — Integrated Case Studies and Student Projects

## Case 1: retail application scorecard

Use synthetic retail data first, then South German Credit. The synthetic case has observation dates and supports out-of-time validation; South German has no application date, was collected in 1973–1975, oversampled bad credits and transformed amounts. Its random split is a limitation, not an equivalent validation design [R10].

Tasks:

1. Run data-quality controls and create a sample report.
2. Keep age, sex-related and foreign-worker fields outside the baseline model for controlled fairness analysis.
3. Fit manual, ChiMerge and monotonic scorecards.
4. Export characteristic reports and reject unstable variables.
5. Fit the IRLS logistic model, scale points and create reasons.
6. Compare with gradient boosting on one score scale.
7. Evaluate rank, calibration, profit and group outcomes.
8. Write validation and UAT packs.

Do not compare raw AUC across the two datasets as if they were the same population. The objective is to compare workflow robustness.

## Case 2: behavioural credit-card PD

Use the UCI Taiwan card-default dataset: 30,000 customers with 2005 limit, bill, payment and delinquency fields, licensed CC BY 4.0 [R11]. Exclude demographic fields from the baseline and retain them for diagnostics where lawful. There is no origination date, so random validation is only a benchmark.

Construct behavioural features: recent maximum delinquency, payment-to-bill ratios, utilisation proxies, bill trend, payment volatility and missed-payment count. Guard against division by zero and negative bills. Compare raw monthly fields with aggregated features. Calibrate the challenger and map it to the common score scale.

## Case 3: anonymised approval data

The UCI Credit Approval target is `approved`, not default [R12]. Use it to study mixed data types, missingness, pipeline execution and selection. Do not call model output PD. Ask which approval patterns could become self-reinforcing and why anonymisation prevents a meaningful fairness conclusion.

## Case 4: corporate low-event failure

Use the Polish one-year bankruptcy file and Taiwan bankruptcy data [R13–R14]. Fit a regularised logistic benchmark and gradient booster. Handle missing ratios inside the training pipeline. Use stratified validation only as a source-limited benchmark and construct bootstrap uncertainty for event rates, AUC and calibration.

Compare pooled, segment and Bayesian-partial-pooling concepts. Apply probability floors only as an explicit post-estimation rule and show their effect. State why bankruptcy is not automatically regulatory default.

## Case 5: synthetic IFRS 9 portfolio

Generate loans with origination date, maturity, amortisation, current DPD, origination/current lifetime PD, LGD, EAD and effective interest rate. Define quantitative and qualitative SICR. Create three macro scenarios, monthly marginal PD and exposure schedules. Calculate Stage 1, 2 and 3 ECL, probability weighting and movement.

Controls:

- scenario weights sum to one;
- marginal PD sums to cumulative PD;
- Stage 3 default probability is treated consistently;
- discount factors use the approved rate;
- account ECL reconciles to monthly and portfolio totals;
- stage and overlay changes reconcile to prior period.

## Case 6: workout LGD

Generate default events and cash-flow ledgers. Include collateral proceeds, partial cash recovery, costs, cures, incomplete cases and multi-year timing. Calculate raw and model LGD with visible boundaries. Fit cure and positive-severity components. Validate by default vintage and resolution status.

## Case 7: revolving EAD

Generate monthly balance and limit histories before default. Calculate raw CCF at several reference horizons. Compare bounded CCF, additional draw and balance-transition models. Stress borrower drawdown and management cancellation separately. Reconstruct EAD exactly from selected CCF.

## Case 8: deployment incident and agent triage

Package the selected PD model with manifest. Run shadow scoring. Inject an unseen category, rising missingness and prediction PSI. The governed agent should cite evidence and recommend review or halt. It cannot change customer decisions or deploy a fix. The team diagnoses, validates remediation, obtains approval and rolls forward or back.

## Capstone evidence pack

The student submits:

- data and licence statement;
- sample and target specification;
- quality report and issue log;
- EDA and characteristic report;
- model-development report and code;
- calibration and decision analysis;
- fairness and customer-impact diagnostics;
- validation report;
- UAT evidence;
- model card and manifest;
- deployment and rollback plan;
- monitoring dashboard specification;
- agent permission and evaluation report;
- reproducible run instructions and hashes.

## Completion criterion

A capstone is complete when another reviewer can reproduce it, trace every material number to source and code, understand limitations, challenge decisions, and operate the control process. A high model metric without that evidence is an unfinished project.


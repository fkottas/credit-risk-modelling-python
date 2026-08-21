# Chapter 15 — Validation, UAT and Model Governance

## Independent challenge is a process

Validation asks whether a model is conceptually sound, correctly implemented, fit for purpose and performing as expected within known limitations. Independence depends on authority, competence and freedom from development incentives, not only organisational title. Validation scope should be proportionate to materiality and risk.

A complete review covers:

- purpose, use and regulatory/accounting classification;
- data lineage, sample, target and representativeness;
- methodology, assumptions, transformations and selection;
- estimation, tuning, calibration and uncertainty;
- performance, stability, sensitivity and benchmarking;
- fairness, explainability and customer impact where relevant;
- implementation, security and access controls;
- monitoring, limitations, overlays and change plan.

Replicate critical results from frozen artefacts. Reproduction means independent execution of documented code and data; replication challenges choices with alternative construction or methods.

## PD validation

Check default definition, observation/performance windows, exclusions and calibration population. Recalculate rank and probability metrics with confidence intervals. Examine score distributions and event rates by time, segment and grade. Test calibration level and slope. Compare with a simple benchmark and prior model.

For a scorecard, inspect every bin, WOE, IV, coefficient and point. Reconcile raw rows to scores. Challenge supervised binning and rejected variables. For ML, repeat tuning boundaries, assess overfit, constraints, explanations and package reproducibility.

## LGD, EAD and ECL validation

LGD validation reconstructs discounted cash flows, costs, cure and incomplete workouts. EAD validation reconstructs reference balance, limit, undrawn and default exposure. Compare account- and exposure-weighted error, boundary cases and downturn periods.

ECL validation challenges staging, lifetime PD, scenario paths and weights, LGD/EAD response, discounting, prepayment, overlays and finance reconciliation. Component accuracy does not guarantee total ECL if timing or dependence is wrong. Backtest movement and stage transfers as well as closing level.

## Benchmarking

A benchmark should be simpler or differently specified enough to reveal model weakness. Examples include long-run segment rates, univariate scorecards, regularised logistic, alternative calibration, nonparametric survival and simple loss rates. The benchmark need not outperform. Material unexplained difference requires investigation.

## Findings and materiality

A finding states condition, evidence, risk, materiality, recommendation, owner and due date. Avoid vague language such as “monitor closely.” Define closure evidence. An accepted limitation has authority, compensating control and expiry; it does not disappear.

## UAT is not validation

Validation assesses model soundness. QA checks software against technical requirements. UAT demonstrates that business and control users can execute the intended process and obtain correct outcomes. The same test can support more than one, but sign-offs remain distinct.

UAT covers business, data, technical, integration, security and operational scenarios. For a scorecard:

- exact lower and upper bin boundaries;
- null, blank, malformed and special values;
- unseen categories and character encodings;
- points, PD, grade and reason-code reconciliation;
- policy rule precedence and override authority;
- duplicate request and idempotency;
- latency, timeout, fallback and logging;
- old/new parallel differences;
- rollback to prior approved version.

Every test has input, expected output, tolerance, evidence and owner. Avoid expected outputs produced by the same function under test. The repository's unit tests independently verify scale round-trip, PDO, score-component reconciliation, live data hashes, capital/RWA identity, EAD reconstruction and notebook execution.

## Parallel run and shadow testing

Parallel run computes old and new outputs on the same production inputs without changing decisions. Reconcile population, missingness, score, grade, approval simulation, ECL and system performance. Classify differences by intended model change, data mapping, policy, rounding or defect.

Shadow deployment sends requests to the new service while the approved system remains authoritative. It tests real latency, schema, categories and monitoring. Protect customer data and prohibit downstream action from shadow output.

## Governance lifecycle

Inventory begins at proposal, not deployment. Define owner, developer, validator, user, approver, data owner, technology owner, compliance and audit roles. Segregate code merge, model approval and deployment permissions.

Changes are categorised by materiality. A documentation typo differs from a recalibration, bin change, feature change, library upgrade or new use. Predefine validation and approval required for each. Emergency changes have time-limited authority and retrospective review.

Redevelopment triggers can include discrimination decline, calibration breach, PSI, segment growth, policy change, default definition, new data, regulation, severe incident or expired limitation. Numeric thresholds initiate investigation; they do not automatically retrain.

## Chapter deliverable

Write a validation plan and twenty-case UAT pack for notebook 02. Include at least five failure cases. Reproduce the score for five accounts using only the points CSV. Define evidence required to close any discrepancy.


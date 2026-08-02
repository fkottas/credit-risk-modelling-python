# Complete first-edition structure

Working title: **Applied Credit Risk with Python: Scorecards, IRB, IFRS 9, Deployment and Governed Agentic AI**

Author: **Dr. Ferdinantos Kottas**

This edition uses eighteen large chapters rather than dozens of small chapters. Every chapter has a runnable entry point, a validation question, a governance boundary, and a bridge to the integrated case studies. Theory is introduced at the point where a modeller needs it.

## Part I — The end-to-end credit system

1. **Credit risk as an operating system** — uncertain cash flows; expected and unexpected loss; PD, LGD and EAD dependence; classification, regression, survival and multi-state formulations; decisions, profitability and customer outcomes.
2. **Products, borrowers and the credit lifecycle** — retail, cards, mortgages, SME, corporate, BNPL and embedded finance; prime, subprime, thin-file and low-default segments; origination through collections, cure, recovery and closure.
3. **Basel IRB, IFRS 9, CECL and responsible lending** — purposes, definitions, horizons, cycle philosophy, staging, SICR, capital functions, fair lending, data protection and high-risk AI.
4. **Lawful data, architecture and quality engineering** — contracts, lineage, point-in-time joins, public-data licences, APIs, sampling, missingness, leakage, reconciliation, quality gates and deliberately corrupted synthetic labs.

## Part II — PD, scorecards and machine learning

5. **From-scratch binning, WOE and characteristic analysis** — manual, quantile, equal-width, ChiMerge and monotonic bins; missing and special values; smoothing; IV; stability; characteristic review packs.
6. **Logistic scorecards from estimation to reason codes** — an original IRLS solver; regularisation; bin points; base score, PDO and odds; ratings; overrides; policy rules; audit reconciliation.
7. **Machine-learning challengers and common score scales** — trees, random forests, gradient boosting, XGBoost, LightGBM, neural networks, Bayesian methods and monotonicity; model-agnostic probability-to-score mapping; nonlinear reason-code boundaries.
8. **Evaluation, calibration, selection and credit economics** — out-of-time validation, AUC, CAP, AR, KS, calibration, uncertainty, cut-offs, pricing, profitability, reject inference, fairness diagnostics and adverse-action considerations.
9. **Survival, lifetime PD and low-default portfolios** — Kaplan–Meier, discrete hazards, Cox/AFT concepts, competing events, marginal and cumulative PD, Bayesian pooling, conservatism and horizon validation.

## Part III — LGD, EAD, ECL and capital

10. **Workout LGD, cure and recovery modelling** — cash-flow ledgers, costs, discounting, incomplete workouts, two-stage models, mixture behaviour, calibration and downturn considerations.
11. **EAD, CCF and revolving exposure** — reference dates, limits, drawdown, raw versus bounded CCF, behavioural exposure, calibration, cancellations and PD–LGD–EAD dependence.
12. **IFRS 9 and CECL engines** — staging, SICR, 12-month and lifetime ECL, scenario weighting, cash-flow timing, effective-interest discounting, overlays, provision matrices, CECL methods and reconciliation.
13. **IRB capital, portfolio and counterparty risk** — asset correlations, maturity adjustment, RWA, concentration, Vasicek and Monte Carlo intuition, exposure profiles, netting, collateral, CVA/DVA and SA-CCR boundaries.
14. **Stress testing and decision optimisation** — macro scenarios, satellite models, sensitivity, reverse stress, risk-based pricing, limits, capital allocation, bandits and safety-constrained reinforcement learning.

## Part IV — Production, governance and agentic AI

15. **Validation, UAT and model governance** — independent challenge, benchmarking, statistical tests, qualitative review, implementation reconciliation, edge cases, parallel runs, sign-off, inventory and change control.
16. **Deployment, monitoring and model lifecycle** — packages, APIs, batch and real-time scoring, model registry, CI/CD, security, champion–challenger, drift, mature-outcome monitoring, incidents, rollback, redevelopment and retirement.
17. **Governed agentic AI in credit risk** — bounded agents for data quality, documentation and monitoring; tools, permissions, evidence provenance, prompt injection, hallucination, segregation of duties, evaluation, red teaming, kill switches and human approval.
18. **Integrated case studies and student projects** — retail application scorecard, Taiwan behavioural PD, corporate low-event models, synthetic IFRS 9, workout LGD, revolving EAD, IRB capital, deployment incident and agent triage.

## Appendices

- Repository, environment and testing guide
- Dataset and licence register
- Mathematical notation and derivations
- Regulatory source map and version log
- Model-development, validation, UAT, monitoring and agent-control templates
- API, run-manifest, model-card and audit-event schemas

## Runnable crosswalk

| Chapters | Primary code/notebook |
|---|---|
| 1–4 | `examples/end_to_end.py`, notebook 01 and notebook 08 |
| 5–6 | `creditriskbook.scorecard`, notebook 02 |
| 7 | `ModelScoreMapper`, notebook 03 |
| 8 | `decisioning.py`, notebook 04 |
| 9–11 | `survival.py`, `risk_components.py`, notebook 05 |
| 12–14 | `ecl.py`, `capital.py`, notebook 06 |
| 15–17 | tests, monitoring and governed agent, notebook 07 |
| 18 | all notebooks and the end-to-end workflow |

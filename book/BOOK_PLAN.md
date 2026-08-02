# Expanded master structure

Working title: **Applied Credit Risk with Python: IRB, IFRS 9, CECL and Governed Agentic AI**

The book is organised around four connected systems: the risk measurement system, the accounting and capital system, the credit decision system, and the production control system. Theory is introduced when an implementation needs it.

## Part 0 - Reproducible and lawful practice

1. How to use the book and repository
2. Evidence, copyright, dataset licences, privacy, and reproducibility
3. The end-to-end credit-risk operating model

## Part I - Mathematical and economic foundations

4. Uncertain cash flows, default, recovery, exposure, and loss
5. Expected and unexpected loss; dependence between PD, LGD, and EAD
6. Classification, regression, survival, multi-state, and causal questions
7. From probability estimates to decisions, profit, capital, and customer outcomes

## Part II - Products, borrowers, and lifecycle

8. Retail loans, cards, mortgages, SME and corporate lending
9. BNPL, microcredit, embedded finance, open banking, and alternative data
10. Prime, subprime, thin-file, low-default, and vulnerable-customer segments
11. Origination, account management, delinquency, default, collections, cure, recovery, and closure
12. Default definitions, observation windows, performance windows, prepayment, and competing events

## Part III - Regulation, accounting, and responsible lending

13. Basel standardised and IRB approaches; PD, LGD, EAD, maturity, and risk weights
14. IRB estimation requirements, long-run averages, downturn LGD, defaulted assets, and margins of conservatism
15. IFRS 9 general and simplified approaches; staging, SICR, lifetime ECL, POCI, modifications, and write-offs
16. CECL scope, lifetime loss methods, reasonable and supportable forecasts, and reversion
17. Reconciling pricing PD, IFRS 9 PD, IRB PD, and management views
18. Fair lending, data protection, adverse-action reasons, consumer protection, and high-risk AI

## Part IV - Data engineering, governance, and quality

19. Source systems, bureau and alternative data, APIs, batch and streaming architecture
20. Data contracts, lineage, metadata, identifiers, as-of joins, and point-in-time correctness
21. Public and synthetic datasets: selection, licence, attribution, and limitations
22. Data-quality dimensions, rules, severity, reconciliation, and issue management
23. Missingness mechanisms, outliers, duplicates, contradictions, and measurement error
24. Sampling, decision bias, reject bias, survivorship, class imbalance, and target leakage
25. Cohorts, vintages, delinquency buckets, roll rates, transitions, cure, and recovery panels

## Part V - Exploration and representation

26. Reproducible EDA by time, product, segment, and outcome
27. Transformations, binning, WOE/IV, encoding, scaling, and monotonicity
28. Behavioural, RFM, trend, ratio, rolling, graph, and macroeconomic features
29. Feature selection: filters, regularisation, wrappers, stability, business relevance, and BART
30. Feature stores, training-serving consistency, and feature validation

## Part VI - PD, scoring, and ratings

31. Application and behavioural scoring frameworks
32. Logistic regression, maximum likelihood, uncertainty, and diagnostics
33. Scorecards, scaling, reason codes, policies, overrides, and fraud-scorecard separation
34. Trees, random forests, gradient boosting, monotonic ML, and benchmarking
35. Neural networks, self-organising maps, and when complexity is justified
36. Bayesian PD, low-default portfolios, external information, and conservative estimation
37. Survival, discrete-time hazard, AFT, competing risks, and lifetime PD term structures
38. Discrimination, calibration, ranking, cost, profit, and uncertainty metrics
39. Calibration, central tendency, rating grades, master scales, migration, and overrides
40. Reject inference, treatment effects, selection models, fairness testing, and counterfactual explanations

## Part VII - LGD, EAD, and expected credit loss

41. LGD data, workout cash flows, costs, discounting, cures, incomplete recoveries, and downturn conditions
42. LGD models: two-stage, fractional, beta, mixture, survival, and calibration
43. EAD and CCF data, drawdown, limits, cancellations, behavioural exposure, and calibration
44. PD-LGD-EAD dependence and coherent scenario simulation
45. IFRS 9 ECL engine: staging, scenario weights, discounting, overlays, reconciliation, and disclosures
46. CECL engine: vintage, roll-rate, DCF, loss-rate, WARM, and forecast reversion examples

## Part VIII - Portfolio, counterparty, and stress risk

47. Portfolio aggregation, concentration, granularity, and dependence
48. Vasicek intuition, Credit VaR, Monte Carlo, and capital allocation
49. Counterparty exposure, netting, collateral, wrong-way risk, and potential future exposure
50. CVA, DVA, and SA-CCR implementation overview
51. Macroeconomic scenarios, satellite models, sensitivity, reverse stress, and climate/ESG extensions

## Part IX - Decisions and optimisation

52. Cut-offs, approval rates, risk appetite, confusion costs, and constrained optimisation
53. Risk-based pricing, profitability, RAROC, affordability, and capital-aware decisions
54. Credit limits, line management, collections, and treatment allocation
55. Bandits and reinforcement learning with delayed outcomes, off-policy evaluation, and safety constraints

## Part X - Validation, implementation, and operations

56. Independent validation design and evidence standards
57. PD backtesting, calibration tests, discriminatory power, stability, and benchmarking
58. LGD/EAD/ECL validation, representativeness, sensitivity, and conservatism
59. UAT, data and integration testing, edge cases, parallel runs, and sign-off
60. Model inventory, materiality, ownership, documentation, change control, and audit
61. Packaging, model registry, CI/CD, containers, APIs, batch scoring, and security
62. Champion-challenger, shadow deployment, rollback, resilience, and incident response
63. Post-deployment data, prediction, calibration, outcome, fairness, and business monitoring
64. Redevelopment triggers, overlays, exceptions, retirement, and lessons learned

## Part XI - Governed agentic AI in credit risk

65. What is and is not an agent in a regulated credit system
66. Agents for data quality, lineage, modelling, validation, monitoring, documentation, and change triage
67. Tool permissions, segregation of duties, human approval, audit trails, and evidence provenance
68. LLM and agent risks: hallucination, prompt injection, data leakage, bias, instability, and unsafe actions
69. Agent evaluation, red teaming, scenario tests, observability, kill switches, and model-risk classification
70. A governed multi-agent reference architecture with deterministic controls and optional language reasoning

## Part XII - Integrated case studies

71. Retail application PD: UCI South German versus a permitted Kaggle teaching dataset
72. Credit-card behavioural PD and calibration using the UCI Taiwan dataset
73. Synthetic IFRS 9 portfolio from origination through staging, lifetime ECL, overlays, and monitoring
74. Synthetic revolving facility for EAD/CCF and dynamic limits
75. Synthetic default and recovery ledger for workout LGD, cure, survival, and downturn analysis
76. End-to-end deployment, shadow run, monitoring incident, governed agent triage, and human sign-off

## Appendices

- Repository, environment, and testing guide
- Dataset and licence register
- Mathematical notation and derivations
- Regulatory source map and version log
- Model-development, validation, UAT, monitoring, and agent-control templates
- API schemas, data contracts, model cards, run manifests, and audit-event schemas


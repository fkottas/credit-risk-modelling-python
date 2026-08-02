# Review and Viva Questions with Instructor Notes

These questions test whether a reader can defend choices rather than repeat definitions. The instructor notes identify essential elements, not a single permitted wording. Students should cite their case evidence, code and policy. Questions can be used for oral examination, model-committee role play or written review.

## Questions 1–6 — Foundations

### 1. Why is credit risk better represented as uncertain cash flows than only a default label?

**Instructor note.** Default classification omits timing, exposure, cure, recovery, cost and prepayment. Cash-flow paths connect economic value to PD, LGD and EAD while allowing classification as one component. A strong answer distinguishes expected value from realised path and avoids claiming the components are independent.

### 2. Why can `average PD × average LGD × total EAD` differ from account-level expected loss?

**Instructor note.** Weighting and alignment matter. Account-level products preserve dependence and exposure. Unweighted or separately exposure-weighted averages can lose covariance. A student should demonstrate with numbers and label any constructed portfolio loss rate rather than call it a unique portfolio PD/LGD decomposition.

### 3. What changes when a common macro factor is added to independent defaults?

**Instructor note.** Unconditional expected defaults can remain similar while clustering increases variance and tail loss. The answer connects systematic dependence to unexpected loss/capital and notes that the factor model itself requires calibration and sensitivity.

### 4. When should credit risk be formulated as classification, regression, survival or competing risks?

**Instructor note.** The estimand determines the formulation: horizon event, severity, event time with censoring, or multiple mutually exclusive events. A good answer defines row denominator and information timing and does not force one dataset to answer incompatible targets.

### 5. What does a logistic coefficient mean after WOE transformation?

**Instructor note.** It is a conditional change in bad log odds per unit WOE, given other variables and the declared WOE/event convention. It is not causal. Sign should be interpreted with convention; binning and selection uncertainty affect inference.

### 6. Why must a baseline model be connected to a decision simulation?

**Instructor note.** Predictive metrics do not determine cutoff, value, capacity or customer safeguards. A simple calibrated benchmark reveals whether complexity adds material decision benefit. Policy remains separate from probability estimation.

## Questions 7–12 — Products and policy

### 7. Why can the same “default” target behave differently for an instalment loan and credit card?

**Instructor note.** Amortisation, undrawn exposure, line management, minimum payment, fees and prepayment differ. Features and EAD mechanisms change. The answer begins from product terms and lifecycle rather than copying a model.

### 8. What hierarchy is needed for SME/corporate modeling?

**Instructor note.** Obligor/group, facility, guarantee/collateral, financial statement and default episode require keys. Default may aggregate at obligor while EAD/LGD remain facility-specific. Duplicate borrowers and statements are a major risk.

### 9. Why is missing bureau history not evidence of low risk for thin-file applicants?

**Instructor note.** Absence can reflect no history, match failure, channel or policy selection. Treat it explicitly, assess missing mechanism and use bounded policy. Alternative data need lawful, necessary and proxy-risk review.

### 10. Separate affordability, fraud and credit risk in a BNPL example.

**Instructor note.** Credit risk estimates repayment/default, affordability assesses ability without hardship, fraud assesses identity/intent, and operations handle payment failures. They may share evidence but have different labels, owners, rules and reasons.

### 11. Why does a green label not automatically justify a lower PD?

**Instructor note.** Environmental eligibility and credit performance are distinct. Any risk relationship needs representative data and control for selection/product differences. Claims also need evidence, use-of-proceeds and monitoring to avoid misrepresentation.

### 12. What is the role of overrides in credit policy?

**Instructor note.** Overrides handle limited documented information outside the model within authority. They are not hidden model corrections. Preserve model recommendation, reason, approver, final decision and performance; monitor direction, concentration and bias.

## Questions 13–18 — Regulation and accounting

### 13. Why keep internal, Basel and IFRS default/stage flags separate?

**Instructor note.** Perimeter, purpose, trigger, cure and timing may differ. Separate reasoned flags allow reconciliation and prevent one definition from silently contaminating target, staging or capital.

### 14. Why must IRB asset class be approved before formula execution?

**Instructor note.** Prescribed correlation and treatment depend on classification, criteria and permission. Code cannot infer legal eligibility from a label. A numerically correct wrong branch creates wrong RWA.

### 15. What is the IRB use-test intuition?

**Instructor note.** Ratings/parameters should be embedded in risk management and not exist solely for regulatory capital. Governance includes assignment, review, overrides, credit processes, monitoring and evidence consistent with regulatory requirements.

### 16. Why is SICR not only a PD-ratio threshold?

**Instructor note.** IFRS 9 is principle-based and considers reasonable/supportable quantitative and qualitative information, DPD backstops and credit-risk change since initial recognition. Thresholds are entity policy, not universal bright lines [R5, R6].

### 17. Why can one calculation engine not make IFRS 9 and CECL identical?

**Instructor note.** Shared cash-flow components do not erase different scope, staging/perimeter, contractual term, forecast/reversion and accounting presentation. Qualified accounting policy configures use [R7, R15].

### 18. What makes credit-scoring AI a high-consequence use?

**Instructor note.** It can affect access, price and treatment of essential financial services and may fall under specific legal regimes. Lawfulness, data, fairness, explainability, human review, contestability, robustness and records matter beyond model performance.

## Questions 19–24 — Data

### 19. What evidence proves a public dataset can be used in this book?

**Instructor note.** Canonical publisher page, creator, DOI, explicit licence/terms, attribution, retrieval date, modifications and redistribution decision. Public visibility alone is insufficient; current terms control.

### 20. Why retain both event and availability time?

**Instructor note.** A fact may describe an earlier event but arrive after the decision. Point-in-time development must reproduce what production could know, including late corrections. Both clocks support leakage tests and historical reconstruction.

### 21. What is a data contract’s most important function?

**Instructor note.** It makes expected grain, meaning, timing and acceptable values executable and assigns response. A contract that reports critical failure without stopping the run is incomplete.

### 22. Can observed data prove that missingness is not MNAR?

**Instructor note.** Generally no. Diagnose patterns and compare mechanisms, but dependence on unobserved values is not identifiable without assumptions or additional information. Use sensitivity and document uncertainty.

### 23. Why should outlier treatment preserve raw values?

**Instructor note.** Impossible, rare valid and risky extremes require different actions. Retaining raw and rule/reason supports audit, source repair, sensitivity and avoids hiding behavior through caps.

### 24. Give a data defect that calibration monitoring may miss.

**Instructor note.** Category recoding can route values to `OTHER` while short-term aggregate calibration appears stable; unit changes may be offset by other features. Schema, distribution and row-level controls detect earlier.

## Questions 25–30 — Scorecards

### 25. What must a characteristic slide show before approval?

**Instructor note.** Definition/timing, fixed-bin counts/shares/goods/bads/bad rate/WOE/IV/points, time/sample stability, missing/special behavior, rationale, concerns and decision. IV alone is inadequate.

### 26. When are manual bins preferable to automatic bins?

**Instructor note.** When stable operational thresholds, contractual terms or risk mechanisms justify them and counts/events support them. Manual does not mean untested; compare out of time and test boundaries.

### 27. What does ChiMerge optimise—and what does it not?

**Instructor note.** It greedily merges adjacent bins with similar class composition under a chi-square heuristic. It does not guarantee globally optimal, causal, stable or legally acceptable bins.

### 28. Why does smoothing not solve a zero-event bin?

**Instructor note.** It prevents infinite WOE but adds a convention to sparse evidence. Sensitivity, merging or more data remain necessary. Smoothing value belongs in artifact/version.

### 29. How can IRLS converge to a poor model?

**Instructor note.** Numerical convergence addresses the chosen objective. Target leakage, invalid sample, wrong form, separation, unstable variables, calibration and decision use can still fail. Report convergence and adequacy separately.

### 30. What exactly reconciles in a scorecard?

**Instructor note.** Raw value maps to bin, WOE, coefficient contribution and points; characteristic points plus base equal raw total; rounding/clipping gives score; score maps back to odds/PD and grade; reasons match penalties.

## Questions 31–36 — PD and machine learning

### 31. Why is an out-of-time split not automatically unbiased?

**Instructor note.** Policy/population/source/target changes and incomplete outcomes can differ; repeated borrowers may leak; developers can repeatedly inspect it. It is valuable temporal evidence under documented design, not magic.

### 32. Distinguish AUC and calibration.

**Instructor note.** AUC ranks a random bad above a good; calibration compares predicted probabilities with event frequency. A model can rank well and systematically underpredict. Use separate metrics and plots.

### 33. Why should grade design include minimum defaults?

**Instructor note.** Very fine grades produce uncertain observed rates and unstable backtests. Grades balance differentiation, monotonicity, population/default support, use and stability.

### 34. When might XGBoost not become champion despite higher AUC?

**Instructor note.** Gain may be immaterial at the decision, while calibration, stability, data dependency, explanations, latency, monitoring or governance are worse. Compare total controlled benefit.

### 35. Why are SHAP values not causal reasons?

**Instructor note.** They allocate a model prediction relative to a background under assumptions. Correlation and model structure affect attribution. They explain modeled association, not intervention or legal justification [R27].

### 36. Why is reject inference uncertain?

**Instructor note.** Outcomes for declined applicants are unobserved and prior policy selects acceptances. Parceling/augmentation impose unverifiable assumptions. Treat as sensitivity and use experiments/external evidence where lawful.

## Questions 37–42 — Lifetime PD, LGD, and EAD

### 37. Why can default count divided by originations bias lifetime risk?

**Instructor note.** Cohorts have different follow-up and censoring. Kaplan–Meier uses risk sets at event times under censoring assumptions; competing prepayment may need cumulative-incidence treatment [R31].

### 38. State the identity linking hazard, marginal PD and cumulative PD.

**Instructor note.** Survival is the product of one minus prior hazards; marginal first-default probability is prior survival times current hazard; cumulative PD is one minus survival and equals marginal sum.

### 39. Why is zero observed defaults not zero PD?

**Instructor note.** A finite low-default sample supports an upper uncertainty bound, not impossibility. Use pooling, external evidence, Bayesian/credible assumptions, floors and named conservatism as appropriate.

### 40. Why discount recoveries to default date?

**Instructor note.** Workout LGD measures economic loss and later cash has lower present value. State rate/day-count and include eligible costs. Different accounting/regulatory conventions require mapping.

### 41. What bias arises from using only completed recovery cases?

**Instructor note.** Quick resolutions may differ from long unresolved defaults, so matured-only selection can under/overstate loss. Show recovery development, unresolved share and completion sensitivity.

### 42. Why can raw CCF exceed 100%?

**Instructor note.** Small reference undrawn, over-limit balances, interest/fees or line changes can make drawdown exceed reference undrawn. Investigate and preserve raw values; validate currency EAD.

## Questions 43–48 — IFRS 9 and stress

### 43. Why use marginal rather than cumulative PD in period ECL?

**Instructor note.** Period terms represent first default in that period; cumulative probabilities overlap. Marginal PDs sum to cumulative lifetime risk and avoid double counting.

### 44. Why retain all stage reason flags?

**Instructor note.** Precedence chooses a primary reason, but multiple quantitative, qualitative, backstop and default indicators support audit, movement and policy assessment. A stage number alone hides why.

### 45. Why is ECL under weighted-average parameters not always probability-weighted ECL?

**Instructor note.** PD/LGD/EAD relationships, transformations and products are nonlinear. Calculate each coherent scenario and weight losses unless the equivalence is proved.

### 46. How does prepayment affect ECL?

**Instructor note.** It changes contractual/expected exposure and cash-shortfall timing and competes with default. Assumptions may vary by scenario. It is not simply another discount factor.

### 47. What makes an overlay governable?

**Instructor note.** Specific gap/evidence, scope, method, amount/sign, double-count check, owner, approval, effective/expiry, backtest and release. Keep it separate from base model output.

### 48. Why is stress testing not forecasting?

**Instructor note.** Stress conditions assess sensitivity/resilience under specified paths, often severe but plausible, rather than assign best-estimate likelihood. Narratives, propagation and constraints must be coherent.

## Questions 49–54 — IRB, portfolio, and counterparty

### 49. What should an IRB audit row expose?

**Instructor note.** Asset class/permission, inputs before/after floors, correlation, maturity adjustment, K, RWA, parameter/formula versions and regulatory adjustments. It must reconcile to source/report.

### 50. Why can retail and corporate exposures with equal PD/LGD/EAD have different RWA?

**Instructor note.** Prescribed correlation and maturity functions differ by asset class. Classification criteria and framework implementation drive the formula branch.

### 51. What is a defensible margin of conservatism?

**Instructor note.** A named adjustment linked to identified data/method uncertainty with evidence, quantification, no double counting, remediation and review. It is not an arbitrary buffer.

### 52. Why does correlation increase tail loss but not necessarily expected loss?

**Instructor note.** Dependence clusters defaults in adverse states while unconditional marginal PD can stay fixed. The mean is driven by marginals; variance/high quantiles by dependence.

### 53. What does HHI miss?

**Instructor note.** It summarises exposure concentration but not PD/LGD, common sectors, guarantees, geography or dependence. Use top-name/sector and stress contributions alongside it.

### 54. Why is counterparty netting a legal-data question before a formula question?

**Instructor note.** Offsetting requires enforceable agreement and correct netting-set scope. Similar names or economic relationship do not authorise netting; collateral timing and disputes also matter.

## Questions 55–60 — Validation and decisions

### 55. Distinguish repeatability from independent validation.

**Instructor note.** Repeatability reruns the same process. Independent validation challenges purpose/data/method and reproduces samples or benchmarks with sufficient independence. Both are necessary evidence.

### 56. Why can an assigned grade PD outside a binomial interval be inconclusive?

**Instructor note.** Dependence, multiple testing, representativeness, weighting and materiality complicate a simple test. Exact intervals are evidence, not the whole validation decision.

### 57. Why validate LGD/EAD in currency and percentage?

**Instructor note.** Percentage error treats tiny and large exposures equally; currency error shows financial impact. Both can reveal segment bias and concentration.

### 58. Why is maximum expected profit not automatically the approved cutoff?

**Instructor note.** Assumptions are uncertain and policy must satisfy affordability, customer protection, capital, concentration, capacity and risk appetite. Prefer robust, governed decisions.

### 59. How can risk-based pricing create adverse selection?

**Instructor note.** Higher-risk borrowers may accept high prices disproportionately and price can affect repayment burden/behavior. Static PD and take-up assumptions may fail; impose conduct/affordability controls.

### 60. Why is delayed default feedback difficult for reinforcement learning?

**Instructor note.** Rewards are censored/delayed, policies alter populations, exploration can harm customers and offline evaluation is confounded. Use constrained simulation and governed experiments.

## Questions 61–66 — Production and governance

### 61. What is training-serving parity at the strongest level?

**Instructor note.** Identical approved raw input yields matching transformation, prediction, calibration, score, grade and reasons under defined tolerance—not only similar aggregate performance.

### 62. Why is fail-open dangerous for missing credit data?

**Instructor note.** Silent defaults can change risk/customer outcomes without evidence. Use approved stop, manual or bounded fallback by error class and log reason/version.

### 63. What does a dependency lock not prove?

**Instructor note.** It improves reproducibility but not security, licensing, model validity or operational compatibility. Scan/review/test and manage updates.

### 64. Give three distinct causes of PSI increase.

**Instructor note.** Genuine population/economic shift, business policy/channel mix, or source/schema recoding. Responses differ; PSI alone cannot diagnose them.

### 65. Why use shadow deployment for a challenger?

**Instructor note.** It observes parity, disagreement, latency and stability on live-like inputs without customer impact. Promotion conditions and data controls are pre-approved.

### 66. Why can a one-line source change be more material than a large refactor?

**Instructor note.** Materiality follows output, definitions, customers and financial/regulatory impact. A refactor can be output-identical; source semantics can change the entire population.

## Questions 67–72 — Agentic AI and capstone

### 67. What distinguishes an agent from a single model response?

**Instructor note.** It observes state, selects actions/tools, may maintain memory and pursues objectives over a workflow. This autonomy increases tool/permission/trajectory risk.

### 68. What does an evidence hash prove?

**Instructor note.** It helps prove payload identity/integrity relative to the hash. It does not prove source authority, correctness, completeness or lawful access.

### 69. How should a quality agent handle prompt injection inside a column name?

**Instructor note.** Treat it as untrusted data. Base action on structured approved fields; deterministic policy ignores prose commands; log and red-team the event.

### 70. Why separate monitoring and validation agents?

**Instructor note.** Separation limits scope/conflict and mirrors specialist responsibilities. Neither approves the other; humans receive cited combined evidence and decide.

### 71. What is an automatic agent release blocker?

**Instructor note.** Any prohibited action, unlogged material write, secret/restricted-data exposure or approval bypass. Correct final prose does not rescue an unsafe trajectory.

### 72. What single principle should the capstone demonstrate?

**Instructor note.** End-to-end controlled integration: lawful and point-in-time data; compatible definitions; tested/reconciled models; separate policy/authority; independent challenge; safe deployment/monitoring; bounded agents; reproducible evidence.

## Oral-examination scoring guide

Score each response on four dimensions from zero to three: definition accuracy; connection to data/code evidence; treatment of limitations/alternatives; and governance/authority. A maximum response uses a concrete case and reconciliation, not jargon. A technically correct answer that ignores lawful use, information timing or customer/accounting/capital authority cannot receive full credit. Ask follow-ups at boundaries: “Which field proves that?”, “What would fail the run?”, “Who approves it?”, and “How would a validator reproduce it?”

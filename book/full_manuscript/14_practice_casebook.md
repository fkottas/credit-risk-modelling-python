# Practice Casebook — Seventy-Two Worked Assignments

This casebook turns every chapter into an evidence-producing assignment. Each case names an analytical question, a reproducible procedure and the conclusion that a student must defend. Instructors can run the cases in sequence or select a path for retail PD, corporate IRB, impairment, portfolio risk, model operations or agent governance. Expected results are expressed as checks and interpretation rather than a single number, because seeds and student policy choices may vary.

## Cases for Part I — Mathematical and Statistical Foundations

### Case 1 — Cash-flow uncertainty map

Create twelve contractual monthly instalments for a synthetic personal loan. Add three mutually exclusive paths: timely payment, default followed by partial recovery, and full prepayment. Compute discounted cash flows per path and their probability-weighted value. Separate credit loss from funding income and opportunity cost. The evidence pack contains the path table, probabilities, discount convention and a reconciliation to the contractual present value. The analytical question is why a binary default target cannot describe timing, prepayment and recovery severity simultaneously. Challenge the probabilities by doubling the default path and explain which cash flows change expected loss and which change revenue.

### Case 2 — Expected versus unexpected loss

Simulate 10,000 one-year portfolio outcomes from 2,000 identical loans with PD 2%, LGD 40% and EAD 10,000. Compare the mean loss with `PD × LGD × EAD × accounts`, then estimate the 99.9th percentile and unexpected loss. Repeat after adding a common macro factor that raises all conditional PDs together. The mean may remain similar while the tail expands. Submit a histogram, empirical quantiles, simulation error and seed. Explain why pricing/provision language and capital language must not be interchanged, and why independent defaults understate systematic portfolio risk.

### Case 3 — Dependence stress

Generate account PD, LGD and EAD so that stressed borrowers have higher values for all three. Compare the average of account-level products with the product of portfolio averages. Then shuffle LGD and EAD independently and repeat. The difference estimates the practical effect of dependence under the simulated design. Do not claim causality from correlation. Report Pearson and rank correlations, conditional means by PD decile, and both loss estimates. State whether a top-down multiplier can reproduce the joint tail or only its mean.

### Case 4 — Classification, regression, and survival views

Use one synthetic cohort to construct three targets: default within twelve months, workout LGD among defaults, and observed time-to-default with censoring. Draw an observation/performance-window diagram and list which rows enter each problem. Fit a logistic benchmark, a bounded LGD benchmark and Kaplan–Meier curve. The deliverable compares denominators: all eligible accounts for PD, defaulted cases for LGD, and eligible at-risk accounts for survival. Explain how using post-default recoveries as an origination feature would leak future information.

### Case 5 — Logistic probability mechanics

Choose an intercept and two coefficients for debt-to-income and recent enquiries. Calculate the linear predictor, odds and probability by hand for five applicants, then verify with NumPy. Increase one variable by one unit and interpret its odds ratio while holding the other constant. Repeat after standardising the variable and show why the coefficient changes but probabilities do not. Test logits of plus/minus 1,000 to motivate stable sigmoid clipping. The report distinguishes mathematical interpretation from an unsupported causal claim.

### Case 6 — Baseline model as a decision component

Fit a one-variable and multivariable logistic benchmark to the original synthetic retail case. Use an out-of-time split, report AUC and Brier score, draw a calibration table, and map calibrated PD to a simple accept/review/decline simulation. Add expected margin and loss to calculate value under three cutoffs. The “best” predictive model need not give the best policy because price, capacity and error costs matter. Document that the policy simulation is not a lending recommendation and retain model reasons separately from policy reasons.

## Cases for Part II — Credit Products, Policy, and the Lifecycle

### Case 7 — Product term sheet to risk specification

Write a term sheet for a fixed personal loan: amount, term, amortisation, rate, fees, delinquency, prepayment and collections. Translate every item into a source field, feature or outcome. Mark values unavailable at decision time. Build five cash-flow paths and identify exposure at each month. The submission must show why a personal-loan model cannot be copied unchanged to a revolving card even when both targets are “default.” A policy owner signs the product definition before modeling begins.

### Case 8 — Revolving account dynamics

Load `synthetic_revolving` and calculate current utilisation, undrawn amount, maximum pre-default balance, raw CCF and EAD. Segment by starting utilisation and line-change flag. Inspect values below zero or above one before deciding whether to cap them. Compare mean raw CCF with aggregate drawdown divided by aggregate undrawn amount; explain the weighting difference. Propose monitoring for line increases, frozen lines and zero-undrawn accounts. The result is a clean development table and an exception table, never silent clipping.

### Case 9 — Mortgage state and collateral

Construct a synthetic mortgage with property value, lien rank, amortising balance, indexed collateral value, months in arrears and costs to sell. Calculate current and stressed loan-to-value. Define when a collateral observation becomes stale. Show how prepayment competes with default and changes remaining exposure. The exercise is intentionally a data design, not a production mortgage model. Students must identify jurisdiction-specific foreclosure timing and consumer-protection rules that cannot be inferred from the dataset.

### Case 10 — SME obligor and facility hierarchy

Create three facilities for one SME and two guarantees shared across them. Define obligor default, facility EAD and recovery allocation. Demonstrate the duplication produced by treating each facility as an independent borrower. Aggregate ratios at the correct financial-statement date, then attach facility terms. The evidence pack includes an entity–facility–collateral diagram, keys and reconciliation. Explain how a consolidated group default and a local legal-entity default could differ under policy.

### Case 11 — BNPL and thin-file policy

Design an educational BNPL strategy using only information available at checkout. Separate fraud, affordability, credit risk and operational failure. For a thin-file customer, mark missing bureau history as absence of evidence rather than good history. Create limit and manual-review rules with maximum exposure and velocity controls. Simulate approval and default rates by repeat-customer status. The report discusses selection bias from prior approvals and rejects any use of sensitive or unlicensed alternative data.

### Case 12 — Green lending claim control

Define a hypothetical energy-efficiency loan where the green label affects price. List evidence required to verify the use of proceeds and post-origination performance. Keep environmental eligibility separate from creditworthiness. Simulate missing certification and false-claim cases and specify whether they trigger review, repricing or reporting. The student must not infer lower default from the label without evidence. Deliver a claims register, source lineage and policy escalation path.

## Cases for Part III — Regulation, Accounting, and Responsible Use

### Case 13 — Default-definition mapping

Take five borrower histories containing DPD, bankruptcy, distressed restructuring, unlikeliness-to-pay and cure. Apply three written definitions: a modeling target, an IFRS staging policy and a Basel default policy. Produce separate flags and reasons rather than forcing them into one field. Reconcile differences and identify dates when each definition first becomes known. The assignment is successful when the student can explain why similar language does not guarantee identical perimeter, horizon or cure treatment.

### Case 14 — Standardised versus IRB decision tree

Build a decision table for corporate, bank, sovereign and retail exposures. For each, record whether the institution has permission to use IRB, the asset class, applicable input ownership and fallback. Do not calculate RWA until exposure classification is approved. Use the repository formula only for eligible illustrative rows and retain intermediate values. The committee question is whether formula correctness can compensate for a wrong asset-class mapping; the required answer is no.

### Case 15 — Stage assignment with reasons

Load the synthetic IFRS 9 schedule and create origination/current PD ratio, absolute PD increase, DPD, watchlist, forbearance and default flags. Apply `StagingPolicy`, then tabulate exposure and count by stage and primary reason. Perturb thresholds and show migration. Check that a defaulted account cannot remain Stage 1 and that cure follows policy. The report describes SICR as a multi-indicator judgement and avoids presenting a numerical threshold as the IFRS 9 standard itself [R5, R6].

### Case 16 — Twelve-month versus lifetime loss

For one amortising loan, construct marginal PD, LGD, EAD and discount factor by month. Calculate Stage 1 and Stage 2 ECL, highlighting which periods differ. Verify cumulative PD equals the sum of first-default marginal probabilities. Repeat for a bullet loan. The case demonstrates that lifetime ECL is not twelve-month ECL multiplied by remaining years. Submit a period table and exact account-level reconciliation.

### Case 17 — CECL adaptation memo

Start from the same cash-flow engine but write a separate US GAAP configuration memo: asset scope, contractual term, expected prepayment, forecast period, reversion, segmentation and qualitative adjustments. Identify elements that require accounting interpretation rather than a Python parameter. Compare the resulting conceptual perimeter with IFRS 9 staging. The assignment is not to declare one superior; it is to prevent a shared engine from erasing different accounting requirements [R7, R15].

### Case 18 — Responsible model feature review

Create a feature register containing necessity, source, decision-time availability, personal-data class, proxy risk, expected relationship, monotonicity, retention and owner. Add demographic variables only to a protected audit view where lawful; exclude them from the decision model unless qualified legal policy authorises use. Train a benchmark with and without a suspicious proxy and compare performance and subgroup outcomes. The conclusion must address legality, fairness, explainability and business necessity, not only AUC.

## Cases for Part IV — Lawful Data and Quality Engineering

### Case 19 — Licence evidence packet

Select two UCI datasets and one optional Kaggle dataset. Save canonical page, creator, DOI, licence, checked date and permitted redistribution in a machine-readable record. For Kaggle, record dataset-specific terms and require the student to authenticate and download it; do not commit the file automatically. Compare CC BY attribution with a source that has unclear terms. The safe outcome for ambiguity is link-only use or legal review, not an assumption that public visibility equals permission.

### Case 20 — Point-in-time join

Create application rows and a monthly bureau table. A naive join selects the latest bureau record, including observations after the application. Build a point-in-time join that selects the latest record at or before the decision timestamp and records age. Add a late-arriving correction whose event time precedes but ingestion time follows the decision. State whether the production system could have known it. Quantify the AUC difference between leaked and valid features and show that leakage can look like excellent modeling.

### Case 21 — Data contract failure

Define a contract for account ID, snapshot date, balance, limit, DPD, product and default flag. Include type, nullability, range, uniqueness, allowed values and cross-field constraints. Inject a duplicate key, negative limit, balance above a policy maximum, missing date and unknown product. Run quality checks and route critical failures to quarantine. A report with red metrics but a continued model run is a control failure; the assignment must demonstrate the stop condition.

### Case 22 — Missingness mechanism experiment

Generate one variable under MCAR, one under observed-segment-dependent MAR and one where missingness depends on the unobserved value. Compare complete-case, median-plus-indicator and simple multiple-model sensitivity. No test can prove MNAR from observed data alone. Report missing rates over time and target rate by missing flag. The student states assumptions and sensitivity range rather than selecting an imputation method by convenience.

### Case 23 — Outlier policy

Create income and utilisation with genuine heavy tails, data-entry errors and policy-valid extremes. Compare deletion, winsorisation, robust transformation and explicit special bins. Show how fitting caps on the full data leaks validation information. Retain before/after counts and row identifiers. The policy must distinguish an impossible value, a rare but valid customer and a high-risk value; each has a different treatment.

### Case 24 — Quality-to-model impact

Run the synthetic retail workflow on clean data and on five defect scenarios: 5% missing income, category recoding, a one-month timestamp shift, duplicate defaults and unit-scaled balances. Measure changes in rows, event rate, coefficients, AUC, calibration and approval simulation. Connect each metric shift to a source fault. The final control matrix identifies which defects should stop scoring, permit fallback or open a warning. A model-monitoring threshold alone cannot replace source-contract checks.

## Cases for Part V — From-Scratch Scorecard Engineering

### Case 25 — Characteristic analysis committee

Use the original synthetic retail sample and freeze development, validation and out-of-time windows. For eight candidate variables, create fixed-bin tables with count, share, goods, bads, bad rate, WOE, IV and points. Export the editable presentation and add definition, timing, stability and business rationale to each slide. Assign each feature `keep`, `merge`, `transform`, `investigate` or `exclude`. A high-IV post-decision variable must be excluded. The committee records dissent, so the final variable list is traceable to evidence rather than an undocumented analyst preference.

### Case 26 — Manual bins at operational boundaries

For utilisation, create cuts at 0%, 30%, 60%, 90%, 100% and above-limit. Treat missing and a legacy `-999` special code separately. For product, group categories only where their mechanics and observed risk support it. Apply the specification to exact boundaries, negative values, positive infinity and an unseen product. The expected evidence is a boundary test table and policy for `OTHER`. Compare bad-rate and WOE stability across time before accepting the business cuts.

### Case 27 — Automated binning tournament

Fit quantile, equal-width, ChiMerge and monotonic candidates on the development sample only. For each candidate, report number of bins, minimum population, minimum goods/bads, IV, monotonic violations, out-of-time PSI and boundary reproducibility. Repeat on twenty bootstrap samples to observe cut instability. Select the method per feature; do not force one algorithm over the entire model. The winner is the most defensible specification under policy, not necessarily maximum development IV.

### Case 28 — WOE calculation audit

Construct a four-bin feature including one bin with zero bads. Calculate good and bad distributions, good-to-bad WOE and IV by hand with smoothing 0.5. Repeat with smoothing 0.1 and reverse the WOE convention. Verify the library output exactly. Explain why smoothing prevents infinity but cannot create evidence in a sparse bin. The final memo fixes event sign and WOE sign in a prominent implementation contract.

### Case 29 — IRLS iteration trace

Fit the from-scratch IRLS model to three WOE variables and retain log-likelihood, gradient norm and coefficient change per iteration. Compare zero, small and larger L2 penalties. Cross-check probabilities against a trusted general logistic implementation within tolerance, while retaining the original estimator as the teaching artifact. Create a deliberately collinear feature to provoke instability, calculate VIF and show how the penalty affects coefficients. Report convergence separately from model adequacy.

### Case 30 — Score and reason reconciliation

Scale the logistic model to score 600 at good-to-bad odds 20 with PDO 50. Verify that doubling good odds adds 50 points. For twenty accounts, sum intercept and bin points to the raw total, then reconcile rounding and clipping to the final score. Map scores to eight grades and produce four adverse characteristic reasons. Cross a rating boundary by one point and test it. Preserve the model reason and a separate policy-decision reason.

## Cases for Part VI — PD, Machine Learning, and Calibration

### Case 31 — Observation and performance windows

Build monthly snapshots from origination through twenty-four months. Select one observation date per account and define default within the next twelve months. Enforce a data-availability timestamp on every feature. Create random and out-of-time splits and compare performance; explain why multiple snapshots from one borrower cannot be randomly divided without grouping. The deliverable includes a cohort waterfall and the number censored because the performance window is incomplete.

### Case 32 — Logistic benchmark with uncertainty

Fit raw-feature and WOE logistic models to the same valid sample. Report coefficients, approximate standard errors, bootstrap intervals, AUC, Brier, log loss and calibration by decile. Compare signs with economic expectations. Investigate rather than automatically remove a counterintuitive coefficient: correlation, selection and nonlinear form may be responsible. The conclusion states the population and horizon to which the probabilities apply.

### Case 33 — Decision-tree rule review

Train a shallow tree with minimum leaf event counts. Export its rules and calculate bad rate and population for every leaf in development and out-of-time samples. Identify splits that reproduce a policy threshold or exploit a fragile rare category. Prune or constrain the tree, then compare stability. A readable tree is not automatically explainable if features are poorly defined or post-decision.

### Case 34 — XGBoost challenger under common controls

Train XGBoost with a fixed seed, early stopping and monotonic constraints only where justified. Use the same feature cutoff, sample and target as the scorecard. Tune on validation, evaluate once on out-of-time data, and retain the search space. Calibrate the selected model and map PD to the same PDO score scale. Compare lift and economics, not just AUC. Label SHAP or sensitivity explanations correctly rather than calling them exact bin points [R27, R30].

### Case 35 — Hyperparameter selection leakage

Run a small grid for depth, learning rate and regularisation. First demonstrate the wrong procedure: select using the test sample repeatedly. Then use nested or development/validation selection and reserve the out-of-time sample for final evaluation. Record all trials. The case quantifies how test reuse inflates optimism and asks students to design a model registry entry that identifies the selected trial and rejected alternatives.

### Case 36 — Calibration and grade design

Create an intentionally miscalibrated score by shifting the event rate. Fit intercept-only recalibration, Platt scaling and isotonic regression on a calibration window. Evaluate reliability tables, Brier score and log loss out of time. Design grades with minimum population and defaults, then estimate grade PD and uncertainty. Avoid grades so fine that observed rates are meaningless. State whether the final PD is PIT, TTC-oriented or a hybrid and how it will be used.

## Cases for Part VII — Lifetime PD, LGD, and EAD

### Case 37 — Kaplan–Meier lifetime view

Create origination cohorts with default and censor dates. Calculate the Kaplan–Meier survival curve from risk sets and events by hand for the first six periods, then verify the library example. Compare cohorts with different follow-up lengths. A naive default count divided by originations understates later risk when censoring is material. Submit risk-set, event, censor and survival columns and explain the independent-censoring assumption [R31].

### Case 38 — Discrete-time hazard model

Expand accounts into account-month rows until default or censoring. Fit a logistic hazard with duration indicators and borrower features. Convert hazards into survival, marginal PD and cumulative PD, verifying all identities. Compare a feature’s effect at month 3 and month 18. Ensure features at each row were known then. The evidence pack includes row-count reconciliation to account histories and a curve monotonicity test.

### Case 39 — Low-default calibration

Use the synthetic corporate IRB case with few defaults. Pool years carefully, calculate long-run average and exact binomial intervals, and compare grade-level observed rates with assigned PD. Apply intercept calibration while preserving rank order. Add a named margin-of-conservatism component for data uncertainty and show the waterfall. The student must resist zero PD for a no-default grade and state how conservatism relates to an identified limitation.

### Case 40 — Workout LGD reconstruction

Load `synthetic_recovery`, select one default and independently rebuild discounted recoveries and workout costs from the ledger. Distinguish cure from recovery, collateral from unsecured cash and gross from net amounts. Calculate LGD at two discount rates and show timing sensitivity. Reconcile account results to portfolio totals. The data-quality report flags cash flows before default, missing types and incomplete observation windows.

### Case 41 — LGD model alternatives

On matured defaults, compare a mean benchmark, fractional response idea and two-part model for cure plus positive loss. Use out-of-time or vintage validation. Report bias, MAE, calibration by prediction band and tail behavior. Clamp predictions only as a documented implementation rule and retain unclamped diagnostics. Discuss how excluding incomplete cases creates selection bias and perform a sensitivity scenario for unresolved recoveries.

### Case 42 — EAD and CCF edge cases

Use revolving facilities to calculate raw CCF. Separate zero-undrawn, limit-decrease, over-limit, closed and default-before-reference cases. Compare account-weighted and exposure-weighted CCF. Fit a bounded baseline by utilisation segment and estimate final EAD as current drawn plus expected draw. Validate both CCF and currency EAD. A perfect CCF metric on tiny undrawn balances may have little monetary relevance, so report exposure-weighted error.

## Cases for Part VIII — IFRS 9, CECL, and Stress

### Case 43 — Scenario-weighted ECL engine

Construct upside, base and downside scenarios with explicit weights, PD and LGD multipliers. Run the engine and reconcile period detail to account, scenario and portfolio totals. Test that weights not summing to one fail. Compare probability-weighted ECL with ECL under the probability-weighted parameter average and explain nonlinearity. Retain the scenario vintage and approving committee in configuration metadata.

### Case 44 — SICR sensitivity matrix

Vary relative PD increase, absolute increase, DPD backstop and watchlist indicator across a grid. Report Stage 1/2 exposure, transfers and ECL. Identify cliff effects around thresholds and cases where qualitative indicators dominate. The analysis does not optimise staging to a preferred allowance. It assesses policy sensitivity and checks alignment with reasonable, supportable information and applicable accounting interpretation [R5, R6].

### Case 45 — Transition, cure, and roll rates

From monthly delinquency buckets, calculate count- and exposure-weighted roll matrices, cure rates and absorbing default transitions. Compare one-month and three-month movement. Reconcile opening bucket plus inflows minus outflows to closing bucket. Segment by vintage and product. Explain how operational collections changes can alter roll rates without changing origination quality.

### Case 46 — Overlay ledger

Create an overlay for a risk not represented in the model. Record evidence, affected portfolio, amount, sign, approval, effective date, expiry and backtest. Apply additive and multiplicative versions separately and show why they are not interchangeable. Reconcile base ECL, overlay movements and final allowance. At the next reporting date, require release, replacement or renewed approval; indefinite overlays fail the case.

### Case 47 — CECL forecast and reversion

Define a two-year reasonable-and-supportable macro forecast and a three-year reversion to a historical rate. Compare immediate, linear and mean-reverting approaches. Document forecast variable, source, coefficient and reversion mechanics. Attribute allowance differences to forecast and reversion. The assignment requires an accounting-policy memo because code cannot choose a compliant forecast horizon by itself [R7, R15].

### Case 48 — ECL stress attribution

Apply unemployment and property-price scenarios through satellite transformations to PD and LGD. Hold EAD constant, then add behavioural drawdown. Decompose total change sequentially and repeat in another order to show interaction effects. Use a declared allocation method for the final pack. Check that stress results preserve valid probabilities and cash-flow timing. Explain why stress is a conditional “what if,” not a forecast.

## Cases for Part IX — IRB, Portfolio, and Counterparty Risk

### Case 49 — Corporate IRB row reconstruction

Select one synthetic corporate exposure and calculate correlation, maturity adjustment, capital requirement and RWA by hand from the applicable Basel formula. Compare exactly with the library audit row. Change PD, LGD, maturity and sales one at a time and confirm the direction or explain nonlinearity. The submission cites the current Basel Framework chapter and states that local implementation, permission and floors require separate configuration [R1–R4].

### Case 50 — Retail asset-class branches

Create otherwise identical residential mortgage, qualifying revolving retail and other retail exposures. Run the asset-class formulas and compare prescribed correlations and RWA. Then misclassify each row deliberately to quantify impact. Formula tests should pass while the governance decision fails, demonstrating that technical correctness cannot detect a wrong legal classification. Require a signed exposure-mapping table before the calculation is accepted.

### Case 51 — IRB parameter waterfall

Start with observed grade defaults, estimate a central PD, calibrate to the long-run average and add named uncertainty components. For LGD, reconstruct workout loss, add downturn adjustment and conservatism. Store base, each adjustment and final value. Reject an unexplained blanket uplift. Show how the parameter changes RWA and expected loss. The committee evaluates whether every adjustment maps to evidence and whether double counting occurs.

### Case 52 — One-factor portfolio simulation

Simulate obligor defaults with a shared Gaussian factor and idiosyncratic shocks. Compare loss distribution under zero, moderate and high asset correlation while holding unconditional PD fixed. Report expected loss, percentile, expected shortfall and Monte Carlo uncertainty. Add exposure concentration and observe tail effects. Explain that the simulation is an educational approximation and that model specification, dependence and calibration dominate numerical precision.

### Case 53 — Concentration diagnostics

Calculate exposure shares, Herfindahl–Hirschman index and top-name/sector/geography concentrations for the synthetic corporate portfolio. Compare equal-weight and concentrated versions with the same average PD and LGD. Stress the largest sector and report loss contribution. Concentration is not captured by an average standalone score; the case connects underwriting, limits and portfolio governance.

### Case 54 — Counterparty netting case

Load synthetic counterparty profiles and aggregate trades under documented netting sets. Calculate current exposure and a simplified expected exposure profile with and without collateral. Apply a toy CVA integral using marginal default probability and discounting. Do not net across legal agreements merely because counterparty names match. The evidence pack includes legal-set identifiers, collateral timing and reconciliations. SA-CCR and regulatory CVA require the applicable full framework, not this introductory calculation [R33].

## Cases for Part X — Validation, Decisions, and Optimisation

### Case 55 — Independent reproduction

Give the validator a frozen artifact, configuration, input sample and requirements without the developer’s result table. Reproduce 100 row-level PDs, scores, grades and reasons; then independently calculate five cases from stored bins and coefficients. Investigate any mismatch beyond tolerance. Record code independence and shared libraries. A validator who reruns the same opaque notebook has tested repeatability, not independent implementation correctness.

### Case 56 — Calibration backtest

For each grade, compare assigned PD with observed defaults using exact binomial intervals, then assess portfolio calibration and discrimination. Distinguish statistical significance from materiality and dependence. Repeat by vintage and product. Define green/amber/red logic with actions before viewing results. A low-default grade with a wide interval is inconclusive, not automatically valid or invalid.

### Case 57 — LGD and EAD validation

Rebuild discounted cash flows and raw CCF on an independent sample. Compare prediction and outcome by band, segment and vintage, including incomplete cases. Report currency-weighted and account-weighted errors. Benchmark against simple segment means. Check the production transformation mapping. The validator identifies whether underprediction is model, data, discount, recovery-process or population shift before proposing remediation.

### Case 58 — Cutoff economics

Sort calibrated applicants by PD and simulate approval at a grid of cutoffs. For each, calculate booked volume, expected interest margin, operating cost, expected credit loss, capital charge and constrained profit. Add manual-review capacity and a minimum service requirement. Perform sensitivity to LGD and take-up. The optimal simulated cutoff is a policy input; customer protections, affordability, limits and strategy approval remain binding.

### Case 59 — Risk-based pricing with constraints

Calculate a break-even rate from funding, operations, expected loss, capital and target return. Add price elasticity and adverse selection sensitivity. Constrain maximum rate and customer segment differences under policy. Compare flat and risk-based price strategies. The case requires transparent component attribution and prohibits using a price increase to disguise an unacceptable affordability or credit decision.

### Case 60 — Contextual bandit sandbox

Build a simulated line-increase experiment with conservative eligibility, maximum change and delayed default feedback. Compare fixed policy, epsilon-greedy and upper-confidence-bound strategies. Measure reward and harm indicators, not just short-term spend. Introduce nonstationarity and show why offline evaluation is difficult. The agent cannot deploy the policy; this is a controlled simulation requiring human-approved experimentation and customer safeguards.

## Cases for Part XI — Deployment, Monitoring, and Governance

### Case 61 — Training-serving parity

Serialize the scorecard specification, coefficient vector, scale and rating map. Score the same golden rows in training code and a production-style entry point. Compare raw inputs, transformed bins, WOE, logit, PD, points and grade. Test missing, special, unseen and boundary cases. A model that matches aggregate AUC but differs on individual bins fails implementation validation.

### Case 62 — API contract and resilience

Define request/response schemas, type constraints, version fields, reason provenance, error codes and latency target. Test oversized batches, malformed fields, duplicate identifiers, timeout and unavailable feature service. Decide fail-closed, fallback or manual route per error class. Never substitute zeros silently. Log only permitted fields and mask sensitive data. The output identifies both model version and policy version.

### Case 63 — Container and dependency evidence

Build the environment from a clean checkout, run tests and generate a software bill of materials. Pin direct dependencies and record transitive versions. Scan for known issues according to institutional process. Rebuild on another machine and compare golden scores. Store secrets outside the image. The case separates reproducibility from security: a perfectly repeatable vulnerable image is still unacceptable.

### Case 64 — Drift triage

Create three monitoring months: population shift with stable model relation, calibration shift without large PSI, and source recoding. Calculate data contract failures, feature PSI, score PSI, AUC and calibration. Diagnose each scenario and propose collect-evidence, recalibrate, restrict, redevelop or source repair. No single drift threshold chooses the action. Include volumes and uncertainty before escalating.

### Case 65 — Champion–challenger shadow run

Run champion scorecard and calibrated XGBoost challenger on identical live-like inputs without letting the challenger affect decisions. Compare PD, grade, approval simulation, reasons, latency, missing handling and subgroup outcomes. Investigate material disagreements using feature and explanation evidence. Define promotion conditions before the comparison. A marginal AUC gain may not justify implementation and governance complexity.

### Case 66 — Model change committee

Present four changes: code refactor with identical output, input-source replacement, intercept recalibration and new model. Classify each under a change policy and specify testing, validation, UAT and approval. Use hashes and golden cases to support the refactor claim. A “small” change to a source or target can be more material than many lines of internal code. Record decision, conditions, owners and expiry.

## Cases for Part XII — Governed Agentic AI and Integrated Systems

### Case 67 — Autonomy classification

List ten candidate agents: data dictionary search, quality triage, report drafting, monitoring investigation, validation planning, cutoff recommendation, retraining, deployment, accounting posting and customer decision. Rate consequence and reversibility. Set maximum autonomy for each. The first five may be bounded read/proposal workflows; the latter material actions require approval or are prohibited. Defend the classification with specific harms rather than enthusiasm about capability.

### Case 68 — Tool and evidence cards

Define schemas for dataset reader, evidence registrar, issue drafter and report generator. Give each the narrowest scope, timeout and data class. Register one JSON quality report as hashed evidence and propose an issue. Demonstrate that changing the payload changes its hash. Explain that a hash proves identity, not truth. External text is untrusted data and cannot edit the system policy.

### Case 69 — Data-quality agent injection test

Create twenty quality reports, including five with column names or comments instructing the agent to ignore policy. Feed only structured metrics to the specialist and retain the raw text as untrusted evidence. Confirm critical contract failures propose quarantine pending approval, warnings propose an issue and injected commands do not change the action. Measure missed critical failures and unsupported statements.

### Case 70 — Monitoring and validation separation

Give a monitoring agent PSI/AUC evidence and a validation agent unresolved finding evidence. Confirm each uses its own allow-list and cannot approve the other. Generate a combined meeting pack that cites both evidence objects and marks missing information. Human owners decide action. Test stale evidence and an unknown agent name. The audit log must contain proposal, policy decision and evidence identifiers.

### Case 71 — Red-team release suite

Execute at least thirty attacks covering deployment, customer decision, retraining, evidence suppression, exfiltration, privilege escalation, replayed approval, proposal modification, poisoned retrieval and unavailable tools. Any prohibited action or unlogged write blocks release. Reviewers inspect complete trajectories, not only final prose. Retain model, prompt, tool and policy versions so the regression suite can be repeated after every material change [R11, R12].

### Case 72 — Integrated model committee

Assemble a team for one capstone portfolio: business, data, development, validation, accounting or capital, compliance, engineering, security and audit. Present the legal dataset packet, quality evidence, scorecard, challenger, calibration, component/ECL/IRB calculation, implementation tests, monitoring and agent red-team results. Every claim links to an artifact and commit. The committee may approve, condition, remediate or reject. Record dissent and outstanding limitations. Re-run the repository from a clean environment before sign-off.

## Casebook completion record

For each completed case, retain a one-page control sheet: student and reviewer; case number; dataset and licence; seed and commit; assumptions; output locations; reconciliations; exceptions; interpretation; limitations; and review outcome. This lightweight record teaches a habit that transfers to professional model inventories and evidence repositories. The purpose of the casebook is not to produce seventy-two disconnected answers. It is to show how one definition or data decision propagates into modeling, accounting, capital, customer treatment, implementation and governance.

# Chapter 13 — Basel Credit Risk Architecture: Standardised and IRB Approaches

## Purpose and structure

The Basel Framework addresses bank capital adequacy; it is not an accounting impairment standard and not a pricing manual. Credit-risk capital may be calculated under a standardised approach or, subject to requirements and supervisory permission, an internal ratings-based approach. The consolidated framework organises IRB overview and asset classes in CRE30, risk-weight functions in CRE31, risk components in CRE32 and minimum requirements in CRE36 [R1–R4]. National or regional law determines what applies to a particular institution.

Under IRB, PD, LGD, EAD and effective maturity enter prescribed functions. “Internal” does not mean that a bank may invent its own capital formula. The model estimates approved risk components, while regulation supplies functions, floors, eligibility and other constraints. Foundation and advanced variants differ in which parameters are institution-estimated for relevant exposure classes.

The standardised approach uses exposure classes, external ratings where permitted, loan-to-value and other prescribed risk drivers. It remains model-dependent operationally: exposure classification, collateral eligibility, due diligence and data quality require controlled systems.

The laboratory starts with the standardised identity $RWA=Exposure\times RiskWeight$ and implements it as a six-line function with boundary checks. Four risk weights make the exposure, RWA and 8% minimum-capital relationship visible. The IRB normal-distribution function is not imported here: it is derived term by term in Part IX, where asset class, correlation and maturity can be audited.

The output is a base teaching calculation. A regulatory engine must identify the exact framework version, jurisdiction, exposure class, applicable floors, supporting factors, expected-loss treatment, output-floor effects, transition rules and supervisory decisions.

## Policy controls

Maintain a regulatory interpretation inventory linking every rule to code, owner, legal text, effective date and test. Prevent model code from silently selecting asset class. Reconcile regulatory exposure to finance and risk systems.

**Lab.** Build a requirements-to-code matrix for CRE30, CRE31, CRE32 and CRE36. Mark which requirements are formulas, data definitions, governance or supervisory eligibility.

# Chapter 14 — Regulatory Default and IRB Asset-Class Definitions

## Definition precedes estimation

An IRB PD estimates the probability that an obligor reaches regulatory default over one year. Default is not simply any missed payment and not automatically the same as bankruptcy, write-off or IFRS 9 Stage 3. The applicable framework combines unlikeliness-to-pay indicators with a past-due backstop and detailed treatment of return to non-defaulted status. Institutions require consistent implementation across systems, products and legal entities [R2, R4].

Default data construction needs an obligor or facility identifier, reference date, default date, trigger, materiality, cure date, probation and multiple-default treatment. If one facility defaults, the contagion rule to other facilities must be explicit. Technical defaults and data corrections require governance, not deletion based on modeller preference.

Asset-class assignment affects risk-weight functions and parameter rules. Corporate, sovereign, bank, residential mortgage, qualifying revolving retail, other retail and specialised-lending treatments are not interchangeable. Retail treatment requires portfolio management characteristics; size alone is insufficient.

The laboratory implements the default definition as a transparent decision function returning both flag and trigger list. Past due, unlikeliness to pay and distressed restructuring remain separate evidence. Readers add materiality, contagion, probation, cure and correction cases as test fixtures before any default-definition component is reused.

Different correlations demonstrate why asset class cannot be chosen to optimise capital. Classification is a regulatory fact determined under approved rules.

## Data policy

Run daily default-identification controls, compare trigger sources and reconcile late flags. Backfill history only under documented corrections. Monitor default rate by definition version. A change in materiality threshold or cure rule can create an apparent model shift without economic change.

**Lab.** Create ten ambiguous cases involving arrears, bankruptcy filing, restructuring, distressed sale, deceased borrower and technical payment error. Apply a written decision tree and record evidence plus escalation.

# Chapter 15 — IRB Use Test, Rating Systems, and Governance

## The rating system must be used

IRB is not a capital-only calculation detached from management. The use test asks whether internal ratings and estimates play an essential role in risk management, approval, pricing, limits, monitoring, provisioning or capital allocation, as relevant. A high-quality statistical model can fail this test if staff ignore it or if ungoverned overrides determine outcomes.

A rating system includes methods, processes, controls, data collection and IT systems supporting assessment, grade assignment and parameter quantification. Governance must cover model ownership, independent validation, internal audit, senior management and board oversight proportionate to materiality. Documentation should explain judgement, not merely reproduce code.

The laboratory writes the grade backtest from a `groupby`: observations, predicted PD, observed rate, defaults and observed-to-expected ratio. Students calculate both grades by hand, then add exact intervals and a traffic-light policy as a separate layer. The mathematics remains visible and the policy cannot silently redefine the statistical result.

The exact interval is evidence, not an automatic pass/fail rule. Small grades have wide uncertainty; pooling may hide heterogeneity. Backtesting must consider overlapping horizons, multiple observations per obligor and economic conditions.

## Governance evidence

Track grade migrations, overrides, stale ratings, concentration and time since review. Minutes should record challenge and action. Validation must be independent from development and able to reproduce results. Audit examines whether the entire framework operates as designed.

**Lab.** Design a use-test dashboard with approval, pricing, limit, watchlist and override evidence. Define a trigger when operational behaviour diverges from the rating system.

# Chapter 16 — IFRS 9 Impairment, Staging, and Significant Increase in Credit Risk

## Accounting objective

IFRS 9 recognises expected credit losses using a three-stage general approach. Stage 1 generally recognises twelve-month ECL; Stage 2 recognises lifetime ECL after a significant increase in credit risk; Stage 3 covers credit-impaired assets with lifetime ECL and different interest-revenue treatment. Twelve-month ECL is the portion of lifetime losses associated with defaults possible in the next twelve months, not cash shortfalls expected only during that year [R5–R6].

SICR is assessed relative to credit risk at initial recognition using reasonable and supportable information. A PD ratio can be one indicator, but no universal doubling rule defines SICR. Delinquency backstops, watchlists, forbearance, qualitative information, low-credit-risk simplification and rebuttals require approved accounting policy.

The laboratory builds `assign_ifrs9_stage` directly. Its ordered conditions expose Stage 3 precedence, the DPD/watchlist/relative-PD Stage 2 indicators and the Stage 1 remainder. The output contains both stage and reason. Students then change one trigger at a time and design cure/probation state, rather than receiving a stage from a class whose rules are still unknown.

The function exposes every trigger and one primary reason. A real engine also needs cure and probation, modification, POCI, revolving-life, collateral and write-off policies.

The IASB completed its Post-implementation Review of IFRS 9 impairment in July 2024 and concluded that the requirements are working as intended, while identifying matters for targeted follow-up and continuing attention to credit-risk disclosures and application questions [R41]. This is not evidence that every implementation is comparable or well controlled. The engine must still document SICR judgement, forward-looking information, model changes, overlays and disclosure reconciliations.

## Control framework

Reconcile stage counts and balances to the ledger. Monitor transfers, cures and manual overrides. Backtest both stage assignment and ECL outcomes. Validate data lineage from source event to disclosure.

**Lab.** Compare absolute PD, relative PD, DPD and watchlist SICR rules. Show how each affects stage distribution and ECL, then write the policy rationale rather than selecting the lowest provision.

# Chapter 17 — CECL and Its Relationship to IFRS 9

## Similar objective, different architecture

US current expected credit losses recognise expected lifetime credit losses for assets in scope, using historical experience, current conditions and reasonable and supportable forecasts, followed by reversion where relevant. Unlike the IFRS 9 general model, CECL does not use Stage 1 and Stage 2 to switch between twelve-month and lifetime ECL. Scope, methods and presentation differ, so one engine should not merely rename fields [R7].

| Dimension | IFRS 9 general approach | CECL |
|---|---|---|
| Initial allowance | twelve-month ECL in Stage 1 | expected lifetime loss from initial recognition for assets in scope |
| Credit deterioration | SICR transfers Stage 1 to lifetime Stage 2; credit-impaired Stage 3 | no equivalent Stage 1/Stage 2 switch |
| Forecast | reasonable and supportable forward-looking information, often probability-weighted scenarios | reasonable and supportable forecast with reversion beyond the forecastable period as applicable |
| Interest and presentation | Stage 3 changes the interest-revenue basis; separate IFRS presentation rules | US GAAP scope, presentation and write-off requirements apply |
| Simplified cases | lifetime provision matrix may apply to eligible receivables | methods include loss-rate, vintage, roll-rate, PD×LGD and DCF where appropriate |

The distinction is architectural: IFRS 9 staging changes the loss horizon, whereas CECL normally begins with lifetime expected loss. Shared utilities for time, curves and reconciliation are useful; shared accounting configuration is not.

Permitted methods may include loss-rate, vintage, roll-rate, probability-of-default, discounted-cash-flow and other approaches appropriate to the asset. The method must capture contractual term, expected prepayments and relevant recoveries according to applicable guidance and policy.

FASB's post-implementation work continues to generate targeted amendments. ASU 2025-05 addresses measurement of credit losses for accounts receivable and contract assets, including a practical expedient and an accounting policy election for entities within its scope; its effective-date and transition provisions must be read from the issued standard [R42]. It is a narrow update, not a replacement for Topic 326 or permission to generalise a receivables expedient to lending assets.

For trade receivables under IFRS 9’s simplified approach, a provision matrix can estimate lifetime ECL by aging bucket, adjusted for forward-looking information. It is not a shortcut to avoid data validation.

The laboratory computes a CECL lifetime loss-rate example directly from exposure, historical rate and an explicitly named qualitative adjustment. It validates bounds and reconciles pool totals. The exercise then contrasts this lifetime-from-initial-recognition logic with the Stage 1/Stage 2 horizon switch under IFRS 9 before either accounting engine is constructed.

## Method governance

Document why a method fits product behaviour, data and forecast. Reconcile changes due to portfolio, model, forecast, reversion, write-off and overlay. Keep IFRS 9 and CECL configurations separate even if they share curves or data utilities.

**Lab.** Calculate lifetime loss using a provision matrix and a PD×LGD×EAD schedule. Reconcile differences to timing, segmentation, exposure and discounting.

# Chapter 18 — Consumer Protection, Fair Lending, Privacy, and High-Risk AI

## Predictive value is not sufficient permission

Credit models operate within consumer, discrimination, privacy, data-protection and AI rules. Requirements depend on jurisdiction, product, customer and use. A variable can be statistically predictive yet unlawful, unfair, non-actionable, unstable or impossible to explain. Proxy risk matters because removing a protected attribute does not remove information correlated with it.

Annex III 5(b) of the EU AI Act identifies AI systems intended to evaluate the creditworthiness of natural persons or establish their credit score as high risk, except AI systems used to detect financial fraud [R8, R64]. Classification is use-specific: a generic language model is not classified only by its name, and an exception cannot be assumed from a vendor label.

The **date is part of the legal statement**. As checked on 22 August 2026, the consolidated text dated 27 July 2026 provides that the Regulation generally applies from 2 August 2026, while Chapter III Sections 1–3 for systems classified under Article 6(2) and Annex III apply from **2 December 2027** [R64–R65]. This reflects the July 2026 amendment and replaces the older 2 August 2026 date still found in pre-amendment commentary. The book therefore distinguishes current classification and preparation duties from provisions whose application date has not yet arrived.

| Evidence label | Position as checked on 22 August 2026 | Design implication |
|---|---|---|
| binding classification | Annex III 5(b) covers specified natural-person creditworthiness and credit-score uses, with the fraud-detection exception | classify the intended use, not merely the algorithm |
| binding application date | Annex III high-risk rules in Chapter III Sections 1–3 apply from 2 December 2027 under the consolidated text | maintain a dated implementation plan and legal review |
| future applicable requirements | Articles 9–15 cover risk management, data governance, technical documentation, automatic logs, deployer information, human oversight, accuracy, robustness and cybersecurity | build evidence, logs and authority boundaries before go-live |
| author implementation choice | the course agent cannot approve, decline, price, change a limit or deploy a model | a deterministic gate and authorised human retain action authority |

GDPR Article 22 is a separate, already applicable control. It concerns decisions based solely on automated processing, including profiling, that produce legal or similarly significant effects, subject to stated exceptions and safeguards [R34]. In the *SCHUFA* judgment, the Court of Justice held that creation of a probability score can fall within automated individual decision-making where a third party draws strongly on that score to establish, perform or terminate a contractual relationship [R66]. A token human click is not necessarily meaningful intervention. A real workflow needs legal analysis of whether processing is solely automated, which exception or legal basis applies, the information and safeguards supplied, and how a person can obtain review and contest the result.

US and other jurisdictions may require specific adverse-action reasons. CFPB Circulars 2022-03 and 2023-03 state that creditors using complex algorithms remain responsible for specific and accurate principal reasons; opacity or a closest sample-form checklist is not a substitute [R44–R45]. Generic feature importance is not automatically an adequate reason. For nonlinear models, the repository labels sensitivity-based reason codes honestly instead of presenting them as logistic bin points.

The laboratory calculates approval rate, true-positive rate and false-positive rate by group from an explicit twelve-row decision table. Every denominator can be inspected. These diagnostics do not decide discrimination or approve model use; they trigger legal, policy and data review. Agent permission enforcement appears only in the final part, after the reader has built the decisions and evidence objects it must protect.

## Responsible-model policy

Define purpose, lawful basis, data minimisation, retention, access, explanation, human review, contestability and monitoring. Evaluate performance and outcomes by relevant groups with uncertainty. A disparity statistic begins investigation; it is not alone a legal conclusion. Preserve evidence for customers, validators, auditors and regulators without exposing unnecessary personal data.

**Lab.** Create a model card for a consumer score. Include prohibited uses, protected and proxy variables, explanation method, human-review route, retention, security, fairness tests and escalation.

> Part III separates accounting, capital and customer-protection objectives. Shared data and models do not make the governing definitions or approvals interchangeable.

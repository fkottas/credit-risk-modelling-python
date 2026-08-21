# Technical and Governance Glossary

Definitions below follow this book’s conventions and are not substitutes for official legal, accounting or regulatory definitions. Where a term has multiple uses, the model document must state the chosen meaning.

**Accuracy ratio (AR).** A rank-discrimination measure derived from the CAP curve, commonly related to AUC by `AR = 2 × AUC - 1` under the usual binary setting.

**Agent.** A system that observes context, selects actions or tools, may update state/memory and pursues an objective across a workflow. Autonomy and consequence determine governance.

**Agent card.** The controlled record of agent purpose, owner, evidence, tools, memory, permissions, evaluations, monitoring, fallback, change rules and kill switch.

**Allowance.** The accounting estimate recognised for credit losses under the applicable framework and policy; it may include model output and separately governed adjustments.

**Application score.** A risk score based on information available at an application decision, distinct from later behavioural information.

**Area under the ROC curve (AUC).** Probability that a randomly selected event receives higher predicted risk than a randomly selected non-event, subject to sample and tie handling.

**Backtest.** Comparison of prior predictions or parameters with subsequently observed outcomes under matched definitions, horizons, populations and maturity.

**Bad.** The adverse event class in a binary scorecard; this book uses target `1=bad/default`. The exact event definition must be documented.

**Basel IRB.** Internal Ratings-Based approach under the applicable Basel/local framework, subject to supervisory permission, minimum requirements and prescribed risk-weight functions.

**Behavioural score.** A score using account performance known after origination, such as utilisation and payment history, for account-management purposes.

**Binning.** Mapping a continuous or categorical characteristic into groups. Bins are learned on development and frozen for validation/scoring.

**Brier score.** Mean squared difference between predicted probability and binary outcome. Lower is better; it combines calibration and refinement effects.

**Calibration.** Agreement between predicted probability and observed event frequency for the defined population/horizon, assessed at portfolio and relevant group levels.

**Capital requirement (K).** In the IRB context, the prescribed capital term per unit exposure before the relevant scaling and other applicable adjustments.

**Cash shortfall.** Difference between contractual cash flows due and cash flows the entity expects to receive, discounted under applicable accounting policy.

**CCF.** Credit conversion factor relating expected additional drawdown to an undrawn commitment under a defined reference/default setup.

**CECL.** Current Expected Credit Loss methodology under US GAAP Topic 326; its scope and implementation differ from IFRS 9 staging.

**Champion–challenger.** Controlled comparison of the approved model with alternatives using compatible data, definitions and decision criteria. A challenger has no authority merely by outperforming one metric.

**Characteristic analysis.** Bin-level review of population, goods/bads, bad rate, WOE, IV, stability, points and business meaning for a predictor.

**ChiMerge.** Greedy algorithm merging adjacent bins with similar class distributions using a chi-square criterion, subject to population/event constraints.

**Competing risk.** An event such as prepayment that prevents or changes observation of the event of interest; it requires explicit estimand and method.

**Conservatism.** An adjustment for identified uncertainty under a defined policy. It must be evidence-based and not hide unresolved defects or double counting.

**CSI.** Characteristic Stability Index, often applying PSI-style comparison to a feature/characteristic distribution under fixed groups.

**Cumulative PD.** Probability of first default on or before a horizon. It is non-decreasing and equals the sum of consistent marginal first-default probabilities.

**Cure.** Return from default/delinquency to sustained performance under an approved duration and criteria; a temporary payment is not automatically cure.

**Data contract.** Executable agreement on grain, keys, definitions, timestamps, types, ranges, categories, nulls, lineage, owners and failure actions.

**Data leakage.** Use of information unavailable at the intended decision time or derived from the target/performance window, creating invalid apparent performance.

**Default.** Defined credit event for a particular purpose. Internal, accounting and regulatory default flags may differ and should be reconciled rather than conflated.

**Discount factor.** Multiplier converting a future cash flow to value at the selected reference date under a stated rate and timing convention.

**Downturn LGD.** LGD parameter reflecting adverse economic conditions under applicable regulatory requirements and evidence, distinct from an arbitrary stress multiplier.

**EAD.** Exposure at default under a defined horizon, product and accounting/regulatory/economic convention.

**ECL.** Probability-weighted discounted expected credit loss, calculated with compatible default probability, cash shortfall/LGD, exposure and scenario assumptions.

**Effective interest rate (EIR).** Accounting rate used under the applicable policy to discount expected cash shortfalls or present interest for relevant instruments.

**Evidence item.** Versioned source object with identifier, provenance, time, classification and digest used to support an analysis or agent proposal.

**Expected loss (EL).** Mean credit loss under defined conditions, often represented as `PD × LGD × EAD` when component definitions and dependence treatment are compatible.

**Exposure-weighted.** Aggregation in which each account contribution is proportional to an exposure amount; it answers a different question from account/obligor weighting.

**Feature availability time.** Time when information became available to the decision system, distinct from when the underlying event occurred.

**Forbearance.** Concession due to borrower financial difficulty under applicable definition/policy; it can be a qualitative credit-deterioration indicator.

**Grade.** Ordered risk category mapped from score/rating process. Grade PD, boundaries, population and use are institution-specific.

**Good.** Non-event class in the scorecard convention. “Good” means not observing the defined bad within the horizon, not a general customer judgment.

**Golden case.** Reviewed input with expected intermediate and final outputs used for implementation regression and independent reconciliation.

**Hazard.** Conditional probability/rate of first event in a period given survival to its start, depending on discrete/continuous-time convention.

**IFRS 9.** International Financial Reporting Standard governing classification/measurement, impairment and related financial-instrument requirements; official effective text and policy control.

**Information value (IV).** Sum across bins of distribution difference times WOE. It is sample/bin-dependent descriptive separation, not automatic variable approval.

**IRLS.** Iteratively reweighted least squares, a Newton-style algorithm for fitting logistic regression using gradients and information/Hessian approximations.

**Isotonic calibration.** Nonparametric monotonic mapping from score/probability to calibrated probability; flexible but potentially unstable with limited data.

**KS statistic.** Maximum separation between empirical score distributions of events and non-events under a specified sample and score direction.

**Lifetime PD.** Cumulative probability of default over remaining life or specified multi-period horizon under stated conditions and competing-event treatment.

**LGD.** Loss given default: economic/accounting/regulatory loss severity conditional on default under a defined recovery, cost, discount and exposure convention.

**Long-run average (LRA).** Default-rate central tendency across a sufficiently representative historical period under applicable regulatory estimation requirements.

**Margin of conservatism (MoC).** Named parameter adjustment for identified uncertainty/deficiency under regulatory policy, with evidence, no double counting and review.

**Marginal PD.** Probability of first default within a particular period from the initial population; equals prior survival times period hazard.

**Maturity adjustment.** Prescribed IRB transformation reflecting effective maturity for applicable exposure classes and bounded inputs.

**Model.** Quantitative method/system applying statistical, economic, financial or mathematical assumptions to transform data into estimates; inventory classification follows consequence, not label.

**Model risk.** Potential adverse consequence from model error, uncertainty, inappropriate use or control failure, including data, method, implementation and governance.

**Monotonic constraint.** Restriction requiring predictions or bins to move in one direction with a feature, used only with justified evidence and testing.

**Observation window.** Period from which input information is drawn before the model’s reference/decision time.

**Out-of-time validation.** Evaluation on a later period untouched by fitting/selection, useful for temporal evidence but still subject to population and outcome maturity.

**Overlay.** Separately governed adjustment to model output for an identified gap or exceptional risk, with amount, evidence, approval, expiry and release.

**PD.** Probability of the defined default event over a stated horizon, population and conditioning basis.

**PDO.** Points to double the good-to-bad odds on a score scale; factor equals `PDO / log(2)`.

**Performance window.** Future interval during which the target outcome is observed after the reference/decision point.

**PIT.** Point-in-time orientation responsive to current/forecast conditions, contrasted with through-the-cycle orientation; actual calibration may be hybrid and must be labeled.

**Platt scaling.** Logistic calibration of a model score/logit using an estimated intercept and slope on appropriate calibration data.

**Point-in-time join.** Join selecting only records available at or before each historical decision/reference timestamp under reproducible source rules.

**Policy engine.** Deterministic component mapping structured proposals and evidence to permitted/denied/approval-required states; it remains separate from language generation.

**Population Stability Index (PSI).** Sum of reference/current share difference times log share ratio over fixed bins, with explicit smoothing and non-universal interpretation.

**Prepayment.** Early repayment/termination changing cash flows, exposure and observation; it may be a competing event and can vary by scenario.

**Provision matrix.** Simplified loss-rate approach commonly used for eligible trade receivables under accounting policy, segmented and adjusted for forward-looking information.

**Quarantine.** Enforced state preventing an invalid data/model run from continuing to scoring, posting or reporting until authorised resolution.

**Rating migration.** Movement among ordered grades over time. Transition matrices require consistent states, interval and denominator and may include default/cure.

**Reason code.** Controlled explanation of key model characteristic penalties or policy rule outcomes. Model reasons and policy reasons retain distinct provenance.

**Recalibration.** Updating mapping from model output to probability/central tendency without necessarily changing rank model; it is a governed model change.

**Recovery.** Cash or other value received after default under a defined workout accounting/economic treatment, net/gross of eligible costs as specified.

**Reject inference.** Methods attempting to account for unobserved outcomes of declined applications; conclusions depend on strong, often unverifiable assumptions.

**Risk appetite.** Board/management-approved type and amount of risk the institution is willing to accept, translated through limits, policies and escalation.

**RWA.** Risk-weighted assets calculated under the applicable framework from exposures, risk weights/capital terms and relevant adjustments.

**SA-CCR.** Standardised Approach for Counterparty Credit Risk under the applicable Basel/local framework; requires complete legal/product treatment beyond toy exposure profiles.

**Score.** Monotonic numerical transformation of risk odds/probability under a declared scale; in this book higher score means lower estimated risk.

**Selection bias.** Difference between observed development sample and intended population caused by approval, booking, survival, data availability or other selection.

**SICR.** Significant increase in credit risk since initial recognition under IFRS 9 policy, assessed with relevant quantitative and qualitative information.

**Stage.** IFRS 9 impairment status determining applicable ECL treatment under policy; retain stage reason, not only number.

**Survival.** Probability of remaining free of the event through a horizon under the stated censoring/competing-risk setup.

**Synthetic data.** Artificially generated records with documented generator/provenance. They are not automatically private, representative or free of source rights.

**TTC.** Through-the-cycle orientation intended to be less sensitive to current conditions across the economic cycle, subject to definition and calibration evidence.

**Unexpected loss.** Loss above the expected amount associated with distribution variability/tail under a stated confidence, horizon and model; conceptually linked to capital.

**Use test.** Evidence that a regulatory rating system and estimates are embedded in meaningful internal risk management, subject to applicable requirements.

**UAT.** User acceptance testing that verifies implemented business, model, data, integration and operational requirements in the target environment.

**Validation.** Independent effective challenge of conceptual soundness, data, process, outcomes, implementation and governance, with finding management.

**Vintage.** Cohort grouped by origination/booking or another start period and compared at consistent age to understand maturation and performance.

**VIF.** Variance inflation factor measuring linear collinearity of a feature with other design variables; diagnostic rather than universal exclusion threshold.

**Watchlist.** Controlled qualitative/quantitative identification of exposures needing enhanced monitoring, often relevant to SICR and credit management.

**WOE.** Weight of evidence. This book uses `log(good distribution / bad distribution)`, so positive WOE indicates relatively lower observed risk.

**Workout cost.** Eligible direct/indirect cost associated with recovery/default resolution under the chosen LGD definition and accounting/regulatory policy.

## Control-language quick reference

Use **must** for mandatory control, **should** for a strong expectation with documented exception, and **may** for permitted choice. Use **estimate** for model output, **decision** for authorised policy outcome, **approval** for recorded authority, and **execution** for an external change. Do not say a model “approved” a customer or an agent “authorised” a deployment when it only generated a recommendation. Precise verbs reveal responsibility.

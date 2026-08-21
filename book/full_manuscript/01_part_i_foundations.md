# Chapter 1 — Credit Risk as Uncertain Cash Flows

## The decision problem

Credit risk is the possibility that contractual cash flows are not received in the amount or at the time expected. That definition is broader than binary default. A borrower may pay late, prepay, cure after delinquency, enter forbearance, draw an unused line shortly before default, or repay only after expensive recovery work. The economic loss depends on the path of cash flows and not merely on the final label.

For a single exposure, let (C_t) denote the contractual cash flow at time (t), (R_t) the cash actually received, (K_t) direct recovery cost, and (d_t) an appropriate discount factor. A cash-flow loss is

\[
L=\sum_{t=1}^{T} d_t(C_t-R_t+K_t).
\]

The familiar product $PD\times LGD\times EAD$ is a useful conditional expectation of this loss only when its three components share a compatible definition, horizon, population, reference date and economic basis. Combining a twelve-month PD, lifetime EAD and workout LGD from another segment does not create a meaningful expected loss.

## A worked lending example

A one-year loan has EAD of EUR 10,000, PD of 3% and LGD of 45%. Expected loss is EUR 135. If the performing margin after funding and operating cost is EUR 500, the simplified expected value is EUR 365. This does not mean that EUR 365 will be earned. In 97% of the stylised outcomes the account may perform; in 3% a loss near EUR 4,500 may occur. Pricing, capital and liquidity must address that distribution, while affordability and consumer law constrain which transactions should be offered.

The standalone Python laboratory below defines the complete `discounted_cash_shortfall` function. It creates each period's contractual shortfall, discount factor and present-value loss as visible columns before aggregation. Nothing is imported from the project library. The same source is committed as an executable Chapter 1 script so that a reader can change receipts, recoveries, costs and timing and inspect the resulting output.

The model output is an input to a decision, not the decision itself. A policy also needs eligibility, affordability, fraud, sanctions, concentration, pricing, product and customer-treatment rules. Those rules must be versioned independently so that a change in business appetite is not misreported as a model redevelopment.

## Controls and practice

Reconcile contractual balances to the finance system before modelling. State whether interest, fees, collateral proceeds and collection costs are included. Record the discount basis and treatment of negative loss. Do not silently clip observations until raw values have been explained and retained.

**Lab.** Use `synthetic_retail`. Calculate expected loss and expected value by product and risk decile. Change LGD and margin assumptions separately. Explain why ranking may remain unchanged while the economically optimal cutoff moves.

# Chapter 2 — Expected Loss, Unexpected Loss, and the Loss Distribution

## Mean loss is not capital

Expected loss is the probability-weighted average loss over repeated comparable exposures. Unexpected loss concerns dispersion around that mean, especially severe portfolio outcomes. Provisions, pricing and capital have different purposes; using the same number for all three obscures risk.

Let account loss be $L_i=D_i\times LGD_i\times EAD_i$, where $D_i$ is a default indicator. Portfolio loss is $L=\sum_{i=1}^{n}L_i$. Even if individual default probabilities are accurate, the portfolio tail depends on default dependence, concentration and the relationship between default, recovery and exposure. Under independence, idiosyncratic variation diversifies rapidly. Under a common downturn, many obligors deteriorate together and recovery values may fall at the same time.

Suppose 1,000 equal exposures each have EAD EUR 10,000, PD 2% and LGD 40%. Expected loss is EUR 80,000. If defaults were independent, the standard deviation of default count would be about √(1000×0.02×0.98)=4.43, but a systematic factor can make a count far above 20 plausible in a severe state. The Basel asymptotic single-risk-factor framework represents this effect through asset correlation and a 99.9% conditional default probability.

The laboratory implements `loss_distribution` directly with Bernoulli trials. It reports analytical expected loss, simulated mean, a 99% loss quantile and unexpected loss. Students first use three exposures small enough to calculate by hand, then increase portfolio size and add a common factor. The Basel calculation is deliberately postponed until the regulatory formula has been derived in Part IX.

The reported capital is not a forecast loss and the risk-weighted asset amount is not EAD. In the base formula, capital rate is the stressed conditional loss less expected loss, with a maturity adjustment for corporate exposures. Eligibility, floors, output-floor effects, provision treatment and jurisdictional changes remain outside the teaching function.

## Portfolio policies

A model-development policy should distinguish central-tendency estimation from tail measurement. A concentration policy should set limits by obligor, connected group, industry, geography, product, vintage and collateral. Stress testing should challenge parameters jointly rather than multiplying only PD while leaving LGD and EAD benign.

**Lab.** Generate `synthetic_corporate_irb`. Compare a granular portfolio with one in which the largest ten EADs are multiplied by ten. Expected loss per euro may change little, but the Herfindahl index and economic concentration risk increase.

# Chapter 3 — Dependence Between PD, LGD, and EAD

## Why multiplication is not enough

The identity $EL=\mathbb{E}[D\times LGD\times EAD]$ does not generally equal $\mathbb{E}[D]\,\mathbb{E}[LGD]\,\mathbb{E}[EAD]$. The latter factorisation assumes independence or uses parameters already defined conditionally in a compatible way. In downturns, obligors default more often, collateral values fall, recovery takes longer, and revolving borrowers may draw available limits. The three components can therefore move adversely together.

A practical scenario engine preserves account-level relationships. For scenario (s), period (t) and account (i), an ECL contribution is

\[
ECL_{i,t,s}=mPD_{i,t,s}\times LGD_{i,t,s}\times EAD_{i,t,s}\times DF_{i,t}\times w_s.
\]

Here marginal PD is the probability of first default in period (t), not the conditional hazard and not cumulative PD. Confusing these quantities double-counts default. The scenario weight (w_s) is applied after scenario-consistent parameter paths are built.

The laboratory builds a common-factor experiment from NumPy primitives. Default, LGD and EAD all respond to the same simulated systematic state, and the code prints component-loss correlation, mean loss and a tail quantile. This is intentionally simpler than an ECL engine: the purpose is to make dependence visible before scenario classes or reusable calculation objects exist.

The library scales conditional hazard rather than directly multiplying marginal probability. This keeps the curve in the probability domain and reconstructs scenario marginal PD consistently. LGD is bounded only in the model layer, while raw workout observations remain available elsewhere.

## Validation questions

Check whether scenarios affect the same economic drivers across PD, LGD and EAD. Ensure collateral haircuts do not duplicate a downturn LGD adjustment. Reconcile EAD to contractual schedules or limit histories. Test whether the sum of marginal PD remains at most one and whether account, scenario and detail ECL totals agree.

**Lab.** Compare three engines: independent average parameters, account-level correlated scenarios, and a deliberately incoherent engine that uses cumulative PD in every period. Quantify the overstatement from double counting.

# Chapter 4 — Time, Cohorts, Transitions, and Competing Events

## The time axis is part of the target

A default label without a reference date and horizon is incomplete. Application PD may ask whether an accepted applicant defaults within twelve months of origination. Behavioural PD may use monthly snapshots and a twelve-month performance window. IFRS 9 lifetime PD follows the remaining contractual life and must interact with prepayment, cure and maturity. IRB one-year PD has a regulatory definition and calibration objective.

For a cohort originated in month (v), vintage analysis tracks cumulative default by months on book. It separates maturation from calendar conditions. A 2025 vintage observed for six months cannot be compared directly with a 2021 vintage observed for thirty-six months. Calendar analysis instead aligns exposures by economic time; both views are needed.

Transition matrices describe movements among states such as current, 1–29 DPD, 30–59 DPD, 60–89 DPD, default, cure, prepayment and closure. Rows must have the same interval and population definition. Treating prepayment as non-default forever can bias lifetime risk because it is a competing event that removes exposure.

The laboratory constructs transition counts and row probabilities directly from an account-month table. Readers must show how the risk set changes, why each row sums to one, and where closure or prepayment removes an account. Kaplan–Meier, cause-specific hazards and cumulative-incidence estimators are introduced only after these counts are understood.

Kaplan–Meier handles right censoring when the event process and censoring mechanism are appropriately interpreted. It does not solve selection bias, cure definitions, left truncation or informative closure automatically. Competing-risk methods are preferable when different exit causes have distinct meaning.

## Temporal controls

All features must be available by the decision timestamp. Outcome windows must not overlap training features. Split data by time whenever dates exist, and leave a maturity buffer so test labels are complete. Store observation date, outcome-end date, extraction date and source-system effective timestamps.

**Lab.** Construct monthly vintages from the synthetic retail data. Produce cohort size, default rate and months of available performance. Then create a misleading comparison that ignores maturity and explain why it fails.

# Chapter 5 — Classification, Regression, Survival, and Multi-State Formulations

## Choose the estimand before the algorithm

Credit risk is not always a classification problem. Binary classification estimates an event probability over a fixed horizon. Regression estimates severity, utilisation, recovery amount, days past due or profit. Survival models estimate time to default under censoring. Multi-state models estimate movement among delinquency, cure, default and closure states. A model is correct only relative to its estimand and use.

For binary PD, logistic regression models log odds as $\beta_0+x^\top\beta$. A tree ensemble may improve nonlinear prediction but still needs calibration and governance. Workout LGD can require a two-stage model: probability of cure or full recovery followed by loss severity. EAD for revolving facilities may model CCF only where undrawn amount is positive. A lifetime engine may model discrete conditional hazard and derive marginal PD.

The public UCI Credit Approval dataset illustrates a crucial warning. Its outcome is approval, not default. It can teach mixed data types and missingness, but relabelling `approved` as PD would change the meaning of the evidence. Likewise, corporate bankruptcy is related to but not identical with a bank’s regulatory default definition.

The laboratory implements a clipped logistic transform and the identity between conditional hazards and cumulative PD. It prints classification probabilities, bounded LGD values and a lifetime curve. The extension asks the reader to define a linear-probability benchmark, a continuous-severity model, an ordinal delinquency model and a competing-risk estimand using the same miniature records, making the difference a matter of mathematics rather than library syntax.

## Model-selection policy

Start with a transparent benchmark. Compare candidates on out-of-time discrimination, probability accuracy, calibration, stability, uncertainty, economics, group outcomes and implementation burden. Complexity must answer a documented need. Do not select by a single cross-validation score if the deployment population, horizon or decision process differs.

**Lab.** For one business question, write four possible estimands: twelve-month default, time to first 90 DPD, loss severity after default and transition to cure. Specify the unit, risk set, censoring, features, label and validation metric for each.

# Chapter 6 — The Credit Model Operating System

## From model to controlled service

An end-to-end credit model has at least nine connected layers: source data; data contract and quality gate; sample and target construction; feature pipeline; estimation and calibration; score or parameter output; policy and decision layer; implementation service; and monitoring/governance. A weakness in any layer can dominate algorithmic performance.

The repository’s baseline workflow demonstrates the chain. It loads a registered dataset, creates a teaching copy with deterministic defects, assesses quality, quarantines invalid rows under explicit rules, applies an out-of-time split where possible, fits a PD benchmark, calculates monitoring metrics, produces a simplified ECL illustration for the compatible synthetic case, and asks a bounded agent for a recommendation. It writes a manifest rather than only displaying a chart.

The laboratory writes `reproducible_run_id` from elementary JSON canonicalisation and SHA-256 hashing. Every input is visible, and changing one policy field changes the identifier. The end-to-end workflow and manifest classes are built much later, after the reader has created the individual data, model, validation and approval artifacts that a run manifest must reference.

The run manifest should include code version, dataset hash, environment, configuration, timestamps, row counts, exclusions, metrics and approvals. A production registry additionally needs owner, intended use, materiality, validation status, effective dates, dependencies, deployment endpoints and retirement status.

## Segregation of duties

Development, validation, approval, deployment and audit should be distinct responsibilities proportionate to model risk. Automated tests can confirm formulas and data contracts; they cannot approve judgemental policy. A model owner may accept business risk but should not rewrite validation conclusions. An agent may draft an issue but cannot close it without authority.

**Lab.** Draw the operating system for an application scorecard and for an IFRS 9 engine. Identify which artifacts are common and which require different owners, horizons, controls and approvals.

> Part I establishes the central idea used throughout the book: every number must be traceable to a defined cash-flow question, time horizon, population, policy and controlled implementation.

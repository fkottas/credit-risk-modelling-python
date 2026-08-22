# Chapter 1 — Credit Loss as a Cash-Flow Problem

## The decision problem

Credit risk is the possibility that contractual cash flows are not received in the amount or at the time expected. That definition is broader than binary default. A borrower may pay late, prepay, cure after delinquency, enter forbearance, draw an unused line shortly before default, or repay only after recovery work. The economic loss depends on the cash-flow path, not merely on the final default label. This distinction underlies pricing, accounting-loss and capital calculations, although each framework defines the relevant cash flows and horizon differently [R5, R14, R78].

For a single exposure, separate normal payments from post-default recovery proceeds. Let $C_t$ be the contractual cash flow due at month $t$, $P_t$ the regular payment received, $Rec_t$ eligible recovery proceeds, $K_t$ direct workout cost and $r$ the annual effective discount rate. With month-end timing, the discounted cash-flow loss is

\[
L=\sum_{t=1}^{T}(1+r)^{-t/12}
\left[(C_t-P_t)-Rec_t+K_t\right].
\]

The bracketed term is the period shortfall,

\[
\Delta C_t=(C_t-P_t)-Rec_t+K_t,
\qquad
d_t=(1+r)^{-t/12},
\qquad
L=\sum_{t=1}^{T}d_t\Delta C_t.
\]

This notation prevents a common sign error: recovery proceeds reduce loss, while eligible workout costs increase it. A system may instead define one signed receipt field, but it must not then subtract a separate recovery field a second time. The period convention also matters. If $t$ is measured in days, replace $t/12$ by the approved day-count year fraction; if the rate is monthly, do not divide the exponent by twelve again.

| Symbol | Business meaning | Unit and domain |
|---|---|---|
| $t,T$ | month and maximum contractual/workout horizon | integer; $1\le t\le T$ |
| $C_t$ | contractual amount due during month $t$ | currency; normally $C_t\ge0$ |
| $P_t$ | regular contractual payment received | currency; normally $P_t\ge0$ |
| $Rec_t$ | eligible post-default recovery proceeds | currency; $Rec_t\ge0$ |
| $K_t$ | eligible direct collection or workout cost | currency; $K_t\ge0$ |
| $r$ | annual effective discount rate | decimal; mathematically $r>-1$ |
| $d_t$ | present-value factor at the reference date | dimensionless; $d_0=1$ |
| $L$ | discounted raw cash-flow loss | currency; can be negative before policy treatment |

In the three-month example, $r=12\%$. Month 1 has no shortfall. Month 2 has $350-200-0+5=155$ and month 3 has $350-0-120+15=245$. Therefore

\[
L=0(1.12)^{-1/12}+155(1.12)^{-2/12}+245(1.12)^{-3/12}
=390.26\text{ EUR}.
\]

The hand calculation supplies three invariants for the code: a fully paid schedule with no cost has zero loss; increasing an eligible recovery while holding everything else fixed cannot increase loss; and, for $r>0$, a later otherwise identical shortfall has a smaller present value. Input validation must reject impossible periods, $r\le-1$, negative receipts or costs under this unsigned convention, and non-finite values rather than silently repairing them.

The familiar product $PD\times LGD\times EAD$ is a useful conditional expectation of this loss only when its three components share a compatible definition, horizon, population, reference date and economic basis. Combining a twelve-month PD, lifetime EAD and workout LGD from another segment does not create a meaningful expected loss.

## A worked lending example

A one-year loan has EAD of EUR 10,000, PD of 3% and LGD of 45%. Expected loss is EUR 135. If the performing margin after funding and operating cost is EUR 500, the simplified expected value is EUR 365. This does not mean that EUR 365 will be earned. In 97% of the stylised outcomes the account may perform; in 3% a loss near EUR 4,500 may occur. Pricing, capital and liquidity must address that distribution, while affordability and consumer law constrain which transactions should be offered.

The first Python implementation stores five values for each period and uses a `for` loop. It calculates the contractual shortfall, discount factor and present-value loss before aggregation. This elementary form allows the reader to change a receipt, recovery, cost or payment month and determine the expected direction from the equation before running the code.

The model output is an input to a decision, not the decision itself. A policy also needs eligibility, affordability, fraud, sanctions, concentration, pricing, product and customer-treatment rules. Those rules must be versioned independently so that a change in business appetite is not misreported as a model redevelopment.

## Controls and practice

Reconcile contractual balances to the finance system before modelling. State whether interest, fees, collateral proceeds and collection costs are included. Record the discount basis and treatment of negative loss. Do not silently clip observations until raw values have been explained and retained.

**Lab.** Use `synthetic_retail`. Calculate expected loss and expected value by product and risk decile. Change LGD and margin assumptions separately. Explain why ranking may remain unchanged while the economically optimal cutoff moves.

# Chapter 2 — Expected and Unexpected Credit Loss

## Mean loss is not capital

Expected loss is the probability-weighted average loss over repeated comparable exposures. Unexpected loss concerns dispersion around that mean, especially severe portfolio outcomes. Provisions, pricing and capital have different purposes; using the same number for all three obscures risk.

Let account loss be $L_i=D_i\times LGD_i\times EAD_i$, where $D_i$ is a default indicator. Portfolio loss is $L=\sum_{i=1}^{n}L_i$. Its variance is

\[
\operatorname{Var}(L)=\sum_{i=1}^{n}\operatorname{Var}(L_i)
+2\sum_{i<j}\operatorname{Cov}(L_i,L_j).
\]

The covariance terms explain why accurate individual PDs do not determine portfolio tail risk. Under independence, idiosyncratic variation diversifies as the portfolio grows. Under a common downturn, many obligors deteriorate together, utilisation can rise and recovery values can fall. Concentration magnifies this effect because a small number of large losses dominate the sum [R14, R32].

Suppose 1,000 equal exposures each have EAD EUR 10,000, PD 2% and LGD 40%. Expected loss is EUR 80,000. If defaults were independent, the standard deviation of default count would be about $\sqrt{1000\times0.02\times0.98}=4.43$, but a systematic factor can make a count far above 20 plausible in a severe state. The Basel asymptotic single-risk-factor framework represents this effect through asset correlation and a 99.9% conditional default probability.

The worked example starts with two exposures and enumerates all four joint default states. For each state it calculates the probability and loss, forms the loss distribution and identifies its 95th percentile. If $q_{\alpha}(L)$ denotes the $\alpha$-quantile, a simple teaching definition is $UL_{\alpha}=q_{\alpha}(L)-\mathbb{E}[L]$. This is not a universal regulatory definition, but it makes the distinction between the mean and the tail explicit before Monte Carlo simulation is introduced. The prescribed Basel calculation is derived separately in Part IX [R1–R4].

The reported capital is not a forecast loss and the risk-weighted asset amount is not EAD. In the base formula, capital rate is the stressed conditional loss less expected loss, with a maturity adjustment for corporate exposures. Eligibility, floors, output-floor effects, provision treatment and jurisdictional changes remain outside the teaching function.

## Portfolio policies

A model-development policy should distinguish central-tendency estimation from tail measurement. A concentration policy should set limits by obligor, connected group, industry, geography, product, vintage and collateral. Stress testing should challenge parameters jointly rather than multiplying only PD while leaving LGD and EAD benign.

**Lab.** Generate `synthetic_corporate_irb`. Compare a granular portfolio with one in which the largest ten EADs are multiplied by ten. Expected loss per euro may change little, but the Herfindahl index and economic concentration risk increase.

# Chapter 3 — Joint Behaviour of PD, LGD, and EAD

## Why multiplication is not enough

The identity $EL=\mathbb{E}[D\times LGD\times EAD]$ does not generally equal $\mathbb{E}[D]\,\mathbb{E}[LGD]\,\mathbb{E}[EAD]$. Let $X=D$, $Y=LGD$ and $Z=EAD$, with means $\mu_X,\mu_Y,\mu_Z$. Then

\[
\mathbb{E}[XYZ]=\mu_X\mu_Y\mu_Z
+\mu_X\operatorname{Cov}(Y,Z)
+\mu_Y\operatorname{Cov}(X,Z)
+\mu_Z\operatorname{Cov}(X,Y)
+\mathbb{E}[(X-\mu_X)(Y-\mu_Y)(Z-\mu_Z)].
\]

The product of marginal means is valid only when the covariance and higher-order dependence terms vanish, or when the parameters are already conditional on a common information set. In downturns, obligors default more often, collateral values fall, recovery takes longer and revolving borrowers may draw unused limits. The three components can therefore move adversely together.

A practical scenario engine preserves account-level relationships. For scenario $s$, period $t$ and account $i$, an ECL contribution is

\[
ECL_{i,t,s}=mPD_{i,t,s}\times LGD_{i,t,s}\times EAD_{i,t,s}\times DF_{i,t}\times w_s.
\]

Here marginal PD is the probability of first default in period $t$, not the conditional hazard and not cumulative PD. Confusing these quantities double-counts default. The scenario weight $w_s$ is applied after scenario-consistent parameter paths are built.

The worked example uses three macroeconomic scenarios. PD, LGD and EAD rise together from base to severe conditions, allowing comparison of scenario-consistent expected loss with the product of three separately weighted averages. Their difference isolates the dependence introduced by scenario co-movement. The accounting chapters later add requirements for reasonable and supportable forward-looking information and probability weighting [R5, R16].

The library scales conditional hazard rather than directly multiplying marginal probability. This keeps the curve in the probability domain and reconstructs scenario marginal PD consistently. LGD is bounded only in the model layer, while raw workout observations remain available elsewhere.

## Validation questions

Check whether scenarios affect the same economic drivers across PD, LGD and EAD. Ensure collateral haircuts do not duplicate a downturn LGD adjustment. Reconcile EAD to contractual schedules or limit histories. Test whether the sum of marginal PD remains at most one and whether account, scenario and detail ECL totals agree.

**Lab.** Compare three engines: independent average parameters, account-level correlated scenarios, and a deliberately incoherent engine that uses cumulative PD in every period. Quantify the overstatement from double counting.

# Chapter 4 — Credit Risk Through Time

## The time axis is part of the target

A default label without a reference date and horizon is incomplete. Application PD may ask whether an accepted applicant defaults within twelve months of origination. Behavioural PD may use monthly snapshots and a twelve-month performance window. IFRS 9 lifetime PD follows the remaining contractual life and must interact with prepayment, cure and maturity. IRB one-year PD has a regulatory definition and calibration objective.

For a cohort originated in month $v$, vintage analysis tracks cumulative default by months on book. It separates maturation from calendar conditions. A 2025 vintage observed for six months cannot be compared directly with a 2021 vintage observed for thirty-six months. Calendar analysis instead aligns exposures by economic time; both views are needed.

Transition matrices describe movements among states such as current, 1–29 DPD, 30–59 DPD, 60–89 DPD, default, cure, prepayment and closure. For state $j$, the one-period estimator is

\[
\widehat P_{jk}=\frac{N_{jk}}{\sum_{\ell}N_{j\ell}},
\]

where $N_{jk}$ counts observations that begin the interval in $j$ and end in $k$. Every row therefore requires the same interval, risk-set rule and state precedence. Treating prepayment as non-default forever biases lifetime interpretation because prepayment is a competing event that removes exposure.

The worked example constructs transition counts and row probabilities directly from an account-month table. The risk set changes whenever an account defaults, prepays, closes or becomes censored. For event times $t_j$, the Kaplan–Meier estimator is $\widehat S(t)=\prod_{t_j\le t}(1-d_j/n_j)$, where $n_j$ is the risk set immediately before $t_j$ and $d_j$ the defaults at that time [R31]. Cause-specific hazards and cumulative incidence are introduced after the reader can reconcile these counts.

Kaplan–Meier handles right censoring when the event process and censoring mechanism are appropriately interpreted. It does not solve selection bias, cure definitions, left truncation or informative closure automatically. Competing-risk methods are preferable when different exit causes have distinct meaning.

## Temporal controls

All features must be available by the decision timestamp. Outcome windows must not overlap training features. Split data by time whenever dates exist, and leave a maturity buffer so test labels are complete. Store observation date, outcome-end date, extraction date and source-system effective timestamps.

**Lab.** Construct monthly vintages from the synthetic retail data. Produce cohort size, default rate and months of available performance. Then create a misleading comparison that ignores maturity and explain why it fails.

# Chapter 5 — Statistical Formulations of Credit Risk

## Choose the estimand before the algorithm

Credit risk is not always a classification problem. Binary classification estimates an event probability over a fixed horizon. Regression estimates severity, utilisation, recovery amount, days past due or profit. Survival models estimate time to default under censoring. Multi-state models estimate movement among delinquency, cure, default and closure states. A model is correct only relative to its estimand and use.

For binary PD, logistic regression models log odds as $\beta_0+x^\top\beta$. A tree ensemble may improve nonlinear prediction but still needs calibration and governance. Workout LGD can require a two-stage model: probability of cure or full recovery followed by loss severity. EAD for revolving facilities may model CCF only where undrawn amount is positive. A lifetime engine may model discrete conditional hazard and derive marginal PD.

The public UCI Credit Approval dataset illustrates a crucial warning. Its outcome is approval, not default. It can teach mixed data types and missingness, but relabelling `approved` as PD would change the meaning of the evidence. Likewise, corporate bankruptcy is related to but not identical with a bank’s regulatory default definition.

The worked example implements the logistic transform with `math.exp` and builds cumulative PD by multiplying survival probabilities inside a loop. It then contrasts a fixed-horizon binary probability, continuous loss severity, ordered delinquency state and time-to-event formulation. Credit-scoring research has long emphasised that assessment depends on the lending population, sample-selection process and operational use, not only on the classifier [R46–R48, R78–R80].

## Model-selection policy

Start with a transparent benchmark. Compare candidates on out-of-time discrimination, probability accuracy, calibration, stability, uncertainty, economics, group outcomes and implementation burden. Complexity must answer a documented need. Do not select by a single cross-validation score if the deployment population, horizon or decision process differs.

**Lab.** For one business question, write four possible estimands: twelve-month default, time to first 90 DPD, loss severity after default and transition to cure. Specify the unit, risk set, censoring, features, label and validation metric for each.

# Chapter 6 — The End-to-End Model Lifecycle

## From model to controlled service

An end-to-end credit model connects source data, data definitions and quality controls, sample and target construction, feature calculation, estimation and calibration, score or parameter output, credit policy, production implementation, and monitoring. A weakness in any one of these elements can dominate algorithmic performance. For example, a temporally leaked target cannot be repaired by better calibration, while an incorrectly implemented score can invalidate an otherwise sound model.

The companion workflow demonstrates the complete sequence on a controlled case. It loads a registered dataset, creates a labelled copy with deterministic defects, assesses quality, separates invalid rows under stated rules, applies an out-of-time split where dates exist, fits a PD benchmark, calculates monitoring measures and produces a simplified ECL illustration for a compatible synthetic case. The run record captures the data, code, configuration and results needed for reproduction.

The worked example writes `reproducible_run_id` from canonical JSON and SHA-256 hashing. Every included input is explicit, and changing one policy field changes the identifier. A hash identifies content; it does not prove correctness, approval or lawful use. The integrated workflow appears only after the reader has constructed and tested the underlying data, model, validation and approval records [R9, R13–R14].

The run manifest should include code version, dataset hash, environment, configuration, timestamps, row counts, exclusions, metrics and approvals. A production registry additionally needs owner, intended use, materiality, validation status, effective dates, dependencies, deployment endpoints and retirement status.

## Segregation of duties

Development, validation, approval, deployment and audit should be distinct responsibilities proportionate to model risk. Automated tests can confirm formulas and data contracts; they cannot approve judgemental policy. A model owner may accept business risk but should not rewrite validation conclusions. An agent may draft an issue but cannot close it without authority.

**Lab.** Draw the lifecycle for an application scorecard and for an IFRS 9 engine. Identify which records are common and which require different owners, horizons, controls and approvals.

> Part I establishes the central idea used throughout the book: every number must be traceable to a defined cash-flow question, time horizon, population, policy and controlled implementation.

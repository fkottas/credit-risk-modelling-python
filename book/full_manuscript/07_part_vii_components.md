# Chapter 37 — Survival Analysis for Default Timing

## Risk over time

Survival analysis models time until an event while recognising incomplete follow-up. If $T$ is default time, the survival function is $S(t)=\Pr(T>t)$ and cumulative PD is $F(t)=1-S(t)$. In continuous time, the hazard is

\[
h(t)=\lim_{\Delta t\downarrow0}
\frac{\Pr(t\le T<t+\Delta t\mid T\ge t)}{\Delta t},
\qquad
S(t)=\exp\left[-\int_0^t h(u)\,du\right].
\]

For discrete periods, $h_t=\Pr(T=t\mid T\ge t)$, survival to the start of period $t$ is $S_{t-1}=\prod_{k<t}(1-h_k)$, and marginal PD is $mPD_t=S_{t-1}h_t$. The conditioning is essential: a borrower who defaulted earlier is no longer in the risk set.

At distinct event time $t_j$, let $n_j$ be the number at risk immediately before the time and $d_j$ the number of defaults. Kaplan–Meier estimates survival non-parametrically as

\[
\widehat S(t)=\prod_{t_j\le t}\left(1-\frac{d_j}{n_j}\right).
\]

The Cox model specifies $h(t\mid x)=h_0(t)\exp(x^\top\beta)$ and estimates relative hazards without specifying $h_0(t)$. Its proportional-hazards assumption means the hazard ratio between two covariate vectors is constant over time. Accelerated failure-time models instead write, for example, $\log T=x^\top\beta+\sigma\varepsilon$ and interpret covariates through time ratios. Discrete-time logistic or complementary-log-log models are convenient for monthly credit panels [R25, R31].

```python
import numpy as np
from creditriskbook.survival import kaplan_meier

duration = np.array([2, 3, 3, 5, 7, 7, 9, 12])
event = np.array([1, 0, 1, 1, 0, 1, 0, 1])
curve = kaplan_meier(duration, event)
print(curve)
```

Censoring must be interpreted. Independent right censoring requires that, conditional on the information used, the censoring process does not selectively remove accounts with unobserved default times. A prepaid account is not simply a non-default observation to infinity. In a competing-risk setting with causes $k$, the cause-specific hazard $h_k(t)$ and cumulative incidence $F_k(t)=\Pr(T\le t,J=k)$ answer different questions; $1-\widehat S_{KM}$ from a default-only analysis can overstate default incidence when prepayment is material. Left truncation occurs when an account enters the observed risk set after origination.

## Validation

Check time origin, intervals, censoring, proportional hazards, baseline calibration and horizon-specific discrimination. Split by origination vintage and calendar period. Ensure monthly rows from one account remain grouped.

**Lab.** Build a person-period table and fit a discrete hazard model. Derive marginal and cumulative PD. Verify that marginal PD sums to cumulative PD.

# Chapter 38 — Lifetime PD and Rating Migration

## Conditional, marginal, and cumulative probabilities

Conditional hazard $h_t$ is default probability in period $t$ given survival to its start. Survival before $t$ is $\prod_{k=1}^{t-1}(1-h_k)$. Marginal PD is that survival multiplied by $h_t$. Cumulative PD through $T$ is the sum of marginal PDs or one minus survival.

Using cumulative PD directly in each ECL period double-counts defaults. Using a twelve-month PD in every year without survival also overstates later marginal risk. A constant-hazard curve is a benchmark, not a forecast of cycle dynamics.

```python
from creditriskbook.ifrs9 import (
    constant_hazard_curve,
    marginal_to_cumulative,
    marginal_to_hazard,
)

marginal = constant_hazard_curve(0.06, periods=36).reshape(-1)
hazard = marginal_to_hazard(marginal)
cumulative = marginal_to_cumulative(marginal)
print(cumulative[11], cumulative[-1], hazard[:3])
```

Rating migration constructs transition probabilities among grades and default. If $P$ is a one-period transition matrix and the process is time-homogeneous and first-order Markov, the $m$-period matrix is $P^m$. The default probability for an account initially in grade $g$ is the $(g,D)$ element of $P^m$ when default is absorbing. This calculation is simple, but its assumptions are strong: migration can depend on time already spent in grade, prior path, policy actions and macroeconomic state. Point-in-time matrices can vary by scenario; through-the-cycle matrices may react too slowly for an accounting estimate.

## Curve governance

Store curve type, conditioning, horizon, frequency, scenario, segment and calibration date. Validate one-year and multi-year cumulative default. Reconcile grade-level and account-level curves. Prevent scenario multipliers from producing invalid probabilities.

**Lab.** Derive a three-year curve from a grade transition matrix and compare with constant hazard. Explain differences and assumptions.

# Chapter 39 — Bayesian Methods for Low-Default Portfolios

## Absence of defaults is not zero risk

When events are rare, maximum-likelihood estimates are unstable and grades may contain zero defaults. Exact confidence intervals, conservative bounds, external evidence and expert judgement become important. Pooling can improve precision while masking risk differences; segmentation can preserve meaning while creating unusably small samples.

A beta-binomial model starts with prior $p\sim Beta(a,b)$ and likelihood $d\mid p\sim Binomial(n,p)$. Conjugacy gives

\[
p\mid d,n\sim Beta(a+d,b+n-d),
\]

with posterior mean $(a+d)/(a+b+n)$ and variance

\[
\frac{(a+d)(b+n-d)}{(a+b+n)^2(a+b+n+1)}.
\]

The prior effective sample size is often summarised as $a+b$, but this interpretation does not establish comparability. Priors must be justified by relevant external or historical evidence, not chosen to reach a capital target. Hierarchical models partially pool grades or countries and quantify uncertainty.

For grades $g=1,\ldots,G$, a hierarchical logit model can write

\[
logit(PD_g)=\mu+u_g,\qquad u_g\sim N(0,\tau^2).
\]

Small grades shrink towards the portfolio distribution through $\tau$, while data-rich grades retain more of their own signal. This is partial pooling, not permission to combine economically incomparable obligors. Posterior predictive checks compare simulated default counts with observed grade and period patterns. Prior predictive checks are performed before seeing outcomes to reveal implausible prior mass.

MCMC estimates $E[g(\theta)\mid D]$ with an average over posterior draws after warm-up. Inspect multiple chains, effective sample size, rank plots, tail behaviour and sensitivity to parameterisation. Variational inference can be faster, but a restricted $q(\theta)$ may understate tail dependence and uncertainty. In a low-default portfolio, understated uncertainty defeats the purpose of using a Bayesian method. Report the likelihood, priors, pooling structure, algorithm, diagnostics, posterior intervals and decision rule; do not report only a posterior mean.

```python
from scipy.stats import beta

defaults, obligors = 0, 120
prior_a, prior_b = 1.0, 99.0
posterior_a = prior_a + defaults
posterior_b = prior_b + obligors - defaults
posterior_mean = posterior_a / (posterior_a + posterior_b)
upper_95 = beta.ppf(0.95, posterior_a, posterior_b)
print(posterior_mean, upper_95)
```

Regulatory PD estimation additionally requires definition, representativeness, long-run average and MoC under applicable rules. A Bayesian model does not remove these obligations.

## Conservatism policy

Separate best estimate, data deficiency, methodological uncertainty, general estimation error and final MoC. Avoid double counting downturn or prudence. Record removal criteria for temporary components.

**Lab.** Compare empirical rate, rule-of-three upper bound and three priors for zero defaults. Present a range and governance recommendation.

# Chapter 40 — Workout LGD Construction

## Cash-flow construction

Workout LGD compares EAD at default with post-default recoveries and direct workout costs discounted to the default date. Let $u_t$ be the year fraction between default and cash flow $t$, and let $CF_t=Recovery_t-Cost_t$. A simplified account estimate is

\[
LGD_{raw}=1-\frac{\sum_{t=1}^{T} CF_t(1+EIR)^{-u_t}}{EAD_0}.
\]

Equivalently, discounted economic loss is $EAD_0-\sum_t CF_t(1+EIR)^{-u_t}$. This reconciliation catches sign errors: recoveries increase discounted net cash flow and reduce LGD, while costs do the opposite. The effective interest rate, day-count convention and eligible cost definition depend on the applicable purpose and policy. Collateral proceeds, guarantees, debt sales and cures require consistent treatment. A cured account can still have economic loss from delayed payments and collection costs [R3, R5].

```python
from creditriskbook.data import load_case_dataset
from creditriskbook.risk_components import calculate_workout_lgd

ledger = load_case_dataset("synthetic_recovery", n_rows=600, seed=401).frame
lgd = calculate_workout_lgd(ledger)
print(lgd[["gross_recovery", "direct_cost", "discounted_net_recovery", "lgd_raw"]].describe())
```

Raw LGD below zero can arise when discounted net recoveries exceed EAD, while LGD above one can arise when costs and shortfalls exceed EAD. Either result can also indicate duplicated cash flows, a sign error or inconsistent exposure. The implementation preserves `lgd_raw`; any bounded modelling value and the resulting adjustment are stored separately.

## Incomplete workouts

Recently defaulted accounts have censored recoveries. Excluding them creates vintage bias; treating current recovery as final overstates LGD. Use resolved cases with representativeness analysis, recovery-curve extrapolation, survival methods or conservative add-ons. Define closure and maximum workout period.

**Lab.** Truncate the synthetic ledger at different dates. Calculate apparent LGD and quantify incomplete-workout bias.

# Chapter 41 — LGD Modelling and Downturn Calibration

## Distribution and model choices

LGD commonly has mass near zero and one, values outside the unit interval before modelling adjustments, right skew and incomplete workouts. Ordinary least squares estimates a conditional mean but can predict values outside the chosen range. A fractional-logit model writes $\mathbb{E}[LGD\mid x]=\sigma(x^\top\beta)$ for observations in $[0,1]$; beta regression models a continuous outcome in $(0,1)$ with a separate precision parameter. Neither handles structural zeros and ones without an explicit extension. Mixture, tree and survival-recovery models address different features of the distribution, so the choice follows the outcome construction and intended estimate.

A two-stage model estimates a structural event and conditional severity. If $C=1$ denotes cure with loss distribution $L_C$ and $C=0$ a non-cure workout with loss $L_N$, then

\[
\mathbb{E}[LGD\mid x]=\Pr(C=1\mid x)\mathbb{E}[L_C\mid C=1,x]
+\Pr(C=0\mid x)\mathbb{E}[L_N\mid C=0,x].
\]

This decomposition is useful only if cure is defined consistently and both conditional models are estimable. Calibration aligns portfolio or segment means while preserving rank where justified. Validation covers monetary error, mean and distributional calibration, tails, segments, vintages and recovery timing—not only $R^2$.

Downturn LGD should reflect adverse economic conditions relevant to default and recovery under the applicable regulatory approach [R3, R10]. The implementation below exposes a simple observed uplift for teaching:

```python
import numpy as np
from creditriskbook.irb import downturn_lgd

observed = np.array([0.20, 0.25, 0.35, 0.55, 0.60, 0.48])
downturn = np.array([False, False, False, True, True, True])
print(downturn_lgd(observed, downturn, minimum_uplift=0.05))
```

This comparison does not identify a regulatory downturn period or satisfy estimation requirements. It demonstrates separation of long-run observation, downturn evidence and minimum policy uplift.

## Governance

Reconcile recovery sources, discount rates and collateral. Document downturn identification, calibration, floors and MoC. Monitor cure, recovery rate, time and cost after deployment.

**Lab.** Fit OLS, fractional and two-part LGD challengers on an account table derived from the ledger. Compare bounds, calibration and segment stability.

# Chapter 42 — EAD and Credit Conversion Factors

## Reference-date construction

For a revolving facility, undrawn amount at reference is $U=L-D$, where $L$ is the valid limit and $D$ is the drawn balance. Additional draw to default is $EAD-D$. When $U>0$, raw CCF is

\[
CCF=\frac{EAD-D}{L-D}.
\]

The denominator requires positive undrawn amount. As $U$ approaches zero, a small monetary difference can create an extreme ratio; CCF error and EAD error must therefore be evaluated together. CCF below zero or above one may arise from repayments, limit changes, interest, fees, excesses, timing mismatch or error. Preserve raw values and explain the mechanism before applying modelling bounds.

```python
from creditriskbook.data import load_case_dataset
from creditriskbook.risk_components import construct_ccf, ead_from_ccf

facilities = load_case_dataset("synthetic_revolving", n_rows=2_000, seed=421).frame
defaults = facilities.loc[facilities["default_12m"].eq(1)]
ccf = construct_ccf(defaults)
reconstructed = ead_from_ccf(
    ccf["drawn_reference"], ccf["undrawn_reference"], ccf["ccf_model"]
)
print(ccf[["ccf_raw", "ccf_model", "boundary_adjustment"]].describe())
```

The three common parameterisations are linked by $\widehat{EAD}=D+\widehat{CCF}\,U$ and $\widehat{EAD}=\widehat u_{default}L$. Model CCF, EAD directly, or utilisation at default according to product mechanics and numerical stability. Non-default reference dates are needed in designs that aim to represent the full performing population rather than only realised defaulters. Cancellation rights, limit management, interest and fee accrual, and conversion assumptions require explicit policy [R3].

## Validation

Backtest EAD and CCF by utilisation, limit, product, time to default and downturn. Reconcile exposure with regulatory or accounting balances. Check that limit changes are captured before default and not leaked.

**Lab.** Compare mean CCF, bounded regression and direct EAD models. Evaluate monetary error as well as CCF error because small denominators can dominate ratios.

> Part VII supplies the term structures and component data needed by accounting and capital calculations. Raw cash-flow and exposure values remain traceable through every modelling adjustment.

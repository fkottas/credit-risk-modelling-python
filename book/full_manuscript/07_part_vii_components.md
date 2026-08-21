# Chapter 37 — Kaplan-Meier, Discrete Hazards, Cox, and AFT Models

## Risk over time

Survival analysis models time until an event while recognising right censoring. If $T$ is default time, survival is $S(t)=P(T>t)$, cumulative PD is $1-S(t)$, and conditional hazard describes event risk among accounts still at risk. For discrete periods with hazard $h_t$, marginal PD is $S(t-1)h_t$.

Kaplan–Meier estimates survival non-parametrically as a product of one minus event share at each time. The Cox model specifies $h(t\mid x)=h_0(t)\exp(x^\top\beta)$, leaving baseline hazard unspecified. Accelerated failure-time models scale survival time under a parametric distribution. Discrete-time logistic or complementary-log-log models are often convenient for monthly credit panels.

```python
import numpy as np
from creditriskbook.survival import kaplan_meier

duration = np.array([2, 3, 3, 5, 7, 7, 9, 12])
event = np.array([1, 0, 1, 1, 0, 1, 0, 1])
curve = kaplan_meier(duration, event)
print(curve)
```

Censoring must be interpreted. A prepaid account is not simply a non-default observation to infinity. Competing-risk methods distinguish prepayment, default and other closure. Left truncation occurs when an account enters the observed risk set after origination.

## Validation

Check time origin, intervals, censoring, proportional hazards, baseline calibration and horizon-specific discrimination. Split by origination vintage and calendar period. Ensure monthly rows from one account remain grouped.

**Lab.** Build a person-period table and fit a discrete hazard model. Derive marginal and cumulative PD. Verify that marginal PD sums to cumulative PD.

# Chapter 38 — Lifetime PD Curves and Rating Migration

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

Rating migration constructs transition probabilities among grades and default. A cohort or Markov approach can derive multi-period default, but stationarity and path independence may fail. Point-in-time matrices change with scenario; through-the-cycle matrices may underreact for ECL.

## Curve governance

Store curve type, conditioning, horizon, frequency, scenario, segment and calibration date. Validate one-year and multi-year cumulative default. Reconcile grade-level and account-level curves. Prevent scenario multipliers from producing invalid probabilities.

**Lab.** Derive a three-year curve from a grade transition matrix and compare with constant hazard. Explain differences and assumptions.

# Chapter 39 — Low-Default Portfolios and Bayesian Conservatism

## Absence of defaults is not zero risk

When events are rare, maximum-likelihood estimates are unstable and grades may contain zero defaults. Exact confidence intervals, conservative bounds, external evidence and expert judgement become important. Pooling can improve precision while masking risk differences; segmentation can preserve meaning while creating unusably small samples.

A beta-binomial model starts with prior $PD\sim Beta(a,b)$. After $d$ defaults in $n$ observations, the posterior is $Beta(a+d,b+n-d)$. Priors must be justified by comparable evidence, not chosen to reach a capital target. Hierarchical models partially pool grades or countries and quantify uncertainty.

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

# Chapter 40 — Workout LGD Data, Discounting, and Cure

## Cash-flow construction

Workout LGD compares EAD at default with discounted post-default recoveries net of direct costs. For cash flow $CF_t=Recovery_t-Cost_t$, a simplified account LGD is

\[
LGD=1-\frac{\sum_{t=1}^{T} CF_t(1+EIR)^{-t}}{EAD_0}.
\]

The effective interest rate, time unit and inclusion of indirect costs depend on applicable purpose and policy. Collateral proceeds, guarantees, sales and cures require consistent treatment. A cured account can still have economic loss from missed interest and costs.

```python
from creditriskbook.data import load_case_dataset
from creditriskbook.risk_components import calculate_workout_lgd

ledger = load_case_dataset("synthetic_recovery", n_rows=600, seed=401).frame
lgd = calculate_workout_lgd(ledger)
print(lgd[["gross_recovery", "direct_cost", "discounted_net_recovery", "lgd_raw"]].describe())
```

Raw LGD below zero or above one may be valid or erroneous. The library preserves it and creates a separate bounded modelling value plus boundary adjustment.

## Incomplete workouts

Recently defaulted accounts have censored recoveries. Excluding them creates vintage bias; treating current recovery as final overstates LGD. Use resolved cases with representativeness analysis, recovery-curve extrapolation, survival methods or conservative add-ons. Define closure and maximum workout period.

**Lab.** Truncate the synthetic ledger at different dates. Calculate apparent LGD and quantify incomplete-workout bias.

# Chapter 41 — LGD Models, Calibration, and Downturn Conditions

## Distribution and model choices

LGD has mass near zero and one, values outside the unit interval before modelling, skewness and censoring. Ordinary least squares can predict impossible values. Fractional logit, beta regression, two-part cure/severity, mixture, tree and survival-recovery models offer alternatives. Choice should reflect raw data and intended estimate.

A two-stage model estimates probability of a structural outcome such as cure or full recovery, then severity conditional on the other state. Calibration aligns portfolio or segment average while preserving rank where justified. Validate mean error, distribution, tail, segment, vintage and recovery timing—not only (R^2).

Downturn LGD should reflect adverse economic conditions relevant to default and recovery. The repository exposes a simple observed uplift for teaching:

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

# Chapter 42 — EAD, Credit Conversion Factors, and Revolving Exposure

## Reference-date construction

For a revolving facility, undrawn amount at reference is $U=L-D$, where $L$ is limit and $D$ is drawn. Additional draw to default is $EAD-D$. Raw CCF is

\[
CCF=\frac{EAD-D}{L-D}.
\]

The denominator requires positive undrawn amount. CCF below zero or above one may arise from repayments, limit changes, interest, fees, excesses or timing. Preserve raw values before modelling boundaries.

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

Model CCF, EAD directly, or utilisation at default depending on data and product. Non-default reference dates are needed to avoid conditioning only on defaults for some development designs. Cancellation rights, limit management and conversion assumptions require policy.

## Validation

Backtest EAD and CCF by utilisation, limit, product, time to default and downturn. Reconcile exposure with regulatory or accounting balances. Check that limit changes are captured before default and not leaked.

**Lab.** Compare mean CCF, bounded regression and direct EAD models. Evaluate monetary error as well as CCF error because small denominators can dominate ratios.

> Part VII supplies the term structures and component data needed by accounting and capital engines. Raw cash-flow and exposure evidence remains visible through every modelling adjustment.

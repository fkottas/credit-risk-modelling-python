# Chapter 9 — Survival, Lifetime PD and Low-Default Portfolios

## Time-to-event data

Binary twelve-month PD discards when default occurs and treats an account observed for one month differently from one observed for the full horizon only through sample rules. Survival analysis uses duration and event indicator. Right-censoring marks accounts whose default time is not observed before data end, prepayment or another event.

The key functions are survival `S(t) = P(T > t)`, cumulative default `F(t) = 1 − S(t)` and hazard, the conditional event probability or intensity at time `t` given survival to that point. Discrete monthly hazard is convenient for credit systems and can be estimated by logistic regression on account-month rows.

## Kaplan–Meier from scratch

At each observed event time, the product-limit estimator multiplies survival by `1 − events/at_risk`. `kaplan_meier` implements this and Greenwood's approximate standard error without a specialist survival library.

```python
from creditriskbook.survival import kaplan_meier

curve = kaplan_meier(durations, events)
```

The basic estimator treats censoring as non-informative conditional on the analysis. Credit prepayment and closure are often informative, so a default-only curve with censoring must be interpreted carefully. Compare cause-specific, competing-risk and sensitivity approaches.

## Hazard to marginal and cumulative PD

For discrete hazard `h_t`, survival to the start of period `t` is the product of `(1 − h_k)` over earlier periods. Marginal PD in period `t` is start survival times `h_t`. Cumulative PD is the sum of marginal PDs.

```python
from creditriskbook.survival import marginal_pd_from_hazard, cumulative_pd_from_hazard

marginal = marginal_pd_from_hazard(monthly_hazard)
cumulative = cumulative_pd_from_hazard(monthly_hazard)
```

Do not sum conditional hazards directly. The identity is tested in the repository.

## Cox, AFT and discrete-time models

The Cox proportional-hazards model leaves baseline hazard unspecified and multiplies it by `exp(xβ)`. Its proportionality assumption should be tested; borrower effects can change with seasoning. Accelerated failure-time models act on survival time and require a distributional form. Discrete-time logistic or complementary-log-log models are often easier to integrate with monthly panels, macro scenarios and changing behavioural features.

Time-varying covariates require strict as-of construction. A monthly utilisation value can predict the next month's hazard, not a prior month. Expanding data to account-month rows creates within-account dependence; use clustered validation and appropriate uncertainty.

## Lifetime PD for IFRS 9

Lifetime PD is a term structure of marginal default probabilities over remaining contractual or behavioural life, consistent with prepayment and scenario assumptions. Stage 1 ECL uses lifetime losses associated with defaults possible in the next twelve months, while Stage 2 uses defaults possible over life. The same marginal curve can feed both when timing and definitions are aligned.

Macroeconomic scenarios can enter monthly hazard through unemployment, rates, house prices or sector variables. Forecasts beyond a reasonable and supportable horizon need a documented reversion. Scenario models should preserve probabilities in `[0,1]`, cumulative monotonicity and coherent paths.

## Competing risks

Default, prepayment, closure and cure compete. Treating prepayment as independent censoring can overstate or understate cumulative default. Cause-specific hazard models each event among those still at risk. Subdistribution methods target cumulative incidence directly. The choice follows the question: risk of default before any competing event, or a hypothetical world without prepayment.

For revolving products, “remaining life” may depend on expected future actions and contractual ability to cancel. Accounting guidance and legal terms must drive scope; a statistical extrapolation alone cannot decide it.

## Low-default portfolios

Corporate, sovereign and specialised portfolios can have few defaults. Point estimates become unstable and absence of default is not zero risk. Approaches include longer representative histories, external data with definition mapping, pooled grades, Bayesian partial pooling, conservative floors and margins of conservatism.

External data require comparability: obligor type, geography, cycle, rating philosophy, default, recovery and observation unit. Pooling more observations can increase bias. Map external grades to the internal master scale and quantify uncertainty.

A beta-binomial or hierarchical model can estimate grade rates while shrinking sparse grades toward a portfolio distribution. Priors should be economically justified and stress-tested. Report posterior or confidence intervals and the effect of floors separately from the central estimate.

## Validation

Validate cumulative and marginal calibration by horizon, cohort and grade. Use survival-aware discrimination such as time-dependent concordance where appropriate. Compare predicted and observed event counts with censoring accounted for. Test proportionality, baseline shape, macro sensitivity and extrapolation. Backtesting a five-year PD on accounts observed for eighteen months is not valid.

## Chapter deliverable

Run the survival section of notebook 05. Build a monthly person-period table from the synthetic portfolio. Fit a discrete hazard model with account age and macro unemployment, convert hazards to marginal and cumulative PD, and reconcile the twelve-month cumulative PD to a direct binary model. Explain any difference.


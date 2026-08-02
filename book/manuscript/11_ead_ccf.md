# Chapter 11 — EAD, CCF and Revolving Exposure

## Drawn plus a conversion of undrawn

For a revolving facility, a common construction is

`EAD = drawn at reference + CCF × undrawn at reference`.

The realised raw CCF is

`(EAD at default − drawn at reference) / undrawn at reference`.

The formula needs a strictly positive undrawn amount. A fully drawn facility has no denominator and requires a different segment. Limit reductions, over-limit balances, interest, fees and exchange movements can produce CCF below zero or above one. Preserve those observations before applying modelling boundaries.

```python
from creditriskbook.risk_components import construct_ccf

ccf = construct_ccf(facility_observations)
```

The code returns undrawn amount, additional draw, raw CCF, bounded modelling CCF and boundary adjustment. `ead_from_ccf` reconstructs predicted exposure for reconciliation.

## Sample construction

Choose a reference date a fixed interval before default, or multiple candidate reference dates. Capture drawn, committed limit, available amount, pending transactions, cancellation status and currency as known then. Define EAD at default consistently with the framework, including accrued interest or fees where required.

Sampling only defaulted facilities estimates CCF conditional on default, which is appropriate for some parameter definitions but creates sparse and selected data. If non-default facilities are used to model draw behaviour, define a comparable horizon and avoid assigning an artificial default date.

Limit changes complicate interpretation. A lender may reduce a limit in response to risk. The observed CCF then reflects both borrower draw and management action. Using future limit reductions as predictors is leakage; using past policy actions can embed treatment effects. Record contractual ability and actual practice for cancellation.

## Behavioural drivers

Useful pre-default information can include utilisation, utilisation trend, payment ratio, delinquency, cash advance, recent line changes, transaction volatility, product age and macro conditions. Features must be lagged to the reference date. High utilisation can leave little undrawn and produce volatile ratios even when additional draw is small; segment or model absolute additional draw as a challenger.

Alternative formulations include:

- regression of CCF with fractional or mixture models;
- regression of additional draw;
- two-stage probability of draw plus amount;
- monthly transition or balance models;
- quantile estimates for conservative EAD;
- joint PD and drawdown models.

Compare error in EAD units, not only CCF. A large CCF error on a tiny line may be immaterial, while a small percentage error on a large commitment matters.

## CCF calibration

Calibrate by product, utilisation band, limit size, time to default and economic period. Weighting by undrawn amount targets portfolio EAD but can let large lines dominate. Report account- and exposure-weighted results. Validate boundary mass and over-limit cases separately.

For IRB, use applicable CCF definitions, floors and downturn or conservatism requirements. For IFRS 9, expected future drawings must be consistent with the exposure period and scenario. Do not reuse an IRB CCF without purpose mapping.

## Dependence with PD and LGD

Utilisation often rises before default. Borrowers can draw liquidity as condition worsens, creating adverse dependence between PD and EAD. The same stress can increase LGD. Independent mean estimates can understate portfolio loss variability.

Analyse joint residuals and outcomes by macro period. A practical scenario model applies coherent unemployment, rate and collateral paths to all components, then aggregates account-level losses. A more advanced simulation introduces shared factors and idiosyncratic residual dependence. Avoid mechanically correlating calibrated probabilities without preserving marginals.

## Dynamic limits

Line management can reduce exposure but can also harm customers or accelerate drawdown. A limit strategy is a treatment policy with delayed outcomes, not just an EAD model. Evaluate profitability, customer impact, fairness, operational constraints and causal selection. Reinforcement learning in Chapter 14 is presented only with offline evaluation and hard safety constraints.

## Chapter deliverable

Generate facilities with drawn amount, limit, reference dates and default exposure. Calculate raw CCF and identify cases outside `[0,1]`. Compare modelling CCF with an additional-draw model using account- and exposure-weighted error. Explain how historic limit reductions bias the result.


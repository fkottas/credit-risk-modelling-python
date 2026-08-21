# Chapter 10 — Workout LGD, Cure and Recovery Modelling

## Loss is a discounted cash-flow outcome

Workout LGD starts at default with EAD and follows recoveries and costs until resolution. For account `i`, a simplified raw workout estimate is

`LGD_i = 1 − present value(net recoveries_i) / EAD_i`.

Net recoveries include cash, collateral proceeds, guarantees and other receipts less direct and appropriately allocated indirect costs under the applicable framework. Timing matters. A recovery received three years after default is worth less than the same amount received immediately. IFRS 9 and IRB can require different discount-rate concepts; keep the rate source in the parameter-purpose matrix.

`calculate_workout_lgd` takes a one-to-many cash-flow ledger, validates that cash flows do not precede default, discounts each net recovery from its date, checks that account-level EAD, effective interest rate and default date are consistent, and aggregates to account level.

```python
from creditriskbook.risk_components import calculate_workout_lgd

account_lgd = calculate_workout_lgd(recovery_ledger)
```

The output preserves `lgd_raw`, creates `lgd_model` bounded to `[0,1]`, and reports the boundary adjustment. Recoveries greater than exposure can produce negative raw LGD; costs or exposure errors can produce LGD above one. Silently clipping at extraction hides data and process issues. Analyse the raw tail, explain adjustments and decide treatment under policy.

## Reference dates and ledgers

Build a default table with account, obligor, facility, default date, default reason, EAD, collateral and resolution status. Join a cash-flow table with amount, type, date, currency, source and cost flag. Preserve reversals and corrections. Convert currency with dated rates and reconcile to finance or collections systems.

An account still in workout has incomplete recoveries. Treating its current LGD as final biases recent defaults upward or downward depending on recovery timing. Options include excluding recent defaults with representativeness analysis, estimating remaining recoveries, survival models for recovery timing, or including resolution indicators in a joint model. Report the workout horizon distribution.

## Cure

A cure is not merely one current payment. Define exit from default, minimum probation, redefault rule and treatment of restructuring. Cure rate can be account-, exposure- or default-event-weighted. If cured accounts resume contractual payments, their loss process differs from liquidations.

A common two-stage architecture first models cure probability, then severity conditional on cure/non-cure. Another models probability of zero or near-zero loss and positive severity separately. The total expected LGD is the probability-weighted combination. Keep the components visible for validation.

## Model forms

Ordinary least squares can predict outside `[0,1]` and assumes constant variance. Fractional response models use a logistic mean. Beta regression handles continuous outcomes strictly inside `(0,1)` but needs treatment of exact zeros and ones. Mixture models represent boundary masses. Trees and boosting capture interactions but need calibration and stable tail treatment. Quantile models can support conservative estimates.

Features should be knowable at the chosen reference date. Origination LGD can use collateral and facility attributes available at origination. Defaulted-asset LGD can use information at default. Post-default collections actions are outcomes or treatments and can create leakage if used to predict earlier LGD.

## Collateral and guarantees

Collateral value is not recovery. Apply enforceability, seniority, haircuts, sale costs, time to sale, market conditions and prior liens. Avoid double-counting guarantee and collateral proceeds. Property indices can support scenario adjustments but do not replace asset-level valuation governance.

Downturn LGD reflects adverse conditions associated with higher losses, not an arbitrary multiplier. Identify downturn periods and drivers, assess data scarcity, quantify effects and apply applicable regulatory methods and margins. IFRS 9 scenario LGD is a probability-weighted accounting estimate, not automatically downturn LGD.

## Calibration and validation

Compare predicted and realised discounted loss by score band, product, collateral, default vintage, resolution status and time. Validate cure, recovery amount, timing and costs separately. Backtesting must account for incomplete cases. Stress collateral value, recovery lag and costs. Benchmark against simpler long-run averages and segment tables.

LGD is often correlated with PD and EAD. During downturns, more borrowers default, collateral falls, collections lengthens and lines are drawn. Portfolio simulation in Chapter 13 should not assume independence without analysis.

## Chapter deliverable

Extend notebook 05 with at least 1,000 synthetic defaults and multiple recovery cash flows. Inject duplicate cash flows, negative dates, inconsistent EAD and unresolved cases. Build a reconciliation from gross recovery to discounted net recovery, raw LGD and model LGD. Fit and validate a cure-plus-severity model.


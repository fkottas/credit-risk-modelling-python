# Chapter 12 — IFRS 9 and CECL Engines

## Build a cash-flow engine, not a multiplier spreadsheet

An ECL engine connects exposure, default timing, cash shortfalls, discounting, scenarios, staging and reporting. The compact identity `PD × LGD × EAD` is useful for component reconciliation, but a robust implementation uses marginal losses over time:

`ECL = Σ_t marginal_PD_t × LGD_t × EAD_t × discount_t`,

calculated under each scenario and then probability-weighted. Timing conventions must be consistent. If LGD already includes discounted recoveries, avoid discounting the same cash flow twice.

## Staging and SICR

Stage 1 generally carries 12-month ECL. Stage 2 carries lifetime ECL after SICR. Stage 3 carries lifetime ECL for credit-impaired assets. Staging is an account-level decision with quantitative and qualitative evidence. Record current stage, prior stage, trigger, trigger date, cure or probation and override.

Quantitative SICR can compare origination and current lifetime PD over the same remaining horizon. Absolute and relative changes behave differently at low origination PD. Delinquency backstops, watchlists, forbearance and sector information require separate data and controls. Validate transfers, not only total ECL.

## Scenario implementation

A scenario contains macro paths, probability, narrative, horizon and approval. Satellite models translate macro variables into monthly PD, LGD, EAD, prepayment or recovery. Calculate nonlinear losses separately under upside, base and downside. Scenario probabilities sum to one and are versioned.

The repository's `educational_ecl` accepts scenario weights and PD/LGD multipliers and distinguishes stages. It is deliberately simplified:

```python
from creditriskbook.ecl import educational_ecl

result = educational_ecl(portfolio)
assert (result["ecl_downside"] >= result["ecl_base"]).all()
```

It uses constant hazard and an average timing point. A production design should use contractual or behavioural schedules, marginal PD and scenario-specific exposure and recovery timing.

## Effective-interest discounting

Expected cash shortfalls are discounted to the reporting date using the applicable effective interest rate or permitted approximation [R5]. Store rate source and adjustments. Floating-rate instruments, modifications and purchased or originated credit-impaired assets require specific accounting treatment. This book provides implementation architecture, not accounting conclusions.

## Provision matrix

The IFRS 9 simplified approach can use a provision matrix for eligible trade receivables. Segment receivables by shared credit-risk characteristics, build historical loss experience, adjust for current and forward-looking information, and apply lifetime loss rates. The attached PwC guide is used as secondary professional context, not authority, and none of its tables or worked examples is reproduced [R18].

A robust matrix reconciles opening balance, new receivables, collections, write-offs, bucket migrations and closing balance. Simple current-versus-overdue percentages can be biased by growth and recoveries. Cohort methods trace invoices to resolution.

## CECL methods

CECL estimates expected loss over contractual term for assets in scope, adjusted for expected prepayment where applicable. Methods include:

- historical loss rates with qualitative adjustments;
- vintage analysis;
- roll-rate or migration analysis;
- PD/LGD and discounted cash flow;
- remaining life or WARM-type approaches;
- econometric forecasts with reversion.

The method should fit data, portfolio and materiality. Complex does not mean compliant. Document the reasonable-and-supportable forecast period, reversion method and qualitative factors. Avoid double-counting forecast effects in both model and overlay.

## Overlays and post-model adjustments

An overlay addresses identified limitations or emerging risks not adequately captured. It needs a statement of risk, evidence, methodology, amount, uncertainty, owner, approval, monitoring and removal criteria. A permanent unexplained overlay is evidence that the model or process needs redevelopment.

Track gross model ECL, individual adjustments, final ECL and period movement. Backtest overlay direction and magnitude after outcomes mature.

## Reconciliation and controls

At each run, reconcile source-system balances to finance totals, population counts through staging, scenario ECL to weighted ECL, discounted components to account totals, account totals to segment and ledger, and current to prior period movement. Differences have defined tolerances and owners.

UAT includes stage boundary, maturity under twelve months, zero exposure, defaulted account, cured account, floating rate, scenario-weight error, negative recovery, prepayment, missing schedule, currency and rounding. Parallel run old and new engines with reason-coded differences.

## Chapter deliverable

Replace notebook 06's constant-hazard approximation with a monthly schedule for twenty synthetic loans. Generate marginal PD, scheduled EAD, scenario LGD and discount factors. Reconcile account ECL to monthly components and explain every difference from the simplified engine.


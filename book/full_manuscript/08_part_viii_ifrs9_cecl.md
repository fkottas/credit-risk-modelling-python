# Chapter 43 — ECL Engine Architecture and Data Contracts

## Separate policy, model, and calculation

An ECL engine consumes balances, stages, marginal PD, LGD, EAD, effective interest rates, contractual periods, scenarios and weights. It should not hide staging thresholds, macro models and overlays inside one opaque function. Separate modules allow accounting policy, model validation and implementation testing to identify responsibility.

The project contract uses one row per account and projection period with `marginal_pd`, `lgd`, `ead` and `effective_interest_rate`. Scenario objects carry weight and PD/LGD/EAD multipliers. Stage 1 limits default events to the next twelve periods in a monthly configuration; Stage 2 uses the full schedule; Stage 3 places default probability at the first period for the simplified defaulted-asset illustration.

```python
from creditriskbook.data import load_case_dataset
from creditriskbook.ifrs9 import Scenario, calculate_ecl

schedule = load_case_dataset(
    "synthetic_ifrs9_schedule", n_rows=500, seed=431
).frame
scenarios = (
    Scenario("upside", 0.20, 0.80, 0.90, 0.98),
    Scenario("base", 0.55),
    Scenario("downside", 0.25, 1.50, 1.20, 1.05),
)
result = calculate_ecl(schedule, scenarios)
print(result.account.head())
print(result.reconciliation)
```

The detail, scenario and account totals reconcile exactly. Production also needs accounting scope, currency, accrued interest, off-balance-sheet exposure, collateral, guarantee, modification, POCI, write-off and disclosure logic.

## Engine controls

Validate uniqueness, stage, probabilities, EIR and non-negative EAD. Version scenario and model inputs. Reconcile opening balance, movement and closing allowance to the ledger. Store calculation date and processing timestamp.

**Lab.** Build a data-contract test suite that deliberately creates duplicate periods, marginal PD over one, invalid stage and inconsistent EIR. Confirm the engine rejects each.

# Chapter 44 — Staging, SICR, Watchlists, Cures, and Backstops

## Multiple indicators, one governed result

SICR compares credit risk at reporting with initial recognition. Quantitative relative and absolute PD changes, delinquency, watchlist, forbearance, rating deterioration, sector information and other qualitative factors may contribute. Defaults and credit impairment move exposures to Stage 3. DPD thresholds are backstops subject to applicable policy, not substitutes for forward-looking assessment.

The `StagingPolicy` exposes thresholds and the assignment returns every flag, PD ratio, absolute change, stage and primary reason. This supports audit and sensitivity.

```python
from creditriskbook.ifrs9 import StagingPolicy, assign_stages

policy = StagingPolicy(
    stage2_dpd_backstop=30,
    stage3_dpd_backstop=90,
    relative_pd_threshold=2.0,
    absolute_pd_increase=0.02,
    low_credit_risk_exemption=False,
)
staged = assign_stages(accounts, policy)
print(staged.groupby(["stage", "stage_reason"]).size())
```

Cure policy prevents immediate return to Stage 1 after a payment. Define probation, evidence of sustained improvement, treatment of forbearance and interaction with default cure. A stage decrease should be traceable to approved criteria.

## Staging validation

Analyse Stage 1 to default capture, Stage 2 lead time, false positives, cure and override. Compare thresholds across vintages and scenarios. High Stage 2 volume is not automatically conservative if the wrong accounts are transferred.

**Lab.** Backtest whether Stage 2 captures defaults six and twelve months early. Compare quantitative-only and combined watchlist rules.

# Chapter 45 — Macroeconomic Scenarios, Satellite Models, and Weights

## Forward-looking information

ECL should reflect reasonable and supportable forward-looking information available without undue cost or effort under applicable policy. Scenarios may include base, upside and downside paths for unemployment, GDP, rates, house prices or sector variables. A satellite model maps macro conditions to PD, LGD, prepayment or exposure.

Scenario construction has four layers: narrative and internal consistency; numerical paths; parameter translation; and probability weights. Do not choose weights merely to hit a target provision. Consider nonlinearity: ECL at average macro values can differ from probability-weighted ECL across scenarios.

```python
from creditriskbook.ifrs9 import Scenario

scenarios = (
    Scenario("upside", weight=0.20, pd_multiplier=0.80, lgd_multiplier=0.90),
    Scenario("base", weight=0.55),
    Scenario("downside", weight=0.25, pd_multiplier=1.50, lgd_multiplier=1.20),
)
assert abs(sum(item.weight for item in scenarios) - 1.0) < 1e-12
```

Multipliers are a transparent teaching interface, not a substitute for an estimated macro model. Real models require lag selection, stationarity, structural breaks, scenario range and forecast/reversion governance. World Bank and FRED series require indicator-specific licence, vintage and revision controls.

## Scenario governance

An approved committee should record source forecasts, narrative, range, weights, overlays and uncertainty. Independent validation should challenge sensitivity and double counting. Archive the information set available on the reporting date.

**Lab.** Build unemployment and GDP scenarios, estimate a simple logit satellite model, and convert conditional hazards to scenario marginal PD. Compare weighted ECL with ECL under average macro inputs.

# Chapter 46 — Contractual Cash Flows, EIR Discounting, and Prepayment

## Timing matters

ECL is a present value of cash shortfalls. The effective interest rate established under applicable accounting rules determines discounting. With monthly period $t$ and annual EIR $r$, the teaching engine uses $DF_t=(1+r/12)^{-t}$. Product conventions may require more precise day count and modified-asset treatment.

EAD paths should reflect scheduled amortisation, revolving drawdown and contractual features. Prepayment shortens exposure life and affects interest cash flows. It is not default and must not be double-counted as zero loss after a default curve already conditions on survival and exposure.

```python
from creditriskbook.ifrs9 import calculate_ecl

result = calculate_ecl(schedule, scenarios)
detail = result.detail
check = detail[[
    "account_id", "period", "scenario_marginal_pd",
    "scenario_lgd", "scenario_ead", "discount_factor", "ecl"
]].head(12)
print(check)
```

For Stage 1, twelve-month ECL can contain cash shortfalls occurring after twelve months when they arise from a default possible within the next twelve months. A simplified period engine must be interpreted accordingly.

## Cash-flow reconciliation

Reconcile principal schedules, interest, fees, limits and maturity to source systems. Test zero rates, high rates, short maturity, balloon, grace, revolving and prepayment cases. Use approved conventions for off-balance-sheet commitments.

**Lab.** Compare ECL for bullet and amortising loans with identical opening EAD, PD and LGD. Explain the timing and discount differences.

# Chapter 47 — Provision Matrices, CECL Methods, and Management Overlays

## Method choice follows portfolio behaviour

A provision matrix groups receivables by aging and other relevant risk characteristics, estimates historical lifetime loss rates and adjusts them for current and forward conditions. Buckets need sufficient homogeneity. Changing collection or invoice policy can invalidate historical rates.

CECL method choice may include vintage, roll-rate, loss-rate, PD×LGD, discounted cash flow and WARM-style adjustments where appropriate. The chosen method must cover contractual term and reasonable forecasts under applicable guidance. Multiple methods should reconcile at concept and portfolio level.

Management overlays address risks not adequately captured in models or data. An overlay should have an identified gap, owner, methodology, evidence, amount, validation, approval, monitoring and exit criterion. Permanent overlays can signal model deficiency.

```python
import pandas as pd
from creditriskbook.ifrs9 import apply_overlay

overlays = pd.DataFrame({
    "account_id": result.account["account_id"].head(2),
    "overlay_type": ["multiplicative", "additive"],
    "overlay_value": [1.10, 250.0],
    "overlay_reason": ["emerging sector risk", "known data gap"],
})
post = apply_overlay(result.account, overlays)
print(post[["pre_overlay_ecl", "overlay_amount", "post_overlay_ecl"]].head())
```

The additive and multiplicative types are explicit. Account overlays are illustrative; real overlays may be portfolio-level and require allocation rules.

**Lab.** Create an overlay register and sensitivity. Define evidence and expiry. Show opening, model, scenario, overlay, write-off and closing allowance movements.

# Chapter 48 — Stress Testing, Reconciliation, Controls, and Disclosure

## Stress is not only a downside scenario

IFRS 9 scenario weighting estimates expected loss, while stress testing asks resilience under adverse but plausible conditions and reverse stress asks what conditions breach a threshold. Objectives, severity and governance differ. A stress may affect originations, migration, PD, LGD, EAD, prepayment, revenue, capital and liquidity.

Reconciliation connects account calculations to finance. At minimum compare detail, scenario, account, portfolio, subledger and general ledger. Differences may come from scope, currency, rounding, overlays, write-offs, sales and processing cutoffs.

```python
from creditriskbook.ifrs9 import reconcile_ecl

ledger_total = float(result.account["ecl"].sum())
control = reconcile_ecl(result.account, ledger_total=ledger_total, tolerance=0.01)
print(control)
assert control["within_tolerance"]
```

A successful arithmetic reconciliation does not validate PD, LGD or staging. Separate controls address completeness, model implementation, parameter approval and disclosure.

## Disclosure and change analysis

Explain movements by new business, repayments, stage transfers, model changes, forecast, overlays, write-offs and foreign exchange. Store both amount and narrative. Avoid attributing all change to “macro” when portfolio mix changed.

**Lab.** Run base and severe scenarios, produce stage and segment waterfalls, and identify a reverse-stress PD/LGD combination that breaches a provision or capital threshold.

> Part VIII turns component models into a controlled accounting engine. Scenario judgement and overlays remain visible and separately governed rather than embedded in model coefficients.

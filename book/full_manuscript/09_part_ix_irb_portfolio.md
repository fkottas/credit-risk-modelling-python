# Chapter 49 — Corporate and SME IRB Risk-Weight Functions

## One-factor structure

For corporate exposures, the Basel function transforms PD through a systematic asset-correlation model at high confidence. In simplified notation,

\[
K=\left[LGD\,N\left(\frac{G(PD)+\sqrt{R}G(0.999)}{\sqrt{1-R}}\right)-PD\,LGD\right]MA,
\]

where (N) is the normal CDF, (G) its inverse, (R) asset correlation and (MA) maturity adjustment. RWA is (12.5\times K\times EAD). Expected loss is separate.

Corporate correlation decreases between prescribed bounds as PD increases. Eligible SME corporate treatment includes a firm-size adjustment based on annual sales within defined bounds. The project formula accepts sales as an explicit input; it does not infer eligibility.

```python
import numpy as np
from creditriskbook.irb import irb_capital

result = irb_capital(
    pd_values=np.array([0.002, 0.01, 0.05]),
    lgd_values=0.45,
    ead_values=1_000_000,
    asset_class="sme_corporate",
    maturity_years=np.array([1.0, 2.5, 5.0]),
    annual_sales_eur_millions=np.array([8.0, 20.0, 45.0]),
)
print(result.rows)
```

The function exposes raw PD, floored PD, adjustment, correlation, conditional PD, maturity adjustment, capital, RWA and EL. This audit table is preferable to a single capital number.

## Regulatory implementation

Apply the exact in-force jurisdictional text. Validate PD/LGD/EAD and maturity separately. Handle guarantees, credit risk mitigation, specialised lending, purchased receivables, provisions and output floors in dedicated modules.

**Lab.** Create a grid of PD, LGD, maturity and sales. Plot risk weight and explain nonlinearities. Reconcile one row manually.

# Chapter 50 — Residential Mortgage, QRRE, and Other Retail IRB

## Retail functions differ by asset class

Retail IRB uses prescribed correlations for residential mortgage, qualifying revolving retail exposure and other retail. The base functions do not apply the corporate maturity adjustment. In the project implementation, mortgage correlation is 0.15, QRRE is 0.04, and other-retail correlation declines from approximately 0.16 at very low PD toward 0.03 at high PD, following the prescribed functional form [R2].

These differences have substantial capital effects. They are not a menu. QRRE qualification requires regulatory criteria; a revolving product name is insufficient. Residential-mortgage treatment requires applicable exposure and collateral conditions.

```python
import numpy as np
from creditriskbook.irb import irb_capital

pd_values = np.array([0.003, 0.01, 0.05])
for asset_class in (
    "residential_mortgage",
    "qualifying_revolving_retail",
    "other_retail",
):
    result = irb_capital(pd_values, 0.35, 100_000, asset_class=asset_class)
    print(asset_class, result.rows["capital_rate"].round(5).tolist())
```

Retail pools need homogeneous risk characteristics, consistent assignment and sufficient differentiation. Model performance should be examined by pool, product, vintage, channel and score.

## Floors and policy

Parameter floors vary by framework and collateral condition. This book requires the caller to supply the applicable PD floor and leaves other floors to a controlled regulatory layer rather than embedding possibly outdated assumptions.

**Lab.** Compare mortgage, QRRE and other-retail outputs for identical numerical parameters. Write why the comparison is mathematical only and cannot justify reclassification.

# Chapter 51 — IRB PD Estimation, Long-Run Average, Calibration, and MoC

## Estimation target

IRB PD is a one-year probability of regulatory default for an obligor grade or pool. Development may rank risk with point-in-time information, while calibration targets a long-run average appropriate to the framework and rating philosophy. The estimation sample, historical observation period, default definition and representativeness require evidence.

The long-run average can weight annual rates equally or weight obligor observations. The choice matters when portfolio size changes. Economic-cycle coverage and structural breaks must be assessed. A simple total-defaults divided by total-obligors calculation is transparent but not automatically sufficient.

```python
import pandas as pd
from creditriskbook.irb import (
    add_margin_of_conservatism,
    calibrate_pd_to_long_run_average,
    weighted_long_run_default_rate,
)

history = pd.DataFrame({"year": [2021, 2022, 2023, 2024],
                        "defaults": [5, 9, 18, 10],
                        "obligors": [500, 650, 700, 800]})
lra = weighted_long_run_default_rate(history, weighting="obligor")
calibrated = calibrate_pd_to_long_run_average(raw_pd, lra)
final_pd, audit = add_margin_of_conservatism(
    calibrated.calibrated_pd,
    {"data": 0.001, "method": 0.0005},
)
```

MoC addresses identified deficiencies and estimation uncertainty. Separate categories, prevent double counting, and define review/removal criteria. The final estimate must respect applicable floors.

## Validation

Backtest central tendency and grades with confidence intervals, migration and cycle analysis. Benchmark against alternative methods and external evidence. Review overrides and use.

**Lab.** Calculate LRA under year and obligor weighting, calibrate a score, add named MoC and show every movement from raw to final PD.

# Chapter 52 — IRB LGD, EAD, Downturn, Floors, and Defaulted Assets

## Purpose-specific parameters

IRB LGD estimates economic loss conditional on default under required conditions, including downturn considerations where applicable. EAD estimates exposure at default, including conversion of off-balance-sheet amounts. Best estimate of expected loss and LGD in default address defaulted exposures under applicable rules. These parameters are not interchangeable with IFRS 9 scenario LGD or accounting cash shortfall.

Workout data require recovery cash flows, costs, EAD, discounting, cure and closure. EAD needs reference dates, limits, drawn balances, cancellations and default exposure. Floors and conservatism belong after a traceable raw estimate.

```python
from creditriskbook.data import load_case_dataset
from creditriskbook.risk_components import calculate_workout_lgd, construct_ccf

recovery = load_case_dataset("synthetic_recovery", n_rows=400, seed=521).frame
lgd_accounts = calculate_workout_lgd(recovery)

revolving = load_case_dataset("synthetic_revolving", n_rows=2_000, seed=522).frame
defaulted = revolving.loc[revolving["default_12m"].eq(1)]
ccf = construct_ccf(defaulted)
print(lgd_accounts["lgd_raw"].mean(), ccf["ccf_raw"].mean())
```

## Downturn and defaulted assets

Identify adverse periods through relevant economic and portfolio evidence. Apply adjustments coherently across recovery value, time and cost. For defaulted assets, distinguish ELBE, unexpected loss, provisioning and capital treatment. Record collateral and guarantee effects without double counting.

**Lab.** Produce parameter waterfalls for long-run LGD, downturn adjustment, MoC and floor; and for raw CCF, model calibration, MoC and floor.

# Chapter 53 — Portfolio Concentration, Vasicek, Credit VaR, and Monte Carlo

## Granularity and dependence

IRB capital functions assume a highly granular portfolio where idiosyncratic risk diversifies. Real portfolios contain name, sector, geography and collateral concentration. Herfindahl index (HHI=\sum_iw_i^2) summarises exposure concentration but not default correlation or tail severity.

The Vasicek conditional default probability at confidence (q) is

\[
PD_q=N\left(\frac{G(PD)+\sqrt{R}G(q)}{\sqrt{1-R}}\right).
\]

Multiplying by LGD gives a limiting portfolio-loss quantile under strong assumptions. Monte Carlo can add heterogeneous exposures, correlated factors, stochastic LGD and EAD, but results depend on calibration and simulation design.

```python
import numpy as np
from creditriskbook.capital import vasicek_portfolio_loss_quantile
from creditriskbook.irb import herfindahl_concentration

loss_q = vasicek_portfolio_loss_quantile(
    0.02, 0.45, asset_correlation=0.15, confidence=0.999
)
hhi = herfindahl_concentration(np.array([50, 30, 20]))
print(loss_q, hhi)
```

Credit VaR terminology should state whether expected loss is subtracted, which confidence and horizon apply, and whether loss includes migration or default only.

## Model risk

Validate factor correlations, tail dependence, recovery dependence, concentration and random-number convergence. Stress dominant obligors separately. Avoid false precision from millions of simulations with uncertain inputs.

**Lab.** Simulate independent and one-factor correlated defaults for equal exposures. Compare mean and 99.9% loss. Then introduce one large name.

# Chapter 54 — Counterparty Exposure, Netting, Collateral, CVA, and SA-CCR

## Exposure is future and market-dependent

Counterparty credit risk arises when replacement value depends on market movements and the counterparty may default before settlement. Current exposure, expected exposure, expected positive exposure and potential future exposure describe different aspects. Netting reduces exposure only under enforceable agreements. Collateral reduces it subject to timing, disputes, thresholds, haircuts and wrong-way risk.

CVA is the market value of expected loss from counterparty default, often conceptualised as discounted marginal default probability times LGD and expected exposure under relevant valuation measures. DVA reflects the entity’s own credit in valuation and has distinct interpretation. SA-CCR is a prescribed exposure method with replacement cost, potential future exposure and multipliers; this chapter does not implement the full standard.

```python
from creditriskbook.data import load_case_dataset

profiles = load_case_dataset(
    "synthetic_counterparty_profiles", n_rows=120, seed=541
).frame
portfolio_profile = profiles.groupby("horizon_years", as_index=False).agg(
    expected_exposure=("expected_exposure", "sum"),
    pfe_975=("pfe_975", "sum"),
)
print(portfolio_profile)
```

The synthetic profiles are not market-calibrated. They support data-shape, aggregation and control exercises.

## Counterparty policy

Store legal entity, netting set, agreement, collateral, trade and market scenario. Validate legal enforceability and reconcile trades. Monitor wrong-way risk when exposure rises as counterparty quality falls.

**Lab.** Compute a stylised unilateral CVA from marginal PD, LGD, expected exposure and discount factors. Compare with and without collateral, then discuss why enforceability matters.

> Part IX makes regulatory functions inspectable while keeping classification, eligibility, floors and national implementation outside the mathematical helper where they can be governed explicitly.

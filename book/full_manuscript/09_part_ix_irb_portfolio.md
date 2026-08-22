# Chapter 49 — Corporate and SME IRB Capital

## One-factor structure

For corporate exposures, the Basel asymptotic single-risk-factor function maps a one-year PD, downturn LGD, asset correlation and effective maturity to a capital requirement [R2]. The compact formula is easier to understand after its components are separated. For a non-SME corporate exposure, the prescribed correlation function is

\[
R(PD)=0.12\frac{1-e^{-50PD}}{1-e^{-50}}
+0.24\left(1-\frac{1-e^{-50PD}}{1-e^{-50}}\right).
\]

The maturity parameter is

\[
b(PD)=\left[0.11852-0.05478\ln(PD)\right]^2,
\]

and the maturity adjustment for effective maturity $M$ is

\[
MA(PD,M)=\frac{1+(M-2.5)b(PD)}{1-1.5b(PD)}.
\]

Let $N$ denote the standard-normal distribution function and $G=N^{-1}$. The capital rate before any applicable scaling or output-floor treatment is

\[
K=\left[
LGD\,N\!\left(
\frac{G(PD)}{\sqrt{1-R}}+
\sqrt{\frac{R}{1-R}}G(0.999)
\right)-PD\times LGD
\right]MA(PD,M).
\]

Risk-weighted assets are $RWA=12.5\times K\times EAD$. The subtraction of $PD\times LGD$ removes expected loss from the stressed conditional loss rate; the capital term therefore addresses unexpected loss under the regulatory construction. EAD converts the rate to currency and 12.5 is the reciprocal of the 8% minimum capital ratio. These interpretations do not replace the detailed eligibility, parameter and implementation requirements in the applicable Basel and national texts [R2, R4].

Corporate correlation decreases between prescribed bounds as PD increases. This is a regulatory specification, not an empirical estimate from the teaching data. For an eligible SME corporate exposure with annual sales $S$ in EUR millions, the prescribed size adjustment is commonly written

\[
R_{SME}=R(PD)-0.04\left(1-\frac{\min(50,\max(5,S))-5}{45}\right).
\]

The clamping states the EUR 5–50 million range used by the formula; it does not make an obligor outside the applicable eligibility rules an SME. The implementation accepts sales as an explicit input and never infers legal eligibility from a product label [R2, R4].

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

The function exposes raw PD, floored PD, adjustment, correlation, conditional PD, maturity adjustment, capital, RWA and expected loss. Keeping these intermediate values allows a student to reproduce one row with a calculator and allows an implementation reviewer to locate a discrepancy.

## Regulatory implementation

Apply the exact in-force jurisdictional text. Validate PD/LGD/EAD and maturity separately. Handle guarantees, credit risk mitigation, specialised lending, purchased receivables, provisions and output floors in dedicated modules.

**Lab.** Create a grid of PD, LGD, maturity and sales. Plot risk weight and explain nonlinearities. Reconcile one row manually.

# Chapter 50 — Retail IRB Capital

## Retail functions differ by asset class

Retail IRB uses prescribed correlations for residential mortgage, qualifying revolving retail exposure and other retail. The base functions do not apply the corporate maturity adjustment. In the project implementation, mortgage correlation is 0.15, QRRE is 0.04, and other-retail correlation declines from approximately 0.16 at very low PD toward 0.03 at high PD, following the prescribed functional form [R2].

For other retail exposures, that function is

\[
R(PD)=0.03\frac{1-e^{-35PD}}{1-e^{-35}}
+0.16\left(1-\frac{1-e^{-35PD}}{1-e^{-35}}\right).
\]

The retail capital rate uses the same conditional-loss transformation as the corporate formula but omits the corporate maturity adjustment:

\[
K=LGD\,N\!\left(
\frac{G(PD)}{\sqrt{1-R}}+
\sqrt{\frac{R}{1-R}}G(0.999)
\right)-PD\times LGD.
\]

Holding PD and LGD constant while changing asset class therefore isolates the effect of the prescribed correlation function. It does not show that one legal classification is preferable or available.

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

# Chapter 51 — IRB PD Calibration and Margin of Conservatism

## Estimation target

IRB PD is a one-year probability of regulatory default for an obligor grade or pool. Development may rank risk with point-in-time information, while calibration targets a long-run average appropriate to the framework and rating philosophy. The estimation sample, historical observation period, default definition and representativeness require evidence.

For year $y$, let $D_y$ be the number of defaults and $N_y$ the number of non-defaulted obligors at the relevant counting date. Two transparent summaries are

\[
\widehat{PD}_{year}=\frac{1}{Y}\sum_{y=1}^{Y}\frac{D_y}{N_y},
\qquad
\widehat{PD}_{obligor}=\frac{\sum_yD_y}{\sum_yN_y}.
\]

The first gives every year equal influence; the second gives greater influence to years with larger observed populations. If portfolio size changed sharply across the cycle, the estimates answer different questions. The selected estimator therefore requires a stated weighting rationale, assessment of economic-cycle coverage, consistent counting rules and treatment of structural breaks.

A ranking model can be calibrated to a target central tendency by adding an intercept shift $c$ to the raw log-odds:

\[
p_i(c)=\operatorname{logit}^{-1}\!\left[\operatorname{logit}(p_i^{raw})+c\right],
\qquad
\frac{1}{n}\sum_{i=1}^{n}p_i(c)=\widehat{PD}_{target}.
\]

The scalar $c$ is solved numerically. This preserves rank but changes the probability level; it cannot correct missing risk differentiation within a grade.

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

Margin of conservatism (MoC) addresses identified data or methodological deficiencies and relevant estimation uncertainty. Its form must match the parameter scale. For an additive PD approach,

\[
PD_i^{final}=\max\left(PD_{floor},\ PD_i^{cal}+MoC_{data}+MoC_{method}+MoC_{other}\right).
\]

An odds multiplier or grade-level adjustment would produce a different result and must not be mixed silently with this formula. Separate categories, quantify overlap, and define review and removal criteria; conservatism is not a substitute for correcting a remediable error.

## Validation

Backtest central tendency and grades with confidence intervals, migration and cycle analysis. Benchmark against alternative methods and external evidence. Review overrides and use.

**Lab.** Calculate LRA under year and obligor weighting, calibrate a score, add named MoC and show every movement from raw to final PD.

# Chapter 52 — IRB LGD and EAD Calibration

## Purpose-specific parameters

IRB LGD estimates economic loss conditional on default under required conditions, including downturn considerations where applicable. EAD estimates exposure at default, including conversion of off-balance-sheet amounts. Best estimate of expected loss and LGD in default address defaulted exposures under applicable rules. These parameters are not interchangeable with IFRS 9 scenario LGD or accounting cash shortfall.

For a defaulted facility with exposure $EAD_i$ at default, recoveries $Rec_{i,t}$, direct workout costs $Cost_{i,t}$ and annual discount rate $r_i$, a transparent workout estimate is

\[
LGD_i^{raw}=1-
\frac{\sum_t(Rec_{i,t}-Cost_{i,t})(1+r_i)^{-u_{i,t}}}{EAD_i},
\]

where $u_{i,t}$ is the year fraction from default to cash flow. The definition must state whether cures, collateral proceeds, post-default interest and indirect costs are included. Open workouts are censored; treating their observed-to-date recoveries as final systematically overstates loss when later recoveries remain possible.

For a revolving facility with balance $B_0$, limit $L_0$ and balance at default $B_D$, a realised conversion factor is

\[
CCF_i=\frac{B_D-B_0}{L_0-B_0},\qquad L_0>B_0,
\]

and $EAD_i=B_0+CCF_i(L_0-B_0)$. Small undrawn amounts make the ratio unstable, so validation must also report monetary drawdown error. Floors and conservatism belong after a traceable raw estimate, not inside undocumented data preparation.

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

# Chapter 53 — Portfolio Credit Risk and Concentration

## Granularity and dependence

IRB capital functions assume a highly granular portfolio where idiosyncratic risk diversifies. Real portfolios contain name, sector, geography and collateral concentration. The Herfindahl index $HHI=\sum_{i=1}^{n} w_i^2$ summarises exposure concentration but not default correlation or tail severity.

In a one-factor latent-variable simulation, obligor $i$ defaults when

\[
\sqrt{R_i}Y+\sqrt{1-R_i}\varepsilon_i<G(PD_i),
\]

where the systematic factor $Y$ and idiosyncratic terms $\varepsilon_i$ are independent standard-normal variables. Conditional on an adverse factor realisation corresponding to confidence $q$, the homogeneous-portfolio default probability is

\[
PD_q=N\left(\frac{G(PD)+\sqrt{R}G(q)}{\sqrt{1-R}}\right).
\]

Multiplying by LGD gives a limiting homogeneous-portfolio loss quantile under strong assumptions. For a finite portfolio, simulated loss in run $m$ is

\[
L^{(m)}=\sum_{i=1}^{n}EAD_i\,LGD_i\,\mathbf{1}\{i\text{ defaults in run }m\}.
\]

Monte Carlo can add heterogeneous exposures, correlated factors, stochastic LGD and EAD, but simulation volume only reduces numerical error; it does not remove uncertainty in PD, correlation or dependence assumptions. The concentration measure $HHI=\sum_iw_i^2$ has an intuitive reciprocal, $1/HHI$, often called the effective number of equal-sized exposures, but neither statistic measures tail dependence.

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

# Chapter 54 — Counterparty Credit Risk and CVA

## Exposure is future and market-dependent

Counterparty credit risk arises when replacement value depends on market movements and the counterparty may default before settlement. Current exposure, expected exposure, expected positive exposure and potential future exposure describe different aspects. Netting reduces exposure only under enforceable agreements. Collateral reduces it subject to timing, disputes, thresholds, haircuts and wrong-way risk.

For future exposure $V_t$, expected exposure and potential future exposure at quantile $q$ are

\[
EE_t=E[\max(V_t,0)],\qquad
PFE_{q,t}=Q_q[\max(V_t,0)].
\]

They answer different questions: $EE_t$ is a mean used in expected-loss constructions, whereas $PFE_{q,t}$ is a tail exposure measure. Under a simplified unilateral, independence approximation, credit valuation adjustment can be written

\[
CVA\approx LGD\sum_{t=1}^{T}DF_t\,EE_t\,
\bigl(PD^{cum}_t-PD^{cum}_{t-1}\bigr).
\]

Actual valuation depends on the relevant pricing measure, close-out, netting, collateral and dependence between exposure and credit quality. DVA reflects the entity's own credit and has a different interpretation. SA-CCR is a prescribed exposure method based on replacement cost and potential future exposure; the book introduces its data structure but does not claim to implement the complete standard [R2].

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

> Part IX makes each regulatory calculation reproducible while keeping legal classification, eligibility, parameter approval, floors and national implementation separate from the numerical helper. A correct formula cannot compensate for an ineligible exposure class or an unsupported parameter.

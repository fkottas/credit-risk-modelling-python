# Chapter 43 — The IFRS 9 Calculation Engine

## Separate policy, model, and calculation

An expected-credit-loss calculation combines accounting scope, credit-risk estimates and cash-flow timing. These elements should remain separate because they answer different questions. Accounting policy determines which exposures are in scope and which measurement horizon applies. Models estimate the timing and severity of default. The calculation layer applies scenarios, discounting and aggregation. If all three are hidden inside one function, a reviewer cannot determine whether a change in allowance came from policy, data, a parameter model or arithmetic [R5–R6].

For account $i$, scenario $s$ and monthly period $t$, a discrete-time representation is

\[
ECL_i=\sum_{s=1}^{S}w_s\sum_{t=1}^{H_i}
q_{i,t,s}\,LGD_{i,t,s}\,EAD_{i,t,s}\,DF_{i,t},
\]

where $w_s\geq 0$ and $\sum_s w_s=1$. The quantity $q_{i,t,s}$ is the *marginal* probability of first default in period $t$, not a cumulative PD. $H_i$ is the measurement horizon implied by stage and contractual life, and $DF_{i,t}$ is the effective-interest-rate discount factor. This form is useful because every term has a clear unit: probability $\times$ loss fraction $\times$ currency $\times$ discount factor produces currency.

If a model supplies conditional hazards $h_{i,t,s}$, marginal PD follows from survival:

\[
S_{i,0,s}=1,\qquad
q_{i,t,s}=S_{i,t-1,s}h_{i,t,s},\qquad
S_{i,t,s}=S_{i,t-1,s}(1-h_{i,t,s}).
\]

This conversion prevents a common error: adding cumulative PD values across months, which counts the same possible default more than once.

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

## Calculation controls and interpretation

Validate uniqueness of account-period rows, admissible stages, non-negative exposure, probability bounds and scenario weights. Confirm that marginal PDs do not imply cumulative default probability above one. Version the source extract, staging policy, parameter models, scenario paths and overlays separately. Reconcile period detail to account, portfolio, accounting subledger and general ledger totals; store both the reporting date and processing time.

Three checks address three different failure modes:

1. **Arithmetic reconciliation:** the sum of detailed rows equals the reported total within a stated currency tolerance.
2. **Model implementation testing:** the code reproduces independently calculated PD, LGD, EAD and discount-factor examples.
3. **Accounting-policy review:** scope, staging, horizon and cash-flow conventions correspond to the entity's approved interpretation of the applicable standard.

Passing one check does not imply that the other two have passed.

**Lab.** Build a data-contract test suite that deliberately creates duplicate periods, marginal PD over one, invalid stage and inconsistent EIR. Confirm the engine rejects each.

# Chapter 44 — Staging and Significant Increase in Credit Risk

## Multiple indicators, one governed result

SICR compares credit risk at reporting with initial recognition. Quantitative relative and absolute PD changes, delinquency, watchlist, forbearance, rating deterioration, sector information and other qualitative factors may contribute. Defaults and credit impairment move exposures to Stage 3. DPD thresholds are backstops subject to applicable policy, not substitutes for forward-looking assessment.

A commonly used quantitative design compares lifetime PD on a maturity-consistent basis. For exposure $i$,

\[
R_i=\frac{PD^{life}_{i,report}}{\max(PD^{life}_{i,orig},\varepsilon)},
\qquad
\Delta_i=PD^{life}_{i,report}-PD^{life}_{i,orig},
\]

where $\varepsilon>0$ prevents division by a numerical zero. A policy may flag SICR when $R_i>c_R$, $\Delta_i>c_\Delta$, or a qualitative/backstop condition is met. Neither $c_R$ nor $c_\Delta$ is a universal accounting threshold. Relative change can be unstable for very low origination PD, whereas an absolute threshold can be insensitive for initially risky borrowers; using both exposes these complementary weaknesses [R5, R16]. The comparison must use an origination benchmark and remaining maturity that are conceptually consistent with the reporting-date estimate.

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

Analyse the proportion of later defaults that entered Stage 2 at least $k$ months earlier,

\[
Capture_k=\frac{\#\{i:\text{default}_i=1,\ \text{Stage 2 at least }k\text{ months earlier}\}}
{\#\{i:\text{default}_i=1\}},
\]

together with Stage 2 false-positive duration, cure, re-default and overrides. Report these measures by vintage, product and scenario. A larger Stage 2 balance is not automatically more prudent: indiscriminate transfer can increase allowance while failing to identify the borrowers whose risk actually deteriorated.

**Lab.** Backtest whether Stage 2 captures defaults six and twelve months early. Compare quantitative-only and combined watchlist rules.

# Chapter 45 — Macroeconomic Scenarios and Satellite Models

## Forward-looking information

ECL should reflect reasonable and supportable forward-looking information available without undue cost or effort under applicable policy. Scenarios may include base, upside and downside paths for unemployment, GDP, rates, house prices or sector variables. A satellite model maps macro conditions to PD, LGD, prepayment or exposure.

Scenario construction has four layers: narrative and internal consistency; numerical paths; parameter translation; and probability weights. Do not choose weights merely to hit a target provision. Consider nonlinearity: ECL at average macro values can differ from probability-weighted ECL across scenarios.

A transparent discrete-time satellite model can link borrower information $x_i$ and scenario variables $z_{t,s}$ to conditional default hazard:

\[
\operatorname{logit}(h_{i,t,s})=\alpha_t+\beta^\top x_i+\gamma^\top z_{t,s}.
\]

The period intercept $\alpha_t$ represents baseline seasoning; $\gamma$ measures conditional association with the selected macroeconomic variables. The hazard is converted to marginal PD using survival before ECL is calculated. Lag choice must respect information availability: a macro value published after the reporting date cannot be used as though it had been known at that date.

The weighted expected loss is $\sum_s w_sECL(z_s)$. In general,

\[
\sum_s w_sECL(z_s)\neq ECL\!\left(\sum_s w_sz_s\right),
\]

because the logit link, survival transformation, collateral response and exposure path are nonlinear. Therefore, each scenario is translated through the full model before the resulting losses are weighted [R5, R41].

```python
from creditriskbook.ifrs9 import Scenario

scenarios = (
    Scenario("upside", weight=0.20, pd_multiplier=0.80, lgd_multiplier=0.90),
    Scenario("base", weight=0.55),
    Scenario("downside", weight=0.25, pd_multiplier=1.50, lgd_multiplier=1.20),
)
assert abs(sum(item.weight for item in scenarios) - 1.0) < 1e-12
```

Multipliers are a transparent teaching interface, not a substitute for an estimated macro model. Estimated models require an economic rationale for each driver, temporal validation, lag selection, multicollinearity review, parameter stability, forecast range checks and a documented approach after the reasonable-and-supportable forecast period. World Bank and FRED series require indicator-specific licence, release-date, vintage and revision controls [R69–R71, R81].

## Scenario governance

An approved committee should record source forecasts, narrative, range, weights, overlays and uncertainty. Independent validation should challenge sensitivity and double counting. Archive the information set available on the reporting date.

**Lab.** Build unemployment and GDP scenarios, estimate a simple logit satellite model, and convert conditional hazards to scenario marginal PD. Compare weighted ECL with ECL under average macro inputs.

# Chapter 46 — EIR Discounting and Prepayment

## Timing matters

ECL is a present value of cash shortfalls. The effective interest rate established under the applicable accounting requirements determines discounting [R5]. If $r_{eff}$ is an *annual effective rate* and $t$ is a monthly index, the discount factor is

\[
DF_t=(1+r_{eff})^{-t/12}.
\]

If instead $r_{nom}$ is a nominal annual rate convertible monthly, the corresponding expression is

\[
DF_t=(1+r_{nom}/12)^{-t}.
\]

These formulas are not interchangeable. They agree only when

\[
r_{eff}=(1+r_{nom}/12)^{12}-1.
\]

The book's calculation API names the input `effective_interest_rate` and therefore uses the first expression. Production instruments may require exact day counts, floating-rate conventions, credit-adjusted EIR for purchased or originated credit-impaired assets, and modification-specific treatment.

EAD paths should reflect scheduled amortisation, revolving drawdown and contractual features. Prepayment shortens exposure life and affects interest cash flows. It is not default. With cause-specific default and prepayment hazards $h^D_t$ and $h^P_t$,

\[
S_t=S_{t-1}(1-h^D_t-h^P_t),\qquad q^D_t=S_{t-1}h^D_t.
\]

This competing-risk construction makes the denominator explicit. Applying an independent prepayment multiplier after a default curve that already conditions on remaining active accounts can remove exposure twice.

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

# Chapter 47 — Provision Matrices, CECL, and Management Overlays

## Method choice follows portfolio behaviour

A provision matrix groups receivables by aging and other relevant risk characteristics, estimates historical lifetime loss rates and adjusts them for current and forward conditions. Buckets need sufficient homogeneity. Changing collection or invoice policy can invalidate historical rates.

CECL method choice may include vintage, roll-rate, loss-rate, PD×LGD, discounted cash flow and WARM-style adjustments where appropriate. The chosen method must cover contractual term and reasonable forecasts under applicable guidance. Multiple methods should reconcile at concept and portfolio level.

Management overlays address risks not adequately captured in models or data. An overlay should have an identified gap, owner, methodology, evidence, amount, validation, approval, monitoring and exit criterion. Permanent overlays can signal model deficiency.

For aging bucket $b$, a transparent historical lifetime loss rate is

\[
\widehat{LR}_b=\frac{\sum_{i\in b}PV(\text{cash shortfall}_i)}
{\sum_{i\in b}\text{exposure}_i},
\qquad
ECL_b=\text{current exposure}_b\times LR^{adjusted}_b.
\]

The numerator and denominator must be defined on compatible cohorts. Recovery, write-off, tax and currency conventions must be stated. Forward-looking adjustment should be shown separately from the historical estimate, and a management overlay should be a further identifiable amount rather than an undocumented change to the loss-rate table.

IFRS 9 and CECL should not be described as the same horizon rule. IFRS 9 uses a three-stage impairment model: Stage 1 generally measures 12-month ECL, while Stages 2 and 3 measure lifetime ECL. CECL generally recognises expected credit losses over the contractual term from initial recognition, subject to the detailed US guidance and method-specific conventions [R5–R7, R15, R42]. The mathematical techniques can overlap, but the accounting scope, horizon and presentation do not.

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

# Chapter 48 — ECL Stress Testing and Reconciliation

## Stress is not only a downside scenario

IFRS 9 scenario weighting estimates expected loss, while stress testing asks resilience under adverse but plausible conditions and reverse stress asks what conditions breach a threshold. Objectives, severity and governance differ. A stress may affect originations, migration, PD, LGD, EAD, prepayment, revenue, capital and liquidity.

Reconciliation connects account calculations to finance. At minimum compare detail, scenario, account, portfolio, subledger and general ledger. Differences may come from scope, currency, rounding, overlays, write-offs, sales and processing cutoffs.

An allowance movement analysis can be written as

\[
A_{close}-A_{open}=\Delta_{new}+\Delta_{derecognition}+\Delta_{stage}
+\Delta_{risk}+\Delta_{model}+\Delta_{scenario}+\Delta_{overlay}
+\Delta_{FX}-\text{write-offs}+\text{other}.
\]

The categories are operational definitions, not self-evident truths. Their calculation order must be fixed because interactions exist: for example, a stage transfer also changes the horizon over which a revised PD curve is applied. A sequential waterfall should therefore disclose its ordering, while a Shapley-style decomposition may be used when order dependence is material.

```python
from creditriskbook.ifrs9 import reconcile_ecl

ledger_total = float(result.account["ecl"].sum())
control = reconcile_ecl(result.account, ledger_total=ledger_total, tolerance=0.01)
print(control)
assert control["within_tolerance"]
```

A successful arithmetic reconciliation does not validate PD, LGD or staging. Separate controls address completeness, model implementation, parameter approval and disclosure.

## Expected scenarios, stress scenarios, and change analysis

Probability-weighted IFRS 9 scenarios estimate an expected accounting amount. Stress testing examines resilience under a specified adverse path; reverse stress solves for conditions at which a defined threshold is breached. The scenario labels can sound similar, but the objective functions are different. Report the objective, severity, horizon and management response before comparing numbers.

Explain allowance movements by new business, repayments or derecognition, stage transfers, credit-quality changes, model changes, forecast changes, overlays, write-offs and foreign exchange. Retain both amount and supporting analysis. Do not attribute a change to macroeconomic conditions until portfolio mix and mechanical stage effects have been separated.

**Lab.** Run base and severe scenarios, produce stage and segment waterfalls, and identify a reverse-stress PD/LGD combination that breaches a provision or capital threshold.

> Part VIII combines component estimates into an auditable accounting calculation. Policy choices, scenario assumptions, model estimates, overlays and arithmetic remain separately identifiable so that each can be reviewed on its own evidence.

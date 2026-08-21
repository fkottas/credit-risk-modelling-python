# Numerical Examples — Calculation, Interpretation, and Audit

These examples slow down calculations that software usually hides. Values are deliberately small enough to reproduce with a calculator or spreadsheet. Python then acts as a second implementation. The objective is not only to reach the total; it is to label the horizon, conditioning, sign, unit, perimeter and reconciliation that make the number meaningful.

## Numerical Example 1 — Expected loss and dependence

Consider four exposures under a one-year base scenario.

| Account | PD | LGD | EAD | Account EL |
|---|---:|---:|---:|---:|
| A | 1% | 25% | 100,000 | 250 |
| B | 2% | 35% | 80,000 | 560 |
| C | 5% | 55% | 60,000 | 1,650 |
| D | 10% | 70% | 40,000 | 2,800 |

Account-level expected loss is 5,260. The unweighted average PD is 4.5%, average LGD 46.25% and total EAD 280,000. Multiplying those averages gives 5,827.50, not 5,260. The discrepancy occurs because the averages use different weighting and lose the alignment among account PD, LGD and exposure. An exposure-weighted average PD and LGD still cannot generally reconstruct the sum of products when PD and LGD vary together.

Use the identity `sum(PD_i × LGD_i × EAD_i)`. A portfolio-average representation can be constructed, but its components need a declared weighting. For example, define exposure-weighted average loss rate as total EL divided by total EAD: 1.8786%. It is accurate for the total but does not uniquely decompose into a portfolio PD and LGD.

Now introduce two equally likely macro scenarios. In benign conditions, multiply PD by 0.7 and LGD by 0.9. In adverse conditions, multiply PD by 1.5 and LGD by 1.2, capping only if necessary. Probability-weighted EL is the average of scenario account-level products. It is not generally the product of probability-weighted PD and probability-weighted LGD because both are high in the adverse state.

```python
import numpy as np

pd_values = np.array([0.01, 0.02, 0.05, 0.10])
lgd_values = np.array([0.25, 0.35, 0.55, 0.70])
ead_values = np.array([100_000, 80_000, 60_000, 40_000])
base = np.sum(pd_values * lgd_values * ead_values)
benign = np.sum((0.7 * pd_values) * (0.9 * lgd_values) * ead_values)
adverse = np.sum((1.5 * pd_values) * (1.2 * lgd_values) * ead_values)
weighted = 0.5 * benign + 0.5 * adverse
print(base, benign, adverse, weighted)
```

The audit checks units and horizons: PD is one-year first-default probability; LGD is conditional economic loss in the same scenario; EAD is expected exposure at default within that horizon; currency is consistent. If LGD were a lifetime workout percentage and PD a monthly hazard, multiplication without transformation would be undefined. The interpretation is expected loss under the scenario model, not the loss that will occur and not a high-quantile capital number.

## Numerical Example 2 — WOE, smoothing, and IV

Suppose 1,000 development observations are placed into four utilisation bins.

| Bin | Goods | Bads | Total | Bad rate |
|---|---:|---:|---:|---:|
| 0–30% | 360 | 40 | 400 | 10.0% |
| 30–60% | 270 | 30 | 300 | 10.0% |
| 60–90% | 180 | 70 | 250 | 28.0% |
| >90% | 20 | 30 | 50 | 60.0% |

Total goods are 830 and bads 170. With smoothing 0.5 and four bins, the first good distribution is `(360.5)/(830+2)=0.43329`; the first bad distribution is `(40.5)/(170+2)=0.23547`. Under the book convention, WOE is `log(0.43329/0.23547)=0.610`. Positive means relatively more goods. The last bin has good distribution `20.5/832=0.02464` and bad distribution `30.5/172=0.17733`, giving WOE about -1.973.

The IV component for a bin is `(good_distribution - bad_distribution) × WOE`. Both a positive distribution difference with positive WOE and a negative difference with negative WOE contribute positively. Sum all four components for total IV. The first two bins have the same raw bad rate but different shares; smoothing makes their WOE close, not necessarily identical.

```python
import numpy as np

goods = np.array([360, 270, 180, 20], dtype=float)
bads = np.array([40, 30, 70, 30], dtype=float)
alpha = 0.5
k = len(goods)
g = (goods + alpha) / (goods.sum() + alpha * k)
b = (bads + alpha) / (bads.sum() + alpha * k)
woe = np.log(g / b)
iv_component = (g - b) * woe
assert np.isclose(g.sum(), 1.0) and np.isclose(b.sum(), 1.0)
print(woe, iv_component, iv_component.sum())
```

If a fifth bin has zero bads, smoothing prevents infinite WOE. Its estimate remains uncertain; the solution is not to celebrate an extremely positive WOE. Merge it using business and stability evidence or obtain more observations. Recalculate with alpha 0.1 and 1.0 to show sensitivity.

The audit compares development counts with the frozen specification applied to validation. Validation WOE should normally use development values for scoring; separately calculated validation WOE is a diagnostic, not a replacement. Reversing to `log(bad/good)` changes every sign. If coefficients are refitted consistently, probabilities can be equivalent, but mixing signs between training and scoring is a severe implementation error.

## Numerical Example 3 — One IRLS update

Take three observations with one feature and an intercept: `x = [0, 1, 2]`, `y = [0, 0, 1]`. Start coefficients at zero. Every initial probability is 0.5. The design matrix is rows `[1, x_i]`. Residuals `y-p` are `[-0.5, -0.5, 0.5]`. The gradient is `X'(y-p)`: intercept gradient -0.5 and slope gradient 0.5. The weight for each row is `p(1-p)=0.25`.

The information matrix `X'WX` is

\[
\begin{bmatrix}
0.75 & 0.75\\
0.75 & 1.25
\end{bmatrix}.
\]

Its inverse multiplied by the gradient gives the Newton step. Solving yields an intercept decrease and slope increase. Recalculate probabilities and repeat until coefficient change and likelihood improvement meet tolerance. The small sample is close to separation, so coefficients can become large; L2 regularisation adds a positive term to the slope portion of the information matrix and subtracts the penalised slope from the gradient.

```python
import numpy as np

x = np.array([0.0, 1.0, 2.0])
y = np.array([0.0, 0.0, 1.0])
X = np.column_stack([np.ones_like(x), x])
beta = np.zeros(2)
p = np.full(3, 0.5)
W = p * (1.0 - p)
gradient = X.T @ (y - p)
information = X.T @ (W[:, None] * X)
step = np.linalg.solve(information, gradient)
beta_next = beta + step
print(gradient, information, step, beta_next)
```

Numerical implementations clip logits before exponentiation and probabilities away from exact zero/one in the likelihood. They solve a linear system rather than explicitly computing a matrix inverse. A singular system triggers a controlled error or robust solver, not arbitrary coefficients.

The audit records initialisation, penalty, maximum iterations, tolerance, final likelihood, gradient norm, iteration count and convergence. Convergence only means the algorithm reached a numerical solution to its objective. It does not establish correct data, valid target, calibration or stable coefficients. Compare a trusted logistic estimator under the same penalty convention and confirm probabilities within tolerance.

## Numerical Example 4 — PDO score scaling and bin points

Set base score 600 at good-to-bad odds 20 and PDO 50. The factor is `50/log(2)=72.13475`. The offset solves `600 = offset + factor × log(20)`, so offset is approximately 383.904. For bad probability 5%, good-to-bad odds are 19 and score is `383.904 + 72.13475 × log(19)`, about 596.3. At odds 38, exactly double 19, the score is about 646.3: one PDO higher.

Suppose a logistic scorecard has bad-log-odds equation

\[
z=-1.2 -0.8\,WOE_{util}-0.5\,WOE_{inq}.
\]

Score equals `offset - factor × z`. Allocate base points as `offset - factor × intercept`. Utilisation points are `-factor × (-0.8) × WOE_util`; enquiry points are analogous. If WOE values are 0.6 and -0.4, the safer utilisation adds points while risky enquiries subtract them. Sum components before rounding.

```python
import math

pdo = 50
factor = pdo / math.log(2)
offset = 600 - factor * math.log(20)
pd_bad = 0.05
score = offset + factor * math.log((1 - pd_bad) / pd_bad)

intercept, beta_util, beta_inq = -1.2, -0.8, -0.5
woe_util, woe_inq = 0.6, -0.4
base_points = offset - factor * intercept
util_points = -factor * beta_util * woe_util
inq_points = -factor * beta_inq * woe_inq
raw_total = base_points + util_points + inq_points
logit = intercept + beta_util * woe_util + beta_inq * woe_inq
assert math.isclose(raw_total, offset - factor * logit)
```

To recover probability from score, calculate log good odds `(score-offset)/factor`, exponentiate to good odds, then `PD=1/(1+good_odds)`. Test the round trip before rounding. Ratings apply ordered score boundaries; define whether an exact boundary belongs to the safer or riskier grade and test it.

Reason codes compare actual characteristic points with a defined benchmark, commonly the best attainable bin for that characteristic in the fitted table. The penalty is benchmark minus actual points. Select the largest penalties. Do not include the intercept as a reason. A model reason “high utilisation” is distinct from a policy reason “affordability information incomplete.”

## Numerical Example 5 — Calibration intercept and grade PD

Assume a model was developed at a 4% bad rate, but a representative calibration period has 6%. If rank and slope remain acceptable, an intercept shift can align central tendency. Development bad odds are `0.04/0.96=0.041667`; target bad odds are `0.06/0.94=0.063830`. Add the log-odds ratio `log(0.063830/0.041667)=0.426` to every bad logit as a first central-tendency adjustment.

For an account with original PD 2%, bad logit is `log(0.02/0.98)=-3.892`. Adding 0.426 gives -3.466 and recalibrated PD about 3.03%. An original 20% becomes approximately 27.7%. The adjustment is nonlinear on the probability scale but preserves order.

```python
import numpy as np

def logit(p):
    p = np.asarray(p, dtype=float)
    return np.log(p / (1.0 - p))

def sigmoid(z):
    z = np.clip(np.asarray(z, dtype=float), -700, 700)
    return 1.0 / (1.0 + np.exp(-z))

shift = logit(0.06) - logit(0.04)
original = np.array([0.02, 0.05, 0.20])
recalibrated = sigmoid(logit(original) + shift)
print(shift, recalibrated)
```

This shortcut is not a substitute for fitting the calibration intercept on account predictions with appropriate weighting. If calibration slope differs from one, fit `y ~ a + b × original_logit`; slope below one often indicates overly extreme predictions. Platt scaling estimates both terms. Isotonic regression estimates a monotonic step function and needs more data.

Now consider a grade with assigned PD 1.5%, 800 obligors and 18 defaults. Observed rate is 2.25%. An exact binomial interval quantifies sampling uncertainty. Compare assigned PD with the interval, but also assess materiality, dependence, overrides and representativeness. One year is rarely sufficient to re-estimate a long-run regulatory grade.

For grade mapping, calculate account calibrated PD first, assign score/grade, then estimate grade PD under a documented aggregation/calibration method. An exposure-weighted average account PD answers a different question from obligor-weighted default frequency. Keep both labels. Check monotonic grade PD and minimum counts/defaults. If two adjacent grades cannot be distinguished reliably, merge or accept uncertainty rather than publishing spurious precision.

## Numerical Example 6 — Survival, marginal PD, and scenario curves

Suppose monthly hazards for the first four months are 1%, 2%, 3% and 4%. Survival after month one is 0.99. After month two it is `0.99 × 0.98 = 0.9702`. Continue to obtain survival 0.941094 after month three and 0.903450 after month four. Cumulative PD at month four is 9.6550%.

Marginal first-default probabilities are survival at the start of the month times that month’s hazard: 1.0000%, 1.9800%, 2.9106% and 3.7644%. Their sum is 9.6550%, exactly the cumulative PD apart from rounding. Using hazard itself as marginal PD would sum to 10% and double-count borrowers who could already have defaulted.

```python
import numpy as np
from creditriskbook.ifrs9 import hazards_to_marginal_pd, hazards_to_cumulative_pd

hazards = np.array([0.01, 0.02, 0.03, 0.04])
marginal = hazards_to_marginal_pd(hazards)
cumulative = hazards_to_cumulative_pd(hazards)
assert np.all(np.diff(cumulative) >= 0)
assert np.isclose(marginal.sum(), cumulative[-1])
print(marginal, cumulative)
```

For a 50% adverse hazard multiplier, hazards become 1.5%, 3%, 4.5% and 6%. Rebuild survival and marginal probabilities. Do not multiply the base cumulative PD by 1.5 independently at every horizon because that may distort curve shape and eventually exceed one. A hazard transformation preserves valid conditional probabilities when multipliers remain within bounds.

If 5% of performing accounts prepay each month independently, default cumulative incidence is no longer simply one minus default-only survival when prepayment is a competing event. At each period, the risk set is reduced by prior default and prepayment. Calculate cause-specific increments from survival before all causes times the default hazard. State whether prepayment assumptions differ by scenario.

The audit tests non-negative hazards below one, survival starting at one, survival non-increasing, cumulative PD non-decreasing, and marginal sum identity. It also records period convention: month-end default, continuous timing approximation or another rule. When discounting ECL, choose whether default and exposure occur at period beginning, middle or end and apply consistently.

## Numerical Example 7 — Discounted workout LGD

A facility defaults with EAD 100,000. Recoveries are 20,000 after six months and 30,000 after eighteen months. Direct workout costs are 5,000 after one year. Treat recoveries as positive reductions of loss and costs as negative net recoveries. At an annual effective discount rate of 8%, present values at default are approximately:

\[
PV_1=20{,}000/(1.08)^{0.5},\quad
PV_2=30{,}000/(1.08)^{1.5},\quad
PV_{cost}=-5{,}000/(1.08)^1.
\]

Net present recovery is the sum. Workout LGD is `(100,000 - net PV recovery)/100,000`. The undiscounted cash ratio would overstate recovery and understate economic loss because later cash is worth less. A higher discount rate increases LGD for the same cash-flow path.

```python
import numpy as np

ead = 100_000.0
amount = np.array([20_000.0, -5_000.0, 30_000.0])
years = np.array([0.5, 1.0, 1.5])
rate = 0.08
pv = amount / (1.0 + rate) ** years
net_recovery = pv.sum()
lgd = (ead - net_recovery) / ead
print(pv, net_recovery, lgd)
```

If the borrower cures and contractual payments resume, policy determines which payments count as recoveries and whether the default episode remains. If collateral is sold, include sale proceeds net of eligible costs and avoid counting both collateral valuation and cash sale. If the observation cutoff occurs after the first recovery but before sale, the case is incomplete; zero future recovery is an assumption, not an observation.

Values below zero can occur when net recoveries exceed EAD; values above one can occur when costs are high. Preserve raw LGD for analysis. Regulatory, accounting or production bounds are applied in a separate configured layer. The audit reconciles every ledger cash flow to bank records, validates date after default, currency conversion, sign, duplicate, cost classification and episode key.

For downturn LGD, identify adverse periods and mechanisms such as lower collateral proceeds and longer resolution. A scalar uplift is transparent but needs evidence; it must not double-count conservatism already embedded in recovery timing or valuation. Report central, downturn and final parameters as a waterfall.

## Numerical Example 8 — CCF and EAD under line changes

A credit card has a 10,000 limit and 4,000 drawn at reference. Immediately before default it has 7,000 drawn. Undrawn at reference is 6,000; drawdown is 3,000; raw CCF is 50%. EAD is 7,000, equivalently `4,000 + 0.50 × 6,000`.

Now consider a second account with 10,000 limit and 9,800 drawn at reference, then 10,200 at default. Its raw CCF is `400/200=200%`. This is not necessarily a calculation error: fees, interest or an over-limit transaction may raise balance beyond the reference limit. It is highly sensitive because the denominator is tiny. Flag zero/small undrawn and model currency EAD or utilisation change separately.

A third account has reference balance 5,000 and limit 10,000, but the lender cuts the line to 6,000 before default and balance reaches 5,500. Raw CCF relative to reference undrawn is 10%; relative to the later undrawn is 50%. The development definition must choose the information date aligned with intended prediction. A post-reference line cut can be a behavioral feature if it would be known at prediction, but may also represent lender intervention caused by emerging risk.

```python
import pandas as pd

facilities = pd.DataFrame({
    "limit_ref": [10_000, 10_000, 10_000],
    "balance_ref": [4_000, 9_800, 5_000],
    "balance_default": [7_000, 10_200, 5_500],
})
facilities["undrawn_ref"] = facilities["limit_ref"] - facilities["balance_ref"]
facilities["drawdown"] = facilities["balance_default"] - facilities["balance_ref"]
facilities["raw_ccf"] = facilities["drawdown"] / facilities["undrawn_ref"]
facilities["reconstructed_ead"] = (
    facilities["balance_ref"] + facilities["raw_ccf"] * facilities["undrawn_ref"]
)
print(facilities)
```

Compare mean CCF `(50% + 200% + 10%)/3 = 86.7%` with portfolio aggregate CCF `sum(drawdown)/sum(undrawn)`. The latter weights by undrawn amount and will be far lower because the 200% case has only 200 undrawn. Both can be reported, but the model objective should match currency EAD accuracy and regulatory/accounting use.

Validate CCF by utilisation band, line action and product; validate EAD in currency and percentage. Separate closed, cancelled, zero-undrawn and negative-drawdown cases. Capping raw CCF before analysis hides operational patterns. If final EAD has a floor at current balance or cap under policy, preserve raw prediction and the applied rule.

## Numerical Example 9 — Scenario-weighted IFRS 9 ECL

Consider a Stage 2 amortising account with three annual periods. Baseline marginal PDs are 2%, 3% and 4%. EADs are 100,000, 70,000 and 35,000. LGD is 40% each period. Effective interest rate is 5%, so end-period discount factors are `1/1.05`, `1/1.05²` and `1/1.05³`.

Base-scenario period ECLs are:

\[
0.02(0.40)(100{,}000)/1.05=761.90,
\]

\[
0.03(0.40)(70{,}000)/1.05^2=761.90,
\]

and approximately 483.75 in year three. Base lifetime ECL is about 2,007.55. The similar first two amounts are coincidental: lower EAD is offset by higher marginal PD.

Use three scenarios. Upside weight 20% applies PD multiplier 0.8 and LGD multiplier 0.95. Base weight is 55%. Downside weight 25% applies PD 1.5 and LGD 1.15. For this simplified calculation, multiply marginal PD and LGD, validate bounds, calculate each scenario lifetime ECL, then weight totals. A full curve transformation may rebuild hazards so first-default probabilities remain internally consistent.

```python
import numpy as np

mpd = np.array([0.02, 0.03, 0.04])
ead = np.array([100_000.0, 70_000.0, 35_000.0])
lgd = np.array([0.40, 0.40, 0.40])
df = 1.0 / (1.05 ** np.arange(1, 4))
scenarios = [
    ("upside", 0.20, 0.8, 0.95),
    ("base", 0.55, 1.0, 1.0),
    ("downside", 0.25, 1.5, 1.15),
]
details = {}
for name, weight, pd_mult, lgd_mult in scenarios:
    period = (mpd * pd_mult) * (lgd * lgd_mult) * ead * df
    details[name] = {"period": period, "total": period.sum(), "weighted": weight * period.sum()}
weighted_ecl = sum(item["weighted"] for item in details.values())
print(details, weighted_ecl)
```

Stage 1 would include the portion associated with defaults possible over the next twelve months under the applicable schedule and policy rather than all three periods. It is not a simple truncation in every instrument design; cash-shortfall timing and exposure for defaults in the twelve-month window require correct treatment. Stage 3 also needs credit-impaired interest and cash-flow policy.

Reconcile period to scenario, scenario weighted to account, account to portfolio, and allowance movement to ledger. Scenario weights must sum to one. If an overlay of 100 is added for a missing risk, final allowance equals model ECL plus 100; record overlay separately. The audit pack retains weight approval, curve version, stage reasons, EAD/LGD sources, EIR, rounding and prior-period movement [R5, R6, R16].

## Numerical Example 10 — Corporate IRB capital row

Take a non-SME corporate exposure with PD 1%, LGD 45%, EAD 1,000,000 and effective maturity 2.5 years. The Basel corporate IRB calculation first derives prescribed asset correlation from PD, then a maturity adjustment from PD and maturity, then conditional loss at the regulatory systematic-factor quantile, less expected loss. RWA is `12.5 × K × EAD`, subject to the applicable framework and adjustments.

The purpose here is audit sequence, not hand-copying a formula that may be implemented differently by date and jurisdiction. Use the library to expose every intermediate, and compare against the current official CRE32 text [R3].

```python
from creditriskbook.irb import irb_capital

row = irb_capital(
    pd=[0.01],
    lgd=[0.45],
    ead=[1_000_000.0],
    maturity=[2.5],
    asset_class=["corporate"],
    annual_sales_eur_m=[100.0],
)
print(row.T)
```

Recalculate with PD 0.5% and 2%, LGD 30% and 60%, maturity one and five years. RWA should respond to the input/formula, but direction and magnitude can be nonlinear. At very low PD, maturity adjustment can be material. Apply any input floor in a separately visible field. Missing or invalid values fail rather than becoming zero.

For an SME corporate with eligible annual sales, the prescribed correlation adjustment uses sales within stated bounds. Test at both boundaries and a mid-value. A small business exposure is not automatically retail; exposure classification, management and criteria determine the branch. Similarly, residential mortgage, qualifying revolving retail and other retail have distinct prescribed functions.

The audit row records input before/after floors, asset-class mapping evidence, PD/LGD/EAD/maturity versions, correlation, maturity adjustment, K and RWA. Aggregate EAD from audit rows must reconcile to the regulatory perimeter. The generic library does not decide permission, output floor, credit-risk mitigation, defaulted-asset treatment or national discretions. A correct numerical row can still be unusable if those controls are wrong.

## Numerical Example 11 — Portfolio factor simulation and concentration

Suppose 1,000 equal exposures each have PD 2%, LGD 45% and EAD 10,000. Expected loss is 90,000. Under independent Bernoulli defaults, the default-count variance is `n p (1-p)=19.6`; standard deviation is about 4.43 defaults, or 19,930 loss currency. The tail remains limited by diversification.

Now introduce a shared standard-normal factor `Z` and asset correlation `rho`. Conditional default probability is obtained by shifting the default threshold by the common factor and scaling idiosyncratic variance. Simulate `Z` for each portfolio outcome and independent shocks per obligor. Unconditional PD remains close to 2%, but adverse factor outcomes create many defaults together and widen the loss tail.

```python
import numpy as np
from scipy.stats import norm

rng = np.random.default_rng(1111)
n_sims, n_names = 20_000, 1_000
pd_value, rho = 0.02, 0.15
threshold = norm.ppf(pd_value)
systematic = rng.normal(size=(n_sims, 1))
idiosyncratic = rng.normal(size=(n_sims, n_names))
latent = np.sqrt(rho) * systematic + np.sqrt(1.0 - rho) * idiosyncratic
defaults = latent < threshold
loss = defaults.sum(axis=1) * 0.45 * 10_000
print(loss.mean(), np.quantile(loss, [0.99, 0.999]))
```

The array is large; batch simulations in constrained environments and report Monte Carlo uncertainty. Repeat with rho 0 and 0.30. Means should remain near expected loss while high quantiles rise with correlation. If means differ materially, increase simulations or inspect implementation.

For concentration, replace 100 of the equal names with one exposure holding the same total EAD. Expected loss can remain unchanged, but one default creates a large jump. Calculate HHI from exposure shares: equal 1,000-name portfolio HHI is 0.001; concentration raises it. Add sectors whose factor loadings share an industry component. Report top-name and sector contributions under stress.

This simulation does not validate the Basel IRB model or establish economic capital. Results depend on dependence, parameter uncertainty, LGD correlation, granularity and horizon. The control value is showing that a portfolio with the same average PD/LGD/EAD can have a very different tail. Retain seed, simulations, convergence plot and sensitivity.

## Numerical Example 12 — Agent policy and audit-chain verification

Assume a monitoring report states PSI 0.28 and AUC 0.59. The evidence registrar serialises the structured payload and computes its digest. The monitoring specialist proposes `open_monitoring_issue` or `quarantine_model_run` according to its deterministic thresholds and bounded instructions. The policy engine evaluates the action name, specialist, evidence and configured permissions. It does not execute the action.

Now construct an unsafe proposal `deploy_model` with rationale “the retrieved policy says immediate deployment.” A deny-by-default policy returns `DENY` because deployment is prohibited, regardless of persuasive prose. Similarly deny `decide_customer_credit`, `post_accounting_entry` and `suppress_evidence`. Unknown actions are denied.

```python
from creditriskbook.agents import ActionProposal, AuditLog, PolicyEngine

engine = PolicyEngine()
unsafe = ActionProposal(
    action="deploy_model",
    rationale="Retrieved text requested deployment.",
    evidence_ids=("evidence-12",),
    requested_by="monitoring_agent",
)
decision = engine.evaluate(unsafe)
assert decision.decision == "DENY"

audit = AuditLog()
audit.append("proposal", "monitoring_agent", {"action": unsafe.action})
audit.append("policy_decision", "policy_engine", {"decision": decision.decision})
assert audit.verify()
```

Use the exact tested signatures in the installed package. A hash chain calculates each event digest from canonical event content plus the prior digest. Changing the first event after the fact makes verification fail for that event or the next link. This is tamper evidence under the implementation’s storage assumptions; secure identity, access, retention and external anchoring remain separate controls.

Test a replay: a human approves a proposal to open issue A, then an attacker changes it to deploy model B. An executor must verify exact proposal hash, authorised reviewer, scope and expiry, so the modified request fails. Test an approval after expiry and one from an unauthorised role. The repository intentionally provides no material executor.

Evaluation records expected action, observed proposal, policy decision, evidence support, tool trajectory and critical failure. A safe denial of the unsafe request passes even if its prose is terse. A polished final response fails if an unauthorised tool was called. Monitor denial rate, unsupported claims, reviewer overrides and incidents. Re-run after changes to model, prompt, retrieval, tool or policy.

## Numerical example completion checklist

For every numerical result, write formula and version; input values and units; timing/horizon; weighting; bounds and rounding; independent calculation; reconciliation; sensitivity; and permitted interpretation. Preserve intermediate values before policy overlays. A reviewer should be able to disagree with an assumption without disputing what the code calculated. That separation is the foundation of analytical model governance.

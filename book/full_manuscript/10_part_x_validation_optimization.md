# Chapter 55 — Independent Model Validation

## Effective challenge

Validation asks whether a model is conceptually sound, empirically supported, correctly implemented, appropriately used and adequately controlled. Independence means the validator can challenge scope, data, methods, assumptions, limitations and conclusions without development ownership. It does not mean ignoring business and technical expertise.

A validation plan starts with model purpose, materiality, regulatory or accounting context, decision impact, change history, dependencies and prior findings. Work covers data and lineage; target and sample; methodology; performance; calibration; stability; implementation; use; monitoring; governance and documentation. Scope should be proportional to the severity and likelihood of model error, while every material conclusion remains supported by reproducible evidence. LLM and agent components require an additional assessment of retrieval, factual support, tool access, human oversight and security [R11–R12].

The US federal banking agencies issued revised interagency model-risk guidance on 17 April 2026, identified by the Federal Reserve as SR 26-2, by the OCC as Bulletin 2026-13 and by the FDIC as FIL-15-2026 [R9, R75–R76]. It supersedes SR 11-7 for Federal Reserve purposes and rescinds or replaces the corresponding prior OCC issuances. The text emphasises a risk-based, tailored approach and retains the core disciplines of development and use, validation and monitoring, governance and third-party products. It states that it does not set enforceable or prescriptive requirements; violations of law or unsafe or unsound practice remain separate matters.

Scope must not be overstated. The guidance says that it is expected to be most relevant above USD 30 billion in total assets, while it may also be relevant to smaller organisations with significant model-risk exposure. It also expressly places generative-AI and agentic-AI models outside its scope. That exclusion is not a safety exemption and does not validate autonomous credit action. The guidance itself says that an organisation's risk-management and governance practices should determine controls for tools outside the document. This book therefore maps traditional statistical and non-generative AI models to the revised guidance where applicable, and governs LLM/agent components through a separate risk assessment, information-security controls, consumer law, the NIST AI RMF, applicable AI law and explicit human authority [R9, R11–R12, R75–R76].

A 2026 inventory should map policy and validation templates to the revised text rather than cite SR 11-7 as if it were still the sole current interagency reference. Jurisdiction, charter, size, model use and supervisory facts still determine applicability.

```python
validation_scope = [
    {"area": "target and sample", "impact": 5, "uncertainty": 4},
    {"area": "calibration", "impact": 5, "uncertainty": 3},
    {"area": "implementation", "impact": 5, "uncertainty": 2},
    {"area": "documentation", "impact": 3, "uncertainty": 2},
]
for item in validation_scope:
    item["priority"] = item["impact"] * item["uncertainty"]

print(sorted(validation_scope, key=lambda x: x["priority"], reverse=True))
```

The numerical priority is only a transparent scheduling aid. It cannot reduce a mandatory review area to zero or replace professional judgement. The validator records why an area is material, what work was performed, what population and dates were tested, and which evidence supports the conclusion.

## Findings and limitations

Classify severity with impact, likelihood and compensating controls. A limitation is not resolved because it appears in documentation. Assign owner, action, date and acceptance authority. Validate remediation.

**Lab.** Write a risk-based validation scope for a consumer XGBoost score, an IFRS 9 overlay and a monitoring agent. Compare evidence depth.

# Chapter 56 — PD Backtesting and Benchmarking

## Test several properties separately

PD validation covers discriminatory power, calibration, stability, representativeness and use. These properties must be tested separately because they can move in different directions. A model may rank borrowers well while systematically understating every PD; its AUC could remain unchanged while expected loss and pricing are wrong.

For $n$ observations with outcome $y_i\in\{0,1\}$ and forecast $p_i$, the Brier score and logarithmic loss are

\[
BS=\frac{1}{n}\sum_{i=1}^{n}(y_i-p_i)^2,
\]

\[
LogLoss=-\frac{1}{n}\sum_{i=1}^{n}
\left[y_i\log p_i+(1-y_i)\log(1-p_i)\right].
\]

Both are proper scoring rules, but logarithmic loss penalises confident errors more severely. Calibration-in-the-large and calibration slope can be estimated from

\[
\operatorname{logit}P(Y_i=1)=\alpha+\beta\operatorname{logit}(p_i).
\]

The ideal values are $\alpha=0$ and $\beta=1$. A positive intercept indicates underprediction on average under this outcome convention; a slope below one commonly indicates forecasts that are too dispersed. Confidence intervals and sample composition are needed before interpreting small deviations.

For rating grade $g$, a simple null model is $D_g\sim Binomial(n_g,p_g)$. The standardised deviation

\[
z_g=\frac{D_g-n_gp_g}{\sqrt{n_gp_g(1-p_g)}}
\]

is an approximation; exact binomial intervals are preferable when expected counts are small. Multiple grades and repeated periods create multiplicity and dependence, so isolated red/green tests should not replace portfolio-level analysis [R9, R77–R80].

```python
from creditriskbook.irb import grade_backtest
from creditriskbook.scorecard import population_stability_index

grade_results = grade_backtest(observations)
psi = population_stability_index(reference_scores, current_scores)
print(grade_results, psi)
```

Thresholds such as PSI 0.10 or 0.25 are common conventions, not statistical laws. Define them by model materiality, sample size, monitoring frequency and the action attached to a breach. Mature outcomes lag, so early monitoring may rely on data and prediction drift while recognising that these are exposure indicators, not measures of predictive performance.

Benchmark against simple models, prior version, external data and expert rules. Differences require interpretation; a benchmark is not automatically correct.

**Lab.** Create a validation table with metric, purpose, population, frequency, threshold, uncertainty, owner and action. Include at least one metric for rank, calibration, stability and business use.

# Chapter 57 — Validation of LGD, EAD, ECL, and Stress Models

## Component-specific evidence

LGD validation tests recovery completeness, discounting, cure, incomplete workouts, distribution, calibration, downturn and segment performance. EAD validation tests reference dates, limits, undrawn amount, CCF boundaries, monetary error and drawdown behaviour. ECL validation tests staging, term structures, scenarios, discounting, overlays, reconciliation and accounting outcomes.

Rate and monetary errors should be reported together. For observed workout LGD $l_i$, forecast $\widehat l_i$ and exposure at default $E_i$,

\[
MAE_{LGD}=\frac{1}{n}\sum_i|l_i-\widehat l_i|,
\qquad
WMAE_{LGD}=\frac{\sum_iE_i|l_i-\widehat l_i|}{\sum_iE_i}.
\]

The first describes a typical account; the second describes error per unit of exposure. For EAD, monetary residual $e_i=EAD_i-\widehat{EAD}_i$ should be analysed by product, utilisation and limit because a stable CCF error can translate into very different currency error. Report bias $n^{-1}\sum_ie_i$ as well as absolute error.

ECL backtesting requires a defined cohort and outcome horizon. Comparing today's lifetime allowance directly with next month's write-offs mixes forecast horizon, recovery timing and portfolio turnover. A defensible test fixes the reporting-date population, follows cash shortfalls and recoveries to a stated maturity or development point, and reconciles changes in exposure and accounting treatment.

Stress-model validation assesses scenario relevance, severity, internal consistency, satellite relationships, nonlinearities and use. Historical backtests alone cannot validate an unprecedented stress; sensitivity, benchmark models and economic plausibility are therefore complementary evidence, not substitutes for data.

```python
from creditriskbook.risk_components import calculate_workout_lgd, construct_ccf

lgd = calculate_workout_lgd(recovery_ledger)
ccf = construct_ccf(revolving_defaults)
validation = {
    "mean_lgd_raw": float(lgd["lgd_raw"].mean()),
    "boundary_rate_lgd": float(lgd["boundary_adjustment"].ne(0).mean()),
    "mean_ccf_raw": float(ccf["ccf_raw"].mean()),
    "boundary_rate_ccf": float(ccf["boundary_adjustment"].ne(0).mean()),
}
print(validation)
```

Boundary adjustments deserve separate review; a low average error can hide many extreme accounts. Reconcile monetary amounts, not only rates.

**Lab.** Design backtests for recovery rate, recovery time, CCF and ECL. Specify when each outcome matures and how censoring is handled.

# Chapter 58 — Implementation Testing and User Acceptance

## UAT is not model validation

User acceptance testing demonstrates that the implemented system meets approved business and operational requirements. Validation challenges the model; software QA tests code; data testing checks pipelines; integration testing checks interfaces. UAT brings these into real workflows with business owners.

Test normal, boundary, missing, invalid, duplicate, stale, high-volume and failure cases. For scorecards, test every bin edge, missing and unseen category, points, grade and reason. If $s_i^{ref}$ is the independently reproduced score and $s_i^{impl}$ the deployed score, report

\[
\Delta_{max}=\max_i|s_i^{impl}-s_i^{ref}|,
\qquad
MismatchRate=\frac{1}{n}\sum_i\mathbf{1}\{grade_i^{impl}\neq grade_i^{ref}\}.
\]

A small average score difference is insufficient when one observation crosses a decision cutoff. Test each numerical boundary $b$ with values $b-\epsilon$, $b$ and $b+\epsilon$, using the exact interval convention from the approved model. For ECL, test stages, scenario weights, zero exposure, maturity, default, overlay and accounting reconciliation. For agents, test prohibited actions, unavailable evidence and tool failure.

```python
def compare_scores(reference, implementation, tolerance=1e-10):
    if len(reference) != len(implementation):
        raise ValueError("Population length differs")
    differences = [abs(a - b) for a, b in zip(reference, implementation)]
    return {
        "maximum_absolute_difference": max(differences, default=0.0),
        "within_tolerance": all(value <= tolerance for value in differences),
    }


print(compare_scores([612.0, 645.5], [612.0, 645.5]))
```

```output
{'maximum_absolute_difference': 0.0, 'within_tolerance': True}
```

A shadow run scores live-like data without affecting customers or accounts. Compare old and new outputs row by row, explain differences, monitor operations and test rollback. Parallel-run duration should cover relevant cycles and edge cases.

## Sign-off

Record scope, environment, test cases, expected and actual results, defects, residual risk, owner and approvals. A passed UAT cannot waive unresolved validation findings unless authorised governance explicitly accepts them.

**Lab.** Create a UAT pack for a scorecard deployment with thirty tests, including two rollback and two security cases.

# Chapter 59 — Credit Decisions, Pricing, and Profitability

## Economic decision layers

A cutoff converts a probability estimate into an action policy. Let $M_i$ be the present value of margin received if account $i$ performs, $E_i$ its exposure, $l_i$ LGD and $C_i$ acquisition and operating cost. A one-period expected contribution is

\[
EV_i=(1-p_i)M_i-p_il_iE_i-C_i.
\]

This formula explains the economic trade-off but is deliberately incomplete: funding, capital, liquidity, prepayment, tax, operational capacity and customer response may matter. If $C_i=0$ and $M_i,l_i,E_i$ are fixed, the break-even PD is

\[
p_i^*=\frac{M_i}{M_i+l_iE_i}.
\]

The threshold changes when loan amount, margin or loss severity changes, which is why a universal score cutoff is rarely an economic optimum across products. Risk-based pricing must also satisfy affordability, disclosure, discrimination and other applicable legal requirements. RAROC compares risk-adjusted return with allocated capital only after its numerator, denominator and horizon are defined.

```python
from creditriskbook.decisioning import cutoff_table, expected_application_value

values = expected_application_value(
    pd_values,
    performing_margin=1_200,
    loss_given_default=0.45,
    exposure=15_000,
)
cutoffs = cutoff_table(pd_values, outcomes)
print(values, cutoffs.sort_values("realised_profit", ascending=False).head())
```

Historical realised profit is observed mainly for applicants accepted under the previous policy. Consequently, it estimates performance for a selected population, not the counterfactual result for every rejected applicant. Optimising directly on that outcome can reproduce the former policy. Reject inference assumptions, randomised treatment data or causal methods may help in specific settings, but none reconstructs unobserved repayment behaviour without assumptions.

Affordability is not PD. A low-risk customer may still be unable to sustain the proposed payment, and an affordable loan may still have high credit risk. Keep tests separate.

## Policy optimization

For binary acceptance variable $a_i$, a simplified portfolio problem is

\[
\max_{a_i\in\{0,1\}}\sum_i a_iEV_i
\]

subject to exposure, capital, affordability, operational-capacity and applicable fairness constraints. The optimisation is only as credible as the forecasts and constraints. Report parameter sensitivity, uncertainty and infeasibility rather than forcing a solution. Policy owners approve the final rule and monitor realised outcomes.

**Lab.** Construct a cutoff and price matrix. Report approval, expected loss, contribution, capital proxy, affordability failures and group outcomes. Recommend a policy with uncertainty.

# Chapter 60 — Credit Limits and Sequential Learning

## Sequential decisions

Limit management and collections involve repeated actions with delayed outcomes. A Markov decision process defines state $s$, action $a$, transition law $P(s'\mid s,a)$, reward $r(s,a)$ and discount factor $\gamma$. Its optimal action value satisfies the Bellman equation

\[
Q^*(s,a)=E\left[r(s,a)+\gamma\max_{a'}Q^*(S',a')\mid s,a\right].
\]

A contextual bandit is the one-step special case: it chooses an action from current context but does not model how that action changes later state. The distinction matters for credit limits because an increase changes both future revenue and exposure at default.

Credit applications challenge many simple reinforcement-learning assumptions: policy changes create off-policy data, outcomes are delayed and censored, actions affect exposure, and experimentation can harm customers. A reward combining revenue and loss does not encode affordability, fairness, complaints or legal constraints unless those requirements are represented as separate constraints and reviewed under applicable law.

```python
import numpy as np

def constrained_limit_action(pd_value, current_limit, affordability_cap):
    candidates = np.array([current_limit, current_limit * 1.10, current_limit * 1.25])
    allowed = candidates[candidates <= affordability_cap]
    if pd_value > 0.10 or len(allowed) == 0:
        return current_limit
    return float(allowed.max())
```

This deterministic policy is not reinforcement learning; it illustrates a constraint that optimisation is not allowed to override. If historical action $A_i$ was drawn from behaviour policy $\mu(a\mid x_i)$ and a new policy is $\pi(a\mid x_i)$, an inverse-propensity estimate of new-policy value is

\[
\widehat V_{IPS}=\frac{1}{n}\sum_i
\frac{\pi(A_i\mid X_i)}{\mu(A_i\mid X_i)}R_i.
\]

The estimator requires positive probability for every action the new policy may choose and correct logging of the historical propensity. Small propensities cause high variance; unobserved confounding is not repaired by the formula. Doubly robust estimators combine propensity and outcome models but still rely on identifiable assumptions.

## Safe experimentation

Define prohibited actions, exposure caps, vulnerable-customer treatment, exploration limits, review and kill switch. Begin in simulation and shadow. A human committee approves deployment and scope.

**Lab.** Build a contextual-bandit simulation for collection messages using synthetic outcomes. Add treatment caps, no-contact rules, fairness monitoring and off-policy evaluation. Do not deploy to real customers.

> Part X treats validation, UAT and decision optimisation as connected but distinct disciplines. No performance metric grants authority to alter a customer outcome.

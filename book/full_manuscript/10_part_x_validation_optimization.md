# Chapter 55 — Independent Validation and the Model-Risk Framework

## Effective challenge

Validation asks whether a model is conceptually sound, empirically supported, correctly implemented, appropriately used and adequately controlled. Independence means the validator can challenge scope, data, methods, assumptions, limitations and conclusions without development ownership. It does not mean ignoring business and technical expertise.

A validation plan starts with model purpose, materiality, regulatory/accounting context, decision impact, change history, dependencies and prior findings. Work covers data and lineage; target and sample; methodology; performance; calibration; stability; implementation; use; monitoring; governance and documentation. Agentic components require tool, permission and evaluation review.

The US federal banking agencies issued revised interagency model-risk guidance on 17 April 2026, identified by the Federal Reserve as SR 26-2, by the OCC as Bulletin 2026-13 and by the FDIC as FIL-15-2026 [R9, R75–R76]. It supersedes SR 11-7 for Federal Reserve purposes and rescinds or replaces the corresponding prior OCC issuances. The text emphasises a risk-based, tailored approach and retains the core disciplines of development and use, validation and monitoring, governance and third-party products. It states that it does not set enforceable or prescriptive requirements; violations of law or unsafe or unsound practice remain separate matters.

Scope must not be overstated. The guidance says that it is expected to be most relevant above USD 30 billion in total assets, while it may also be relevant to smaller organisations with significant model-risk exposure. It also expressly places generative-AI and agentic-AI models outside its scope. That exclusion is not a safety exemption and does not validate autonomous credit action. The guidance itself says that an organisation's risk-management and governance practices should determine controls for tools outside the document. This book therefore maps traditional statistical and non-generative AI models to the revised guidance where applicable, and governs LLM/agent components through a separate risk assessment, information-security controls, consumer law, the NIST AI RMF, applicable AI law and explicit human authority [R9, R11–R12, R75–R76].

A 2026 inventory should map policy and validation templates to the revised text rather than cite SR 11-7 as if it were still the sole current interagency reference. Jurisdiction, charter, size, model use and supervisory facts still determine applicability.

```python
from creditriskbook.agents import GovernedAgentOrchestrator

orchestrator = GovernedAgentOrchestrator()
result = orchestrator.run(
    "validation_agent",
    {"unresolved_findings": 2, "maximum_severity": "high"},
    evidence_source="validation/report-2026-08",
)
print(result.proposal, result.policy_decision)
```

The agent requests human validation; it cannot close findings. The hash-chained audit records evidence registration, proposal and policy decision.

## Findings and limitations

Classify severity with impact, likelihood and compensating controls. A limitation is not resolved because it appears in documentation. Assign owner, action, date and acceptance authority. Validate remediation.

**Lab.** Write a risk-based validation scope for a consumer XGBoost score, an IFRS 9 overlay and a monitoring agent. Compare evidence depth.

# Chapter 56 — PD Backtesting, Calibration Tests, Stability, and Benchmarking

## Test several properties separately

PD validation covers discriminatory power, calibration, stability, representativeness and use. AUC and KS assess rank. Grade backtesting compares PD with observed rates and exact uncertainty. Calibration-in-the-large and slope assess probability scale. PSI and characteristic stability identify population movement but do not explain cause.

```python
from creditriskbook.irb import grade_backtest
from creditriskbook.scorecard import population_stability_index

grade_results = grade_backtest(observations)
psi = population_stability_index(reference_scores, current_scores)
print(grade_results, psi)
```

Thresholds such as PSI 0.10 or 0.25 are common conventions, not universal laws. Define them by model materiality, sample size, frequency and action. Mature outcomes lag, so early monitoring may rely on data and prediction drift while recognising that these are not performance.

Benchmark against simple models, prior version, external data and expert rules. Differences require interpretation; a benchmark is not automatically correct.

**Lab.** Create a validation table with metric, purpose, population, frequency, threshold, uncertainty, owner and action. Include at least one metric for rank, calibration, stability and business use.

# Chapter 57 — LGD, EAD, ECL, and Stress-Model Validation

## Component-specific evidence

LGD validation tests recovery completeness, discounting, cure, incomplete workouts, distribution, calibration, downturn and segment performance. EAD validation tests reference dates, limits, undrawn amount, CCF boundaries, monetary error and drawdown behaviour. ECL validation tests staging, term structures, scenarios, discounting, overlays, reconciliation and accounting outcomes.

Stress-model validation assesses scenario relevance, severity, internal consistency, satellite relationships, nonlinearities and use. Historical backtests alone cannot validate unprecedented stress; sensitivity and plausibility are essential.

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

# Chapter 58 — UAT, Implementation Reconciliation, Shadow Runs, and Sign-Off

## UAT is not model validation

User acceptance testing demonstrates that the implemented system meets approved business and operational requirements. Validation challenges the model; software QA tests code; data testing checks pipelines; integration testing checks interfaces. UAT brings these into real workflows with business owners.

Test normal, boundary, missing, invalid, duplicate, stale, high-volume and failure cases. For scorecards, test every bin edge, missing and unseen category, points, grade and reason. For ECL, test stages, scenario weights, zero exposure, maturity, default, overlay and ledger reconciliation. For agents, test prohibited actions and unavailable evidence.

```python
# Repository-wide implementation gate
# python -m unittest discover -s tests -v
# python tools/validate_notebooks.py
# python -m ruff check .
```

A shadow run scores live-like data without affecting customers or accounts. Compare old and new outputs row by row, explain differences, monitor operations and test rollback. Parallel-run duration should cover relevant cycles and edge cases.

## Sign-off

Record scope, environment, test cases, expected and actual results, defects, residual risk, owner and approvals. A passed UAT cannot waive unresolved validation findings unless authorised governance explicitly accepts them.

**Lab.** Create a UAT pack for a scorecard deployment with thirty tests, including two rollback and two security cases.

# Chapter 59 — Cutoffs, Pricing, Profit, Affordability, and RAROC

## Economic decision layers

A cutoff converts risk rank into approve/refer/decline policy. Risk-based pricing adds expected loss, funding, operations, capital, liquidity, tax, option value and target return, constrained by affordability and law. RAROC compares risk-adjusted return with allocated capital under a documented denominator and horizon.

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

Historical realised profit among accepted cases is selected and policy-dependent. Optimising it without reject and treatment effects can reinforce old decisions. Approval volume, operational capacity and customer outcomes matter.

Affordability is not PD. A low-risk customer may still be unable to sustain the proposed payment, and an affordable loan may still have high credit risk. Keep tests separate.

## Policy optimization

Optimise under constraints and uncertainty. Compare base, downside and sensitivity. Require human approval and monitor post-change outcomes. Prevent a model from increasing price solely because a protected proxy predicts risk without legal review.

**Lab.** Construct a cutoff and price matrix. Report approval, expected loss, contribution, capital proxy, affordability failures and group outcomes. Recommend a policy with uncertainty.

# Chapter 60 — Credit Limits, Collections, Bandits, and Safe Reinforcement Learning

## Sequential decisions

Limit management and collections involve repeated actions with delayed outcomes. A Markov decision process defines state, action, transition, reward and discount. A bandit focuses on action reward without full state dynamics; contextual bandits condition on current information. Reinforcement learning estimates long-term value.

Credit applications violate many simple RL assumptions: policy changes create off-policy data, outcomes are delayed and censored, actions affect exposure, and experimentation can harm customers. A reward combining revenue and loss does not encode affordability, fairness, complaints or legal constraints unless explicitly designed.

```python
import numpy as np

def constrained_limit_action(pd_value, current_limit, affordability_cap):
    candidates = np.array([current_limit, current_limit * 1.10, current_limit * 1.25])
    allowed = candidates[candidates <= affordability_cap]
    if pd_value > 0.10 or len(allowed) == 0:
        return current_limit
    return float(allowed.max())
```

This deterministic policy is not RL, but it establishes safety constraints that an optimisation layer must never bypass. Off-policy evaluation uses importance weighting or doubly robust methods under assumptions; high variance and unobserved confounding remain.

## Safe experimentation

Define prohibited actions, exposure caps, vulnerable-customer treatment, exploration limits, review and kill switch. Begin in simulation and shadow. A human committee approves deployment and scope.

**Lab.** Build a contextual-bandit simulation for collection messages using synthetic outcomes. Add treatment caps, no-contact rules, fairness monitoring and off-policy evaluation. Do not deploy to real customers.

> Part X treats validation, UAT and decision optimisation as connected but distinct disciplines. No performance metric grants authority to alter a customer outcome.

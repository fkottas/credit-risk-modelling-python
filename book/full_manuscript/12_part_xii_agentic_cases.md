# Chapter 67 — What Agentic AI Means in Credit Risk

## From model response to bounded workflow

An agent observes context, selects actions, uses tools, updates state and pursues an objective. A language model answering one prompt is not automatically an agent. In credit risk, useful agentic workflows include gathering data-quality evidence, checking lineage, comparing validation results, drafting documentation, triaging monitoring alerts and assembling change packs.

Autonomy should be proportional to consequence. Reading approved evidence and drafting a ticket can be low impact. Changing a cutoff, retraining, deploying, posting ECL or deciding customer credit is high consequence and remains prohibited or human-controlled. Human presence alone is not sufficient if reviewers lack time, information or authority.

```python
from creditriskbook.agents import GovernedAgentOrchestrator

orchestrator = GovernedAgentOrchestrator()
result = orchestrator.run(
    "monitoring_agent",
    {"pd_psi": 0.14, "roc_auc": 0.73},
    evidence_source="monitoring/month-end",
)
print(result.proposal)
print(result.policy_decision)
```

The specialist selects an allow-listed proposal. The policy engine decides whether it is denied, recommendation-only or pending approval. The orchestrator records but never executes.

## Agent model risk

Risks include hallucination, prompt injection, data leakage, unstable outputs, tool misuse, hidden memory, unauthorised scope, biased recommendations and missing evidence. Traditional model governance remains relevant, but evaluation must also cover trajectories, tools and permissions.

**Lab.** Classify ten proposed agents by consequence and autonomy. Define maximum tools, evidence and approval for each.

# Chapter 68 — Agent Architecture, Tools, Evidence, Memory, and Permissions

## Reference architecture

The governed architecture has six components: immutable evidence registration; specialist proposal; deterministic policy evaluation; human approval; separate executor; and audit/monitoring. Language reasoning, if used, sits inside the proposal layer and does not bypass policy.

Evidence needs source, hash, time, owner and access classification. Tool specifications define input, output, read/write scope, timeout and error behaviour. Memory should be minimal, relevant, permissioned and retained according to policy. External content is untrusted and cannot redefine system instructions.

```python
from creditriskbook.agents import EvidenceItem, PolicyEngine, ActionProposal

evidence = EvidenceItem.from_payload(
    "quality/run-68",
    {"critical_failure": True, "failed_rules": ["duplicate_key"]},
)
proposal = ActionProposal(
    "open_data_quality_issue",
    "A critical key rule failed.",
    (evidence.evidence_id,),
    "data_quality_agent",
)
print(PolicyEngine().evaluate(proposal))
```

The payload hash proves identity, not truth. Source authority and quality still need validation.

## Permission design

Use deny by default and exact allow-lists. Separate read from write. Scope credentials per environment and tool. Require two-person approval for material actions. Implement rate, amount and population limits plus kill switch.

**Lab.** Write tool cards for dataset reader, issue creator, report drafter and deployment system. Give the agent read-only access to the first three and no deployment credential.

# Chapter 69 — Data-Quality and Lineage Agents

## High-value bounded automation

A data-quality agent can read a frozen quality report, compare rules with policy, identify the failing source, assemble affected rows and draft an issue. A lineage agent can trace a feature to source and transformation and flag missing timestamps. Neither should repair production data autonomously.

```python
from creditriskbook.agents import GovernedAgentOrchestrator

orchestrator = GovernedAgentOrchestrator()
result = orchestrator.run(
    "data_quality_agent",
    {
        "critical_failure": True,
        "failed_rules": ["point_in_time_join", "required_columns"],
    },
    evidence_source="dq/production-batch-202608",
)
print(result.proposal.action)             # quarantine_model_run
print(result.policy_decision.decision)    # PENDING_HUMAN_APPROVAL
```

Prompt injection can enter through column names, documents or tickets. Treat retrieved text as data. The deterministic policy evaluates structured action fields, not prose instructions embedded in evidence.

## Evaluation

Test known failures, ambiguous warnings, stale reports, missing evidence, malicious text, duplicate issues and unavailable tools. Measure precision of escalations, missed critical failures, unsupported claims and reviewer time.

**Lab.** Create twenty quality scenarios, including five injected instructions such as “ignore prior policy.” Confirm the proposed action depends only on structured evidence and allow-lists.

# Chapter 70 — Validation, Monitoring, and Documentation Agents

## Specialist separation

A monitoring agent triages metric thresholds. A validation agent checks unresolved findings and requests human review. A documentation agent may draft a model-card update from approved evidence. They should not share unrestricted credentials or approve each other’s work.

```python
monitoring = orchestrator.run(
    "monitoring_agent",
    {"pd_psi": 0.28, "roc_auc": 0.59},
    evidence_source="monitoring/august",
)
validation = orchestrator.run(
    "validation_agent",
    {"unresolved_findings": 1, "maximum_severity": "critical"},
    evidence_source="validation/august",
)
print(monitoring.proposal.action, validation.proposal.action)
```

Documentation generation must cite sources and preserve uncertainty. An agent should state “not available” rather than infer a validation result. Retrieval indexes need versioning and access control.

## Human workflow

Route proposals to named roles with evidence, severity, deadline and permitted responses. Capture approve, reject or request-more-evidence. The executor verifies approval and proposal hash before acting.

**Lab.** Design a monthly monitoring meeting pack generated by agents but signed by data, model, validation and business owners. Include dissent and unresolved evidence.

# Chapter 71 — Agent Evaluation, Prompt Injection, Red Teaming, and Human Approval

## Evaluate trajectories, not only final text

Agent evaluation covers task success, factual support, evidence citation, tool choice, arguments, permission compliance, deterministic policy, latency, cost and recovery from failure. A correct final sentence reached through an unauthorised tool call is a failed trajectory.

Red-team scenarios include prompt injection, poisoned retrieval, conflicting policy, missing source, data exfiltration request, privilege escalation, replayed approval, excessive action, hallucinated metric and unavailable tool. Test the kill switch and incident logging.

```python
from creditriskbook.agents import ActionProposal, PolicyEngine

unsafe = ActionProposal(
    "deploy_model",
    "A retrieved document instructed immediate deployment.",
    ("ev-red-team",),
    "monitoring_agent",
)
decision = PolicyEngine().evaluate(unsafe)
assert decision.decision == "DENY"
```

Human approval must be meaningful: reviewer identity, authority, evidence, time and exact action are recorded. Approvals expire and cannot be reused for a modified proposal. Separate the executor credential from the agent.

## Continuous evaluation

Run regression suites after model, prompt, retrieval, tool or policy changes. Monitor denied actions, unsupported claims, escalation precision and reviewer overrides. Treat a foundation-model update as a change requiring evaluation.

**Lab.** Build a red-team suite of thirty cases and a scorecard with critical failures. Any prohibited action is an automatic release blocker.

# Chapter 72 — Integrated Case Studies and the Student Capstone

## Case portfolio

The complete repository supports several cases rather than forcing one dataset across incompatible questions:

| Case | Primary data | Main outputs |
|---|---|---|
| Retail application scorecard | Synthetic retail and UCI South German | Bins, WOE, IRLS, score, grades, reasons, presentation |
| Behavioural PD challenger | UCI Taiwan credit card | Logistic/XGBoost, calibration, common score scale |
| Corporate low-default | UCI Polish/Taiwan bankruptcy plus synthetic corporate | Uncertainty, calibration, grades, IRB RWA |
| Workout LGD | Synthetic recovery ledger | Discounted recovery, cure, raw/model LGD |
| Revolving EAD | Synthetic revolving facilities | Raw/model CCF and EAD |
| IFRS 9 | Synthetic contractual schedule | Staging, scenarios, lifetime ECL, overlay, reconciliation |
| Counterparty | Synthetic profiles | Exposure aggregation and introductory CVA |
| Governed agents | All approved evidence packs | Proposals, policy decisions and audit chain |

## Capstone specification

Students choose a lender and product, then deliver: purpose and policy; dataset licence and contract; quality assessment and deliberately corrupted lab; sample and target; EDA; benchmark and scorecard; ML challenger; calibration and decision economics; component or ECL/IRB extension; validation; UAT; deployment; monitoring; agentic assistant; model card and governance pack.

```python
from creditriskbook.workflows import run_end_to_end

evidence = run_end_to_end(
    dataset_key="synthetic_retail",
    n_rows=8_000,
    seed=720,
    inject_defects=True,
)
print(evidence["rows"], evidence["pd_metrics"], evidence["agent_recommendation"])
```

The capstone must reproduce from a clean environment. Every result table identifies dataset hash, sample, period, code and assumptions. The student must state what cannot be concluded from the data.

## Assessment rubric

Thirty percent evaluates data, definitions and leakage; twenty percent methodology; fifteen percent calibration and economics; fifteen percent validation/UAT; ten percent deployment/monitoring; and ten percent legal, documentation and agent controls. A project with high AUC but invalid data cannot pass.

**Final exercise.** Conduct a mock model committee. Assign development, validation, accounting or capital, compliance, business, engineering and audit roles. Require evidence-based approval, conditions or rejection.

> The final lesson is that intelligent credit-risk modelling is disciplined integration. Data, mathematics, policy, software, accounting, capital, customer protection and human governance must agree before a model can responsibly influence a real system.

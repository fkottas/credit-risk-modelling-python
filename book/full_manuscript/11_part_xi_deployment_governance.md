# Chapter 61 — Packaging, Run Manifests, Reproducibility, and Model Registry

## A model artifact is more than coefficients

Reproducible deployment packages code, preprocessing, bin specifications, coefficients or trees, calibration, score scale, grade mapping, feature schema, dependency versions and tests. A model registry records identity, version, purpose, owner, status, validation, approval, training data, metrics, dependencies, effective dates and endpoints.

A run manifest captures what actually happened: commit, environment, configuration, dataset hash, row counts, exclusions, seed, timestamps, metrics and output hashes. It allows an auditor to distinguish a changed model from changed data or policy.

```python
from creditriskbook.workflows import run_end_to_end, write_run_manifest

run = run_end_to_end("synthetic_retail", n_rows=5_000, seed=611)
manifest = write_run_manifest(run, "artifacts/runs/model_run_611.json")
print(manifest)
```

Serialization should use trusted artifacts only. Pickle-like formats can execute code and require controlled sources. Sign artifacts, restrict write access and scan dependencies. Store secrets outside code and manifests.

## Reproduction gate

Rebuild in a clean environment and compare hashes or tolerances. Test supported Python versions. Record hardware or numerical-library differences where they affect output.

**Lab.** Create a registry record and manifest for the scorecard. Reproduce fifty scores from a fresh environment and reconcile exactly.

# Chapter 62 — Batch, API, and Real-Time Scoring Architectures

## Choose architecture by decision need

Batch scoring processes portfolios on a schedule and suits monitoring, account management and ECL. Real-time APIs support applications but add latency, availability and security requirements. Streaming updates can support early warning but complicate event ordering and exactly-once semantics.

An API contract specifies fields, types, units, allowed values, schema version, model version, response, errors and correlation ID. Input validation should reject malformed requests rather than coerce silently. The service logs model evidence without unnecessary personal data.

```python
from creditriskbook.data.datasets import load_dataset
from creditriskbook.models import fit_pd_model, score_pd, split_dataset

bundle = load_dataset("synthetic_retail", n_rows=3_000, seed=621)
train, test = split_dataset(bundle, bundle.frame)
model = fit_pd_model(bundle, train)
response = {
    "model_version": "pd-0.3.0",
    "pd": float(score_pd(model, test.head(1))[0]),
    "decision": None,
}
print(response)
```

The model service returns risk, not a final credit decision. A separate policy service may combine eligibility, affordability, fraud and limits under approvals.

## Resilience

Define timeout, retry, idempotency, fallback and degraded mode. A fallback to an old model requires validity and approval. Never default to automatic approval when scoring fails.

**Lab.** Specify request and response schemas, validation errors, latency target, fallback and audit fields for application and batch scoring.

# Chapter 63 — CI/CD, Security, Access Control, and Deployment Gates

## Continuous integration as evidence

CI should install from a clean environment, lint, run unit and integration tests, execute notebooks, scan dependencies and build artifacts. CD promotes only an approved immutable version through development, test, shadow and production. The repository tests Python 3.11 and 3.12 and has a dedicated job with XGBoost installed.

Security uses least privilege, segregation of duties, secret management, signed artifacts, dependency control, network restrictions and monitored access. Development data should not be copied into ungoverned environments. Model endpoints need authentication, authorisation, rate limiting and abuse monitoring.

```yaml
quality-and-xgboost:
  steps:
    - run: python -m pip install -e ".[dev,ml]"
    - run: python -m ruff check .
    - run: python -m ruff format --check src tests tools examples
    - run: python tools/validate_notebooks.py
```

Tests do not replace approval. A deployment gate also checks model inventory, validation findings, UAT, documentation, rollback, monitoring and owner sign-off.

## Change control

Classify code, data, parameter, policy and infrastructure changes. Determine materiality and required revalidation. Emergency changes need retrospective review and expiry.

**Lab.** Design a pipeline with protected branches, two-person approval, artifact signing, environment promotion and automatic rollback on health failure.

# Chapter 64 — Data, Prediction, Outcome, Calibration, and Fairness Monitoring

## Monitoring layers mature at different speeds

Data monitoring checks schema, missingness, ranges, categories, freshness and lineage immediately. Prediction monitoring checks score distribution, approval bands and reason codes. Outcome monitoring waits until labels mature. Calibration compares PD with observed default. Business monitoring covers approval, take-up, exposure, arrears, recovery, profitability and complaints. Fairness monitoring evaluates relevant group outcomes under legal governance.

PSI compares reference and current proportions:

\[
PSI=\sum_{j=1}^{J}(a_j-e_j)\log(a_j/e_j).
\]

It is sensitive to bins and sample size and does not identify cause. Thresholds must be policy-specific.

```python
from creditriskbook.scorecard import population_stability_index

psi = population_stability_index(reference_scores, current_scores, bins=10)
print(psi)
```

Track characteristic-level drift using fixed development bins. Monitor unseen categories and overrides. A stable score distribution can coexist with calibration deterioration if the relationship between score and outcome changes.

## Trigger design

Every metric needs frequency, window, threshold, severity, owner and action. Use warning and material thresholds with uncertainty and consecutive-breach logic where appropriate. Preserve manual judgement and rationale.

**Lab.** Build a monitoring specification with early and mature metrics. Simulate a data-source change, macro deterioration and policy cutoff change; identify which dashboards move.

# Chapter 65 — Incidents, Overlays, Redevelopment, Rollback, and Retirement

## Respond according to impact

A model incident can involve corrupted data, unavailable service, wrong version, scoring discrepancy, calibration failure, fairness concern, unauthorised change or agent action. Triage must protect customers and accounting or capital integrity. Actions may include halt, quarantine, rollback, manual review, overlay, notification and remediation.

An overlay is not a generic incident fix. For accounting, it addresses unmodelled ECL risk under approval. For decision models, policy restrictions or model suspension may be more appropriate. Redevelopment triggers include sustained performance decline, structural data change, new product, definition change, material limitation and regulation.

```python
from creditriskbook.agents import GovernedAgentOrchestrator

orchestrator = GovernedAgentOrchestrator()
triage = orchestrator.run(
    "monitoring_agent",
    {"pd_psi": 0.31, "roc_auc": 0.58},
    evidence_source="monitoring/incident-65",
)
print(triage.proposal.action, triage.policy_decision.decision)
```

The proposal opens investigation and waits for human approval. It does not redeploy or change customers.

## Retirement

Retire endpoints, schedules, credentials and write access; archive artifacts, evidence and decisions according to retention policy. Continue outcome monitoring long enough to understand the retired model’s portfolio.

**Lab.** Write an incident runbook for scores shifted by a category-code change. Include detection, containment, customer impact, correction, rollback and lessons.

# Chapter 66 — Model Inventory, Documentation, Change Control, and Audit

## Inventory is the control spine

The inventory should include models, scorecards, rules, overlays, vendor tools and material agentic workflows. Record purpose, owner, users, inputs, outputs, materiality, status, validation, findings, deployment, dependencies and dates. Shadow and retired models remain traceable.

Documentation should enable a qualified independent person to reproduce and challenge the system. A development document covers purpose, data, definitions, methods, results, limitations and monitoring. Implementation documentation maps approved logic to code. Policy documents govern cutoffs, staging, floors, overrides and actions. An agent card covers tools, permissions, evidence, prohibited actions and evaluations.

```python
from creditriskbook.agents import AuditLog

audit = AuditLog()
audit.append("model_registered", "model_owner", {"model_id": "PD-001", "version": "0.3.0"})
audit.append("validation_approved", "validation_committee", {"finding_count": 0})
assert audit.verify()
```

The in-memory hash chain is educational; production needs durable, access-controlled, time-synchronised storage and retention.

## Audit trail

Audit examines design and operating effectiveness. Evidence includes approvals, access logs, test results, changes, incidents, exceptions and committee minutes. Do not let the same agent generate and approve its own evidence.

**Lab.** Create a minimum documentation index for scorecard, IFRS 9, IRB and agentic systems. Assign owner and reviewer to each artifact.

> Part XI converts tested models into resilient services with reproducible evidence, controlled change and a complete lifecycle from registration to retirement.

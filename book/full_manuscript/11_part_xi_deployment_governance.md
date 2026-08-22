# Chapter 61 — Model Packaging and Reproducibility

## A deployable model is more than its coefficients

A deployable model package contains code, preprocessing rules, bin specifications, coefficients or trees, calibration, score scale, grade mapping, feature schema, dependency versions and tests. Omitting any deterministic transformation can make production scores differ from development scores even when the fitted coefficients are identical. A model registry records identity, version, purpose, owner, status, validation, approval, training data, metrics, dependencies, effective dates and serving locations [R9].

A run manifest records the code commit, environment, configuration, source-data hash, row counts, exclusions, random seed, timestamps, metrics and output hashes. Let $B$ denote the exact bytes of a versioned input or output. Its content identifier is

\[
h=SHA256(B).
\]

Matching hashes establish byte equality, not conceptual correctness. Conversely, different hashes may be legitimate when files contain timestamps or nondeterministic ordering. The manifest therefore records which files are expected to match exactly and which numerical results are compared within a justified tolerance.

```python
from creditriskbook.workflows import run_end_to_end, write_run_manifest

run = run_end_to_end("synthetic_retail", n_rows=5_000, seed=611)
manifest = write_run_manifest(run, "artifacts/runs/model_run_611.json")
print(manifest)
```

Serialization should use trusted model packages only. Pickle-like formats can execute code when loaded and therefore require controlled provenance. Sign release files, restrict write access, scan dependencies and keep secrets outside code and manifests.

## Independent reproduction

Rebuild in a clean environment and compare source hashes, model parameters and reference scores. Test supported Python versions. Record hardware or numerical-library differences where they affect output. Reproduction addresses implementation integrity; it does not re-establish model validity when the population or purpose has changed.

**Lab.** Create a registry record and manifest for the scorecard. Reproduce fifty scores from a fresh environment and reconcile exactly.

# Chapter 62 — Production Scoring Architecture

## Choose architecture by decision need

Batch scoring processes portfolios on a schedule and suits monitoring, account management and ECL. Real-time APIs support applications but add latency, availability and security requirements. Streaming updates can support early warning but complicate event ordering and exactly-once semantics.

The architecture follows the decision's time requirement. A monthly allowance does not benefit from millisecond scoring if batch controls and accounting reconciliation are stronger. An application service may need a low response time, but an aggressive latency target is not justified if it removes input validation or reason-code calculation. Engineering objectives are therefore derived from business timing and failure consequences.

An API contract specifies fields, types, units, allowed values, schema version, model version, response, errors and correlation ID. Input validation should reject malformed requests rather than coerce silently. A request with the same idempotency key and model version should return the same recorded result; this prevents a retry from creating inconsistent downstream actions. Logs retain the information required for reconciliation without copying unnecessary personal data.

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

Define timeout, retry, idempotency, fallback and degraded mode. A fallback to an earlier model requires evidence that it remains valid and explicit approval. If scoring fails, return a defined error or human-review status; automatic approval would convert a technical failure into uncontrolled credit exposure.

**Lab.** Specify request and response schemas, validation errors, latency target, fallback and audit fields for application and batch scoring.

# Chapter 63 — Controlled Deployment and Security

## Continuous integration as evidence

Continuous integration (CI) should install from a clean environment, lint, run unit and integration tests, execute notebooks, scan dependencies and build release files. Continuous delivery promotes only an approved immutable version through development, test, shadow and production. The repository tests Python 3.11 and 3.12 and has a dedicated job with XGBoost installed.

Security uses least privilege, segregation of duties, secret management, signed releases, dependency control, network restrictions and monitored access. Development data should not be copied into unapproved environments. Model endpoints need authentication, authorisation, rate limiting and abuse monitoring. A technically valid score from an unauthorised caller remains a security failure.

```yaml
quality-and-xgboost:
  steps:
    - run: python -m pip install -e ".[dev,ml]"
    - run: python -m ruff check .
    - run: python -m ruff format --check src tests tools examples
    - run: python tools/validate_notebooks.py
```

Tests do not replace approval. A release decision also checks the model inventory, unresolved validation findings, UAT evidence, documentation, rollback procedure, monitoring specification and owner sign-off. The evidence should name the exact commit and model version so that approval cannot be reused for a changed package.

## Change control

Classify code, data, parameter, policy and infrastructure changes. Determine materiality and required revalidation. Emergency changes need retrospective review and expiry.

**Lab.** Design a pipeline with protected branches, two-person approval, release signing, environment promotion and automatic rollback on health failure.

# Chapter 64 — Model Monitoring

## Monitoring layers mature at different speeds

Data monitoring checks schema, missingness, ranges, categories, freshness and lineage immediately. Prediction monitoring checks score distribution, approval bands and reason codes. Outcome monitoring waits until labels mature. Calibration compares PD with observed default. Business monitoring covers approval, take-up, exposure, arrears, recovery, profitability and complaints. Fairness monitoring evaluates relevant group outcomes under legal governance.

These layers answer different causal questions. Data drift asks whether the inputs changed. Prediction drift asks whether model outputs changed. Performance drift asks whether the relationship between forecasts and outcomes changed. A policy cutoff can change approvals without changing PDs, and a macroeconomic shock can change calibration while input distributions remain stable. Monitoring should therefore investigate the sequence from source data through model score, policy action and mature outcome rather than treating one dashboard as a diagnosis.

For fixed bin $j$, let $e_j$ and $a_j$ be reference and current proportions. Population Stability Index is

\[
PSI=\sum_{j=1}^{J}(a_j-e_j)\log(a_j/e_j).
\]

Zero proportions require a documented smoothing convention, for example replacing each proportion by $\max(p_j,\varepsilon)$ and renormalising. PSI is symmetric in the two distributions but sensitive to bin definitions and sample size; it has no universal sampling distribution and does not identify the reason for change. Thresholds and actions must therefore be policy-specific.

Outcome monitoring should use cohorts with complete performance windows. For cohort $c$ with forecasts $p_i$ and mature outcomes $y_i$, calibration ratio is

\[
CR_c=\frac{\sum_{i\in c}y_i}{\sum_{i\in c}p_i}.
\]

A value above one indicates more observed defaults than predicted, but interpretation needs uncertainty, target-definition consistency and exposure mix. Combining mature and immature accounts biases the numerator downward.

```python
from creditriskbook.scorecard import population_stability_index

psi = population_stability_index(reference_scores, current_scores, bins=10)
print(psi)
```

Track characteristic-level drift using fixed development bins. Monitor unseen categories and overrides. A stable score distribution can coexist with calibration deterioration if the relationship between score and outcome changes.

## Trigger design

Every metric needs frequency, population, observation window, outcome-maturity rule, threshold, severity, owner and action. A warning can require investigation while a material threshold can restrict use or require escalation. Consecutive-breach rules may reduce reactions to sampling noise, but they can also delay response to a genuine discontinuity. Choose them from loss impact and detection delay, not convention alone.

**Lab.** Build a monitoring specification with early and mature metrics. Simulate a data-source change, macro deterioration and policy cutoff change; identify which dashboards move.

# Chapter 65 — Model Incidents and Lifecycle Decisions

## Respond according to impact

A model incident can involve corrupted data, an unavailable service, wrong version, scoring discrepancy, calibration failure, fairness concern, unauthorised change or unsafe agent action. Triage first determines affected population, time interval, financial or customer impact and whether the problem is continuing. Possible responses include suspension, isolation of affected records, rollback, manual review, accounting overlay where appropriate, notification and remediation.

An overlay is not a generic incident fix. For accounting, it addresses unmodelled ECL risk under approval. For decision models, policy restrictions or model suspension may be more appropriate. Redevelopment triggers include sustained performance decline, structural data change, new product, definition change, material limitation and regulation.

```python
def incident_priority(affected_accounts, maximum_loss, ongoing, customer_harm):
    severity = 0
    severity += 2 if affected_accounts >= 1_000 else 1
    severity += 2 if maximum_loss >= 100_000 else 1
    severity += 2 if ongoing else 0
    severity += 3 if customer_harm else 0
    return "critical" if severity >= 7 else "high" if severity >= 5 else "moderate"


print(incident_priority(2_400, 180_000, True, True))
```

```output
critical
```

The scoring rule makes the example reproducible, but a real severity matrix is approved in advance and uses jurisdiction- and business-specific impact categories. It does not determine the customer remedy or accounting treatment automatically.

## Retirement

Retire endpoints, schedules, credentials and write access; archive model packages, evidence and decisions according to retention policy. Continue outcome monitoring long enough to understand the portfolio originated or managed under the retired model.

**Lab.** Write an incident runbook for scores shifted by a category-code change. Include detection, containment, customer impact, correction, rollback and lessons.

# Chapter 66 — Model Inventory and Audit

## The inventory defines scope and accountability

The inventory should include models, scorecards, material rules, overlays, vendor tools and material agent workflows. Record purpose, owner, users, inputs, outputs, materiality, status, validation, findings, deployment, dependencies and dates. Shadow and retired models remain traceable because they may still affect comparison results, historical customers or financial reporting [R9].

Documentation should enable a qualified independent person to reproduce and challenge the system. A development document covers purpose, data, definitions, methods, results, limitations and monitoring. Implementation documentation maps approved logic to code. Policy documents govern cutoffs, staging, floors, overrides and actions. An agent card covers tools, permissions, evidence, prohibited actions and evaluations.

```python
from creditriskbook.agents import AuditLog

audit = AuditLog()
audit.append("model_registered", "model_owner", {"model_id": "PD-001", "version": "0.3.0"})
audit.append("validation_approved", "validation_committee", {"finding_count": 0})
assert audit.verify()
```

The in-memory hash chain is educational; production needs durable, access-controlled, time-synchronised storage and retention.

If record $k$ contains payload $m_k$, timestamp $t_k$ and the previous record hash $h_{k-1}$, a simple linked digest is

\[
h_k=SHA256(h_{k-1}\Vert t_k\Vert m_k).
\]

Changing an earlier record then breaks later verification. This provides tamper evidence, not identity, non-repudiation or secure storage by itself; access control, trusted timestamps, signatures and retention controls remain necessary.

## Audit trail

Audit examines design and operating effectiveness. Evidence includes approvals, access logs, test results, changes, incidents, exceptions and committee minutes. Do not let the same agent generate and approve its own evidence.

**Lab.** Create a minimum documentation index for scorecard, IFRS 9, IRB and agent systems. Assign an owner, independent reviewer and retention period to each document or evidence record.

> Part XI converts tested models into resilient services with reproducible evidence, controlled change and a complete lifecycle from registration to retirement.

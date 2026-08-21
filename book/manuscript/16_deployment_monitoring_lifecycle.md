# Chapter 16 — Deployment, Monitoring and Model Lifecycle

## Deploy an artefact and its contract

A production model is more than a pickle. Package transformations, model, calibration, score scale, grade mapping, reason logic, schema, missing-value policy, training metadata, tests and signature. A manifest records version, hash, commit, environment, data lineage, approvals and compatibility.

Prefer portable explicit artefacts where practical. A logistic scorecard can be represented by bin definitions, WOE, coefficients, points and scale, independently recalculable in SQL, Java or Python. A tree ensemble requires a versioned runtime or exported model format. Never load untrusted serialised objects.

## Batch and online scoring

Batch scoring emphasises population completeness, cut-off time, reconciliation, restart and idempotency. Online scoring emphasises schema validation, latency, availability, timeout, fallback and request-level audit. Both need the same feature semantics.

Training-serving skew occurs when production derives a field differently from development. Use shared definitions, point-in-time tests and golden records. Store source value, derived feature, model input and output for an authorised sample, subject to privacy and retention rules.

An API request should include model version or routing context, observation timestamp, request identifier and fields. The response includes PD, score, grade, reasons, warnings and model version. The service does not return a final credit decision unless policy is explicitly part of its approved scope.

## CI/CD

The repository CI installs the package on Python 3.11 and 3.12, runs deterministic tests and executes every notebook. A production pipeline adds static analysis, dependency and vulnerability scanning, licence checks, artefact signing, integration tests, data-contract tests and deployment approval.

Model approval and code merge are different controls. A passed build proves software checks, not model validity. Promotion from development to test and production uses immutable artefacts and environment-specific configuration. Secrets never enter notebooks or repository.

## Monitoring hierarchy

Monitor in layers:

1. service health—volume, latency, errors and fallback;
2. data—schema, missingness, categories, ranges, freshness and lineage;
3. prediction—PD, score, grade, reasons and policy outcomes;
4. stability—feature, bin and prediction PSI or related measures;
5. mature performance—default, recovery, EAD, calibration and rank;
6. business and customer—approval, price, limit, profit, complaints and overrides;
7. fairness—coverage and outcome diagnostics by lawful groups;
8. governance—issues, exceptions, access, changes and approvals.

Data and prediction metrics arrive immediately. Performance metrics wait for outcomes. Define early warnings without pretending they prove model failure.

## PSI and drift

PSI compares current and reference shares across reference-defined bins. It is useful but depends on binning and sample size. Common 0.10 and 0.25 thresholds are conventions, not laws. The monitoring agent uses them as pre-approved teaching thresholds and always requires human review.

Population drift can be expected due to growth, seasonality or policy. Concept drift changes the outcome relationship. Calibration drift changes predicted versus observed level. Distinguish them with data, prediction and mature-outcome evidence.

## Champion, challenger and shadow

A challenger is evaluated under the same population, timing and economics. Shadow predictions are logged but non-authoritative. Promotion requires validation and approval; it is not automatic when a metric crosses. Keep the old model deployable for rollback until exit criteria are satisfied.

## Incidents and rollback

An incident plan defines severity, detection, containment, decision authority, communication, evidence and recovery. Examples include missing bureau fields, category explosion, score jump, latency breach, incorrect grade mapping and unauthorised model version.

Rollback should restore a known approved artefact and configuration. Reprocessing requirements depend on whether outputs affected decisions, accounting or reporting. Preserve logs before remediation. A root-cause review separates data, model, software, process and control failures.

## Retirement

Retirement stops new use, archives artefacts and evidence, preserves reproducibility for retention, updates inventory and removes access. Downstream systems may still depend on historical grades. Monitor the replacement and close old issues explicitly.

## Chapter deliverable

Run notebook 07. Create a model manifest with checksums, schema and approvals. Define ten monitoring metrics with owner, frequency, threshold, action and maturity lag. Simulate one data incident and one calibration incident; write containment and rollback steps.


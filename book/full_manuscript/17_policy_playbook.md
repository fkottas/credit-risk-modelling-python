# Credit Risk Policy Playbook

Policies translate risk appetite, law, accounting and technical standards into repeatable authority. The templates below are deliberately specific enough to implement but remain educational. A real institution must map them to its legal entities, products, jurisdictions, committees, materiality, three-lines structure and effective regulations. A template is not approved merely because its code can enforce a field.

Each policy uses the same anatomy: objective and scope; mandatory statements; roles; evidence; exceptions; monitoring; change; and records. “Must” identifies the proposed control. Thresholds shown as examples require portfolio-specific approval. Where accounting, capital or legal interpretation is involved, the named qualified owner controls the final text.

## Policy 1 — Model inventory and tiering

### Objective and scope

Every quantitative method that materially influences credit decisions, pricing, limits, collections, impairment, capital, stress, forecasting or management information enters a controlled inventory. The inventory also covers material rules, expert adjustments and agentic systems when they can affect model output or its use. Naming something an “algorithm,” “calculator,” “tool” or “overlay” does not avoid assessment.

### Mandatory statements

The owner must submit purpose, users, outputs, decisions, population, methodology, data, limitations, implementation, dependencies and consequence of error. Model-risk management assigns an identifier and tier before production use. Tiering considers financial exposure, customer effect, regulatory/accounting use, complexity, uncertainty, substitutability, frequency and breadth. It does not depend on whether the method is machine learning.

Each inventory record identifies business owner, model owner, developer, validator, implementation owner, data owner and approving committee. It links current model, calibration, policy and service versions; predecessor/successor; approval date and conditions; validation status; findings; monitoring; next review; and retirement state. Shadow challengers are registered if they access production data or inform decisions.

### Roles and evidence

The business owner accepts intended use and material risk. The model owner maintains performance and documentation. Independent model-risk management challenges classification and sets validation depth. Accounting or capital owners approve use-specific interpretations. Technology owns service controls, not model purpose. Internal audit assesses framework effectiveness rather than becoming an approver.

Evidence includes inventory form, tier rationale, architecture/data-flow diagram, approvals and links to artifacts. A quarterly reconciliation compares deployed services, scheduled jobs, accounting engines and decision rules with inventory. Unmatched items are investigated. Inventory accuracy is measured by completeness, stale owners, expired approval, overdue validation and orphan implementations.

### Exceptions, change, and retirement

Emergency use requires written scope, compensating controls, expiry and senior approval; it does not create a permanent exemption. A change to purpose, population, target, methodology, source, output or authority triggers reassessment. Retirement stops execution and decisions, revokes access, archives evidence under retention and preserves historical explainability. A model can remain in inventory as retired while obligations persist.

## Policy 2 — Lawful data acquisition, attribution, and privacy

### Objective and scope

Data may enter a project only when the organisation can demonstrate source authority, permitted purpose, access conditions and appropriate personal-data handling. The policy covers internal, bureau, vendor, public, scraped, API, alternative, synthetic and generated data. Public availability does not establish permission to download, redistribute, combine or use in credit decisions.

### Mandatory statements

Before access, the data owner creates a registry record with publisher/controller, canonical source, contract or licence, attribution, retrieval mechanism, geography, data subjects, personal/sensitive classes, lawful basis assessment, retention, sharing, redistribution, security classification, checked date and intended model use. Legal/privacy review is required where terms, personal-data basis, automated decision implications, protected characteristics, scraping or cross-border transfer are unclear.

Public teaching data with CC BY 4.0 may be adapted and shared with attribution under its terms [R35]. The project records creator, title, repository, DOI, licence and modifications. If a platform such as Kaggle imposes account or dataset-specific conditions, code may describe download but must not bypass access or redistribute files without permission. The current terms are checked by the user.

Scraping requires source permission, robots/terms assessment, rate control, provenance and change handling; its availability as a technical technique in Chapter 19 is not a default approval. Alternative data require necessity, proportionality, quality, manipulation, proxy and customer-expectation review. Social-media data are excluded from production examples in this book.

### Synthetic and defective data

Original rule-based generators state that records are fictional and retain seed/assumptions. A learned generator trained on personal data requires privacy and memorisation assessment; “synthetic” is not an automatic anonymisation finding. Deliberate corruption is stored separately from the clean base with a defect manifest. Transforming a public dataset by adding noise does not necessarily create a new freely redistributable dataset or remove attribution.

### Roles, monitoring, and evidence

Data owner maintains the record; legal/privacy functions provide required interpretation; security enforces classification; model owner uses only approved fields. Automated jobs verify checksum, schema and licence-record presence, but cannot determine legal basis. Reviews occur on contract/licence change, new purpose, new field, new geography, retention expiry or incident. Evidence includes terms snapshot/link, approval, data protection assessment where applicable, attribution, access logs and deletion record.

An exception has named dataset, limited purpose, environment, fields, users, safeguards and expiry. Ambiguity defaults to no production use and no redistribution. Breach, unauthorised access or licence violation follows incident policy and may require stopping downstream models.

## Policy 3 — Data contracts, quality, lineage, and quarantine

### Objective and scope

Every material model input and output has a data contract that supports point-in-time reconstruction, validation and operational control. Quality is fitness for the approved purpose, not a generic cleanliness score. The contract covers keys, definitions, event/availability timestamps, types, units, categories, nulls, ranges, cross-field rules, frequency, lineage, source owner and service level.

### Mandatory statements

Critical inputs must be uniquely keyed at the declared grain. Required fields cannot be imputed silently. Event time and ingestion/availability time are retained when they affect what was knowable. Transformations identify source columns, code/version and effective dates. Training, validation and scoring use the same definition or document an approved mapping.

Rules are classified as critical stop, controlled fallback, warning or informational before execution. Examples of critical failures are missing target source for development, duplicate decision key, post-decision leakage, corrupted artifact mapping, incompatible currency/unit and incomplete accounting perimeter. A critical stop quarantines the run and prevents publication, scoring, posting or capital reporting as applicable. A dashboard that reports red while the pipeline continues is not a quarantine control.

Repairs preserve raw values, repair rule, reason, owner and before/after counts. Model-based imputation is a learned transformation with training and validation; it is not data correction. Outlier handling distinguishes impossible, rare valid and high-risk values. Source-level remediation is preferred when feasible.

### Quality evidence and thresholds

Each run produces contract version, source snapshot/hash, rule results, affected rows/exposure, comparison with history, exceptions and disposition. Aggregate reconciliations compare source-to-stage, stage-to-feature and feature-to-model row counts and amounts. A second control validates that rule execution itself completed; absence of failures is not evidence if checks did not run.

Thresholds use business impact and statistical context. A 1% missing increase may be critical for an essential field and immaterial for an unused optional field. Monitor data volume, freshness, missingness, distribution, unseen categories, duplicates, reconciliation differences and repair rate by source/segment. Track recurring waivers and time to fix.

### Roles and change

Source owner fixes upstream issues; data owner approves definitions; model owner assesses impact; technology implements pipeline; independent validation challenges material transformations. A schema or code change requires impact analysis, regression, point-in-time test and updated contract. Emergency fallback has explicit permitted fields, maximum duration, customer/accounting impact and approval. Quarantined data are access-controlled and not reused as a convenient development sample.

## Policy 4 — Sample, target, default, and performance-window approval

### Objective and scope

The target specification determines what a model estimates. It must be approved before variable search and remain reproducible from event data. This policy covers PD/default, delinquency, bankruptcy, recovery, cure, LGD, CCF/EAD, prepayment, stage and other credit outcomes.

### Mandatory statements

The specification states unit (obligor, facility, account, invoice), event definition, horizon, observation date/window, performance window, aggregation, first/repeat event, cure/re-default, exclusions, outcome maturity, data sources and availability. It maps to intended use. Regulatory default, IFRS 9 Stage 3/credit-impaired status, accounting write-off and internal delinquency can be related but remain separate flags unless policy establishes identity.

Eligibility and exclusions are frozen in an ordered waterfall. Every removal has pre-defined reason and count/exposure. Cases without complete performance are censored or excluded under the design, not labeled non-events. Multiple snapshots per borrower use group/time splitting to prevent leakage. Accepted-only development states selection limits and any reject-inference method is sensitivity, not observed truth.

For LGD, the default episode, EAD reference, recoveries, costs, discounting, cure, collateral, currency and incomplete-case treatment are explicit. For EAD, reference date, limit, undrawn, balance at default, line changes and zero-undrawn treatment are explicit. For survival, censoring and competing events are defined.

### Approval and tests

Business and model owners approve economic purpose; data owner approves derivation; regulatory/accounting owners approve mapped use; validation independently reconstructs a sample. Evidence includes definition document, event-source lineage, SQL/Python version, timeline examples, positive/negative edge cases, waterfall, event rates by cohort and reconciliation to authoritative reports.

Tests cover event exactly on boundaries, event before observation, simultaneous events, late/reversed event, multiple facilities, cure/re-default, incomplete window, prepayment and source correction. Outcome backfills are versioned. A target definition change creates a new model dataset/version and impact analysis; it is not applied retrospectively without governance.

### Monitoring

Monitor event volume/rate, source lag, reversals, cure, duplicate events, incomplete share and definition exceptions. Compare model outcome to regulatory/accounting reports while explaining perimeter differences. A sudden performance gain can be a target-source problem. Target lineage is retained for historical decisions and validations after source systems change.

## Policy 5 — Scorecard development and characteristic approval

### Objective and scope

Application and behavioural scorecards must be interpretable, reproducible and stable from raw characteristic through score, grade and reason. Specialist scorecard libraries may support independent benchmarks, but the approved implementation documents every bin, WOE convention, coefficient and point calculation. This book’s primary implementation uses original code.

### Mandatory statements

Development begins only after sample, target, split and feature register are approved. Bins are learned on development. Manual cuts have operational or risk rationale; automated cuts satisfy minimum population and event/non-event rules and undergo business review. Missing, declared special codes and unseen categories have separate handling. Validation and out-of-time samples use frozen cuts.

The WOE convention is stated as good-to-bad or bad-to-good with target sign. Smoothing is fixed and justified. Characteristic tables include counts, shares, goods, bads, bad rate, WOE, IV, coefficient and points across samples/time. IV is not an automatic selection rule. Variable selection combines availability, legality, business meaning, univariate relationship, correlation/VIF, sign, stability, manipulation, incremental value and implementation.

Logistic estimation records objective, penalty, convergence, iterations and diagnostics. Coefficients are not manually edited after fitting; constraints or exclusions are part of a documented refit. Score scaling states base score, base odds, PDO, rounding, clipping and higher/lower risk direction. Rating boundaries and reason-code algorithm are approved separately.

### Approval evidence

Required artifacts are feature register, binning memo, characteristic presentation, WOE/IV audit, variable decisions, coefficient diagnostics, performance, calibration, score/PD round trip, points reconciliation, grade design, reason examples, artifact schema and golden tests. A reviewer reconstructs at least one account from raw values.

The model owner approves analytical proposal; business owner approves characteristic meaning and use; compliance/privacy reviews fields; validation challenges method/results; technology approves implementation readiness; committee grants use. Disagreement about a variable remains in minutes.

### Monitoring and change

Monitor input contract, bin shares, missing/special/unseen, WOE relationship, PSI/CSI, score/grade, discrimination, calibration, reasons, overrides and decision outcomes. Re-binning, variable regrouping, sign/coefficients, scale or grade changes are model changes. A policy cutoff change may not alter model, but its customer and selection impact is separately approved and monitored. Never alter production cuts to reduce a drift alert without redevelopment governance.

## Policy 6 — Machine-learning challengers, calibration, and explainability

### Objective and scope

Complex models may be developed when a clear hypothesis and expected decision benefit justify their data and control burden. They remain challengers until validated, calibrated, implemented and approved. Complexity is evaluated relative to a transparent benchmark on identical valid data.

### Mandatory statements

The search plan specifies algorithms, features, preprocessing, constraints, hyperparameter space, validation method, selection metric and compute budget before final test evaluation. Experiment records include all trials, not only the winner. The out-of-time or final test set is evaluated after selection and is not repeatedly used for tuning.

Probability calibration is a versioned component trained on an appropriate sample or cross-fitted. Raw and calibrated outputs are retained. Calibration method and use are documented; discrimination and calibration are evaluated separately. A common score mapping may report calibrated probability on the same PDO scale, but explanations remain model-specific.

Explainability distinguishes global structure, local attribution, sensitivity and counterfactual. Tree SHAP values require declared output space and background/implementation [R27]. Local explanations are tested for additivity or faithfulness as applicable, stability, direction and missing behavior. They do not prove causality or fairness. Logistic bin points must not be fabricated for a nonlinear model.

Monotonic constraints require business/statistical evidence and edge testing. Feature interactions, missing routing and unseen categories are documented. Protected or sensitive information is handled under legal policy and isolated audit views where appropriate. Fairness assessment includes sample/label limitations and decision context, not one ratio.

### Champion decision and monitoring

The committee compares performance, calibration, economics, stability, data reliance, subgroup outcomes, explanations, latency, resilience, monitoring, change frequency and operational complexity. Benefit must be material for intended use. Possible outcomes include champion, shadow, benchmark, restricted segment or reject.

Monitor raw/calibrated prediction, feature and interaction drift, explanation distribution, errors, latency, calibration and decisions. Foundation/library updates that change output are assessed. Retraining is never automatic based solely on drift; it requires approved data/target window, evaluation, validation and release. An agent may draft an investigation but cannot retrain or promote.

## Policy 7 — IFRS 9 impairment and management overlays

### Objective and scope

The institution estimates, reviews and posts expected credit losses using approved accounting policy, complete perimeter, controlled data, validated models, forward-looking scenarios and reconciled adjustments. This educational template does not determine compliance; the applicable IFRS 9 text and qualified accounting judgement govern [R5, R6].

### Mandatory statements

The accounting owner defines financial-instrument scope, reporting date, ECL measurement, effective-interest discounting, write-off, credit-impaired interest, modified assets, commitments/guarantees, revolving facilities, simplified approach and disclosures. Risk/model owners implement approved parameter and staging methods. Gross carrying amount and commitments reconcile to subledgers before calculation.

SICR policy combines quantitative change in default risk with qualitative indicators, watchlists, forbearance, DPD backstops and reasonable/supportable forward-looking information. Thresholds are not represented as IFRS-prescribed bright lines. Origin/current measures are comparable. Stage reasons, cure/probation and overrides are retained and monitored.

PD curves use valid marginal first-default probabilities. LGD reflects expected cash shortfalls, recoveries, collateral and timing under policy. EAD/cash flows cover applicable exposure and prepayment/drawdown. Scenarios have narratives, macro paths, model transformations, probabilities, approval and version. Nonlinearity is represented sufficiently; weights sum to one.

### Close controls

The engine reconciles period, scenario, account, stage, portfolio and entity. Closing allowance reconciles opening and movements to ledger. Source/configuration/model hashes are archived. Movement analysis explains volume, stage, risk parameters, exposure, scenario, model/data, write-off, FX and overlay under a declared attribution method. Independent review reproduces golden accounts and aggregate totals.

Management overlays address identified model/data gaps or exceptional risks. Each overlay has evidence, affected perimeter, method, amount/sign, double-count assessment, owner, approval, effective date, expiry, backtest and release rule. Overlays remain separate from model output. They cannot be used to manage earnings or conceal model failure.

### Monitoring and change

Monitor perimeter reconciliation, stage mix/migration, stage reasons/overrides, PD/LGD/EAD, scenarios, ECL, overlays, defaults, cure, recoveries, backtests and ledger differences. Scenario, weight, staging, model, source and overlay changes follow materiality/approval. Accounting signs the final allowance and disclosures; model committee approval alone is insufficient.

## Policy 8 — Basel IRB rating systems and capital calculation

### Objective and scope

IRB systems operate only within supervisory permission, applicable law and approved exposure classes. Rating systems support risk management and capital calculation under use-test, data, estimation, validation, governance and reporting requirements. The Basel Framework provides international standards; local implementation controls actual reporting [R1–R4, R10].

### Mandatory statements

Every exposure is mapped to legal entity, approach, asset class, obligor/facility, default status and credit-risk mitigation under approved rules. Unmapped or ineligible exposure does not default into a convenient IRB formula. Obligors are aggregated consistently. Ratings are assigned and reviewed under a documented process with override authority, independence and monitoring.

PD estimation uses approved default definition, historical observation, long-run average, grades/pools, calibration, conservatism, floors and representativeness. LGD uses workout/eligible methodology, recoveries, costs, discounting, cure, incomplete cases, collateral and downturn conditions. EAD/CCF defines reference/default exposure, undrawn, line changes and conservatism. Maturity follows regulatory definition.

Margins of conservatism map to named data/method deficiencies and uncertainty, with base, adjustment and final parameter reconciled. Deficiencies have remediation owners. Conservatism is not a reason to leave a material target or data defect unresolved. Parameter changes preserve versions and effective dates.

### Capital execution and reconciliation

The calculation stores input before/after applicable floors, asset-class correlation, maturity adjustment, K, RWA and subsequent regulatory adjustments. Golden tests cover every branch and boundary. Independent calculation verifies samples. Exposure and RWA reconcile to source/regulatory returns. Movement analysis covers volume, mix, approach, grade/PD, LGD, EAD, maturity, default and rule changes.

Regulatory implementation includes applicable output floor, transitional arrangements, defaulted exposures, expected loss/provision comparison, credit-risk mitigation, specialised lending and national discretions outside a generic teaching function. Formula results, adjustments and final reported values remain distinguishable.

### Governance and monitoring

Business uses ratings in credit approval, limits, pricing, monitoring and reporting as required by policy. Monitor overrides, migrations, realised defaults, grade calibration, recoveries, CCF, conservatism, floors, exceptions, data and RWA. Validation frequency/depth follows materiality and regulation. Capital/regulatory reporting owner approves returns; supervisory communication and permission are handled by authorised functions.

## Policy 9 — Independent model validation and finding management

### Objective and scope

Validation provides effective challenge of conceptual soundness, data, process, outcomes, implementation and governance before initial use and throughout the lifecycle. Depth is proportionate to materiality, complexity and uncertainty. Independence requires authority, access and competence; rerunning developer code alone is not validation.

### Mandatory statements

Validation scope identifies model/use versions, purpose, population, decisions, dependencies, material changes and prior findings. The validator assesses design against purpose, assumptions and alternatives; reconstructs data/target and a risk-based row sample; reproduces/benchmarks calculations; tests discrimination, calibration, stability, sensitivity, uncertainty and segments; evaluates limitations and controls; and reconciles implementation.

For scorecards, validation checks bins, WOE, coefficients, points, grades/reasons and parity. For ML, it checks search, calibration, explanations, constraints and robustness. For LGD/EAD, it rebuilds cash flows/CCF and incomplete cases. For IFRS 9, it checks staging, curves, scenarios, ECL and close reconciliation with accounting expertise. For IRB, it checks default/parameters, asset classes, formulas and regulatory controls. For agents, it checks evidence, trajectory, permission, approvals and red-team.

Outcomes are approve, approve with conditions, not approved or another framework-defined rating. Findings state requirement/evidence, condition, risk/consequence, severity, owner, action and due date. Severity considers financial, customer, legal/regulatory/accounting, operational and control impact. Model owner responses do not change a validator’s conclusion without evidence.

### Finding closure

Closure requires implemented remediation, testing, independent verification and residual-risk assessment. A management acceptance/waiver names authority, rationale, compensating controls and expiry; it does not mark the technical finding fixed. Recurring extensions escalate. Validation tracks open, overdue, repeat and accepted findings by tier.

### Ongoing validation

Trigger events include performance/calibration deterioration, data/source/target change, new population/use, methodology/calibration/grade change, implementation incident, regulation/accounting change, material override/overlay, agent/tool change and elapsed review period. Monitoring informs validation but does not replace it. Records include plan, evidence, code, independent outputs, report, responses, approvals and closure.

## Policy 10 — UAT, implementation reconciliation, and production sign-off

### Objective and scope

User acceptance testing proves that the implemented system satisfies approved business, model, data, accounting/capital, operational and control requirements in its target environment. UAT complements development QA and independent validation. It covers batch, API, user interface, downstream decisions, accounting/capital interfaces and reports.

### Mandatory statements

Requirements are uniquely identified and trace to tests. Every test records preconditions, input, expected output, observed output, tolerance, evidence, status, defect and retest. Test data cover normal, boundary, missing, special, unseen, malformed, duplicate, high volume, timeout, partial dependency and security/role cases. Personal production data are used only under approved controls.

Implementation reconciliation compares approved and production-style output at raw input, transformation, bin/encoding, model score, probability, calibration, score, grade, reason and policy result. ECL/IRB tests compare row components, aggregates and reporting/posting. Differences are explained; tolerances define units and rounding stage. Aggregate equality cannot excuse customer-level mismatches.

Parallel/shadow run uses identical population and reports count/exposure differences, decisions, grades, ECL/RWA, reasons, errors, latency and downstream acceptance. Old and new data cutoffs are aligned. The challenger cannot influence production during shadow without separate approval.

### Defects and sign-off

Defects have severity based on consequence. Critical defects block sign-off; lesser defects require disposition, owner and approved workaround/expiry. Rejected tests are not removed from the pack. Regression tests rerun after fixes. Sign-off roles include business/user owner, model owner, validation, data, technology/operations, security and accounting/capital/compliance where relevant.

Release readiness also requires artifact/configuration version, deployment/rollback, monitoring, support, training, access, batch calendar, recovery and incident contacts. UAT approval is limited to the tested version/environment. A material change after sign-off reopens affected tests.

## Policy 11 — Deployment, access, resilience, and rollback

### Objective and scope

Only approved model, policy and data artifacts may enter production through controlled release. The service must be reproducible, least-privileged, observable, resilient and recoverable. This policy applies to real-time and batch scoring, ECL/IRB engines, reporting jobs, model registries and agent services.

### Mandatory statements

Release references approved inventory/model/change records, source commit, artifact/configuration hashes, dependency manifest, test/UAT/validation evidence and release owner. Build occurs in a controlled pipeline. Secrets are stored in approved secret management and are not committed, logged or embedded in artifacts. Environments and credentials are separated.

Inputs are schema-validated. Failures follow approved stop, fallback or manual routes; no silent imputation or version fallback. Outputs identify model, calibration, policy, data and service versions. Logging observes correlation ID, outcome, timing, warnings and permitted diagnostics while minimising personal data. Access is role-based, reviewed and revoked on role change/retirement.

Canary or shadow deployment limits impact. Health checks test service and analytical golden cases. Performance targets cover availability, latency, throughput and batch completion. Resilience tests include dependency loss, malformed/oversized request, corrupted artifact, storage/network failure, duplicate/retry, partial batch and recovery. Idempotency prevents double posting or action.

### Rollback and emergency controls

Rollback identifies a compatible complete stack—code, model, calibration, schema and policy—not one file. It is tested before release. Accounting/capital runs preserve prior approved rerun capability. Emergency stop/kill switch has authorised roles, customer/accounting impact process and audit. An agent cannot trigger deployment or rollback; it may propose escalation from evidence.

Release evidence and production verification are archived. Unauthorised output difference or critical incident stops use under incident policy. Technology approves operational readiness; model/business/accounting/capital owners approve use. Deployment success does not substitute for those approvals.

## Policy 12 — Monitoring, thresholds, escalation, and redevelopment

### Objective and scope

Monitoring detects data, population, model, decision, component, operational and governance change early enough for action. It distinguishes leading indicators from mature outcome tests. Every metric links to an owner, threshold and response; monitoring is incomplete if alerts repeatedly expire without decisions.

### Mandatory statements

The monitoring plan states population/use, reference/current windows, frequency, segmentation, weighting, metric formula/bins, outcome maturity, thresholds, uncertainty, owner and action. Layers cover data contract/freshness; feature/score/grade; discrimination/calibration; decisions/economics/fairness; LGD/EAD/recovery/cure; IFRS stage/ECL/scenarios/overlays; IRB ratings/parameters/RWA; operations; and agents.

PSI/CSI uses frozen development or approved reference bins with smoothing and labels its convention. It is not a universal model-redevelopment rule. AUC/AR and KS assess ranking; Brier/log loss/calibration assess probabilities. Report volumes and intervals. Vintages compare outcomes at equal age. Backfilled outcomes are versioned.

Thresholds are green/amber/red or another approved structure. Critical data/implementation/policy failures stop or restrict according to runbook. Statistical alerts trigger investigation before recalibration/redevelopment. An investigation assesses data, target, selection, policy, economy, source, implementation and true relationship. Actions include accept with evidence, enhance monitoring, repair source, restrict/fallback, recalibrate, redevelop or retire.

### Reporting and governance

Dashboard totals reconcile to the modeled/decisioned population. Reports identify source/model/policy versions and unresolved exceptions. Material alerts go to the appropriate committee with consequence and due date. Overrides, waivers and repeated amber/red are aggregated. Monitoring agents may draft triage but deterministic policy and humans control action.

Redevelopment triggers include sustained material performance/calibration loss, invalid assumptions, major source/target/population/use/regulation change, irreparable implementation, material customer harm or expired architecture. A trigger initiates governance; it does not automatically promote a newly trained model. Champion remains controlled until replacement approval and verified cutover.

## Policy 13 — Model and policy change management

### Objective and scope

Changes are classified by effect on purpose, data, methodology, output, decision, accounting/capital amount, customer outcome and control. Line count or developer effort is not materiality. The policy covers source/schema, feature, target, model, calibration, score/grade, cutoff/rule, code, dependency, infrastructure, report, prompt, retrieval, tool and permission changes.

### Mandatory statements

Every change request states current/proposed state, rationale, affected inventory/version, population/use, expected output/customer/financial effect, risks, tests, validation, UAT, monitoring, rollback, owner and schedule. A diff and impact sample accompany technical changes. Materiality classification is independently challenged and approved under the tier framework.

Example categories may be: non-functional refactor with proven output identity; controlled maintenance with limited understood effect; material recalibration/source/policy change; redevelopment/new use. Categories determine validation and committee depth, but all production changes receive code review, tests, artifact/version and release evidence. Output identity requires golden and representative batch comparison, not developer assertion.

Data-source replacement is material when definitions, coverage, timing, population or missingness change even if columns keep names. Target/default or observation-window change normally requires redevelopment assessment. Calibration changes affect probability, score/grade and downstream ECL/decisions. Cutoff and price/limit rules can materially affect customers without changing the model. Dependency/foundation-model updates can change numerical or agent behavior.

### Emergency changes

Emergency action is limited to containing an active incident. It has authorised approver, exact scope, risk, test, rollback and expiry. Full retrospective documentation and independent review follow within defined time. Emergency cannot be used to meet a business date after ordinary governance was delayed.

### Records and post-implementation review

Maintain request, classification, approvals, code/config diff, tests, validation/UAT, release, rollback and monitoring. After release, compare expected/observed output, errors, decisions and financial amounts. Unexpected material effect invokes incident or rollback. Versions of model, calibration, policy and service remain separable so historical output can be reproduced.

## Policy 14 — Governed agentic AI and human approval

### Objective and scope

Agentic systems in credit risk operate only within bounded, documented purpose and deterministic permissions proportionate to consequence. They can retrieve approved evidence, perform analysis and propose actions. They cannot acquire authority through prompts, retrieved documents or tool access. Customer decisions, material model changes, deployment and accounting/capital postings remain prohibited or under separately approved human/executor controls.

### Mandatory statements

Every agent has inventory ID, owner, agent card, foundation/model version, system prompt/version, retrieval sources, tools, memory, actions, permission policy, evaluation, monitoring, fallback and kill switch. Evidence objects have source, time, owner/classification and digest. Retrieved/free text is untrusted. Secrets and personal data are minimised; memory is scoped and retained/deleted under policy.

Permissions are deny by default and exact. Separate read, proposal, approval and execution. Explicitly prohibit deciding credit/affordability, changing price/limit/cutoff, retraining, promoting/deploying, altering/suppressing evidence, regulatory parameter changes, ledger posting and restricted export. Unknown actions/agents are denied. The proposal orchestrator has no material executor credential.

Human approval records reviewer identity/role, evidence, exact proposal hash/scope, decision, time and expiry. Modified or replayed proposals need new approval. Reviewers have adequate information, time and authority; monitoring detects rubber-stamping and systematic overrides. High-consequence execution, if authorised outside this teaching package, uses a separate service that re-verifies approval and limits.

### Evaluation and release

Test ordinary tasks, factual/evidence support, unsupported claims, tool/arguments, complete trajectory, permissions, approval integrity, latency, cost and recovery. Red-team prompt injection, poisoned/stale retrieval, exfiltration, privilege escalation, false authority, replay, population expansion, unavailable/partial tools and malicious data. Any prohibited action, secret exposure or unlogged write is critical.

Re-evaluate after foundation model, prompt, retrieval, tool, memory, policy, permission or workflow change. Monitor task success, unsupported claims, denials, overrides, incidents, cost and drift. The system follows NIST AI risk concepts as useful voluntary structure while applicable law, including high-risk credit-use obligations where relevant, requires legal assessment [R8, R11, R12].

## Policy 15 — Incident response, containment, and customer/accounting correction

### Objective and scope

An incident is an event that compromises model/data correctness, lawful use, security, availability, customer treatment, accounting/capital output, evidence integrity or authorised agent behavior. The response prioritises containment and impact while preserving evidence. A performance alert becomes an incident when defined severity conditions are met.

### Severity and notification

Severity considers affected customers/accounts/exposure, financial misstatement, regulatory return, unlawful discrimination/privacy/security, duration, reversibility, control bypass and recurrence. Critical examples include wrong score/grade due to mapping, leaked target in production feature, incorrect ECL posting, incorrect IRB perimeter, unauthorised deployment, agent customer action, evidence suppression or sensitive-data exfiltration.

On detection, record time, reporter, system/version, evidence and suspected scope. Notify incident lead and required business, model risk, technology/security, compliance/privacy, accounting/capital, legal and communications roles. External notification obligations are determined by authorised specialists; technical teams do not improvise them.

### Containment and analysis

Possible containment includes stop scoring/job, disable action, fallback/manual route, quarantine data, freeze posting/report, revoke credential, rollback or restrict population. Preserve logs, inputs, artifacts, approvals and hashes. Do not “fix forward” by overwriting evidence. Establish incident window and affected decisions/amounts through reproducible queries.

Root-cause analysis distinguishes triggering event, underlying control weakness and detection failure. Reproduce the fault and test absence in corrected version. Estimate customer, financial, regulatory and operational impact with uncertainty. Determine whether historical decisions, notices, prices, limits, collections, allowances or returns require correction under qualified owner guidance.

### Closure and learning

Closure requires contained risk, validated correction, restored service/control, affected-party treatment decision, required reporting, root cause, remediation owners/dates and independent verification. Temporary workaround expires. Update tests, monitoring, policy and training. Track time to detect/contain/recover, affected scope, recurrence and overdue actions. Committee and audit receive material incident reporting without sanitising uncomfortable evidence.

## Policy 16 — Documentation, records, reproducibility, and publication

### Objective and scope

Documentation enables an informed independent person to understand purpose, reproduce material output, evaluate limitations and trace authority. Records cover development, validation, decisions, accounting/capital calculations, implementation, monitoring, changes, incidents, agents and public educational publication.

### Mandatory model record

The model document includes executive purpose/use; product/population/lifecycle; law/accounting/regulatory mapping; data and licence/lineage; sample/target; EDA/quality; methodology and alternatives; estimation/calibration; performance/stability/uncertainty; economics/customer outcomes; limitations; implementation; validation/UAT; governance; monitoring; and retirement. Formula and code references include versions. Assertions cite evidence; unavailable information is labeled.

The reproducibility package contains commit, environment/dependencies, dataset record/hash/extraction, configuration/seed, artifact hash, commands, tests and result tables. Generated reports link to their machine-readable data. Screenshots are supplemental. Records use access classification and approved retention; documentation does not justify unnecessary personal-data copies.

### Accounting, capital, and decision records

Each close/return retains perimeter reconciliation, input/model/configuration, scenarios/parameters, row/aggregate output, overlays/adjustments, movement, approvals and posted/reported reconciliation. Each material decision system retains model/policy versions and reasons sufficient for lawful explanation/contest under applicable policy. Access to historical reconstruction is maintained after retirement.

### Public and educational publication

Before GitHub/book publication, remove secrets, personal/confidential data, unauthorised datasets, internal policy and oversized generated artifacts. Confirm open-source code licence and third-party notices. Dataset documentation cites creator, source, DOI/licence, retrieval and modifications. Do not reproduce copyrighted books/standards beyond permitted quotation; summarise in original words and link to authorised sources. Attached materials with use permission remain references, not text to copy.

### Quality and change

Documentation is reviewed with the model, not months later. Automated checks can verify required sections, links, chapter count, notebook validity and reproducible tests. Humans verify truth, clarity and judgement. Material changes update affected documents and issue a version history. Draft/review/approved status is visible. Records cannot be deleted merely because they document a rejected model, dissent or incident.

## Policy playbook adoption checklist

Before adopting any template, map the responsible legal entities, products, jurisdictions, regulations, committees, three-lines roles, tier thresholds, materiality and retention. Resolve conflicts with higher authority. Train owners and operators, implement evidence/workflows, test quarantine/rollback/kill switch, and set an effective date. Measure whether controls operate, not only whether documents exist. Annual review alone is insufficient when law, accounting, product, data or technology changes earlier.

The playbook’s central principle is separation with reconciliation: data owners establish evidence; models estimate; policy governs use; accounting/capital owners control specialised interpretation; technology operates; validation challenges; committees approve; audit assesses; and agents remain bounded assistants. Every layer connects through identifiers, versions, reasons and totals so responsibility cannot disappear between them.

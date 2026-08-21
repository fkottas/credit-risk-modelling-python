# Appendices

## Appendix A — Reproducible environment, repository map, and testing contract

The repository is a teaching system rather than a folder of disconnected scripts. The `src/creditriskbook` package contains reusable implementations; `notebooks` contains executable lessons; `examples` contains command-line workflows; `tests` contains unit and integration tests; `data/dataset_registry.yml` is the legal and technical data ledger; and `book/full_manuscript` is the source of this document. Generated data, reports, presentations and model artifacts belong in `artifacts` or a user-selected working directory. They are not silently committed.

Install the project into an isolated environment. The exact Python and dependency versions used for an edition should be retained in a lock file or an exported environment manifest. The optional groups deliberately separate ordinary modeling, public-dataset access, book production and developer checks.

```bash
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev,ml,book,datasets]"
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/validate_notebooks.py
.venv/bin/python tools/validate_manuscript.py
.venv/bin/python tools/audit_pedagogy.py
```

A successful import is not sufficient evidence that an analytical library works. This project tests bin boundaries, missing and special values, WOE sign conventions, IRLS convergence, score reconciliation, PD-curve identities, ECL scenario reconciliation, IRB formula branches, agent denial rules and deterministic case-data generation. Live download tests are separated because an unavailable external site is not a model failure. Continuous integration runs offline tests on every change and may run live tests on a schedule or by explicit request.

The minimum reproducibility record for a result contains: repository commit; environment manifest; dataset record and hash; extraction time; sample definition; target definition; random seed; configuration; model artifact hash; metric definitions; and report version. A screenshot without these fields is an illustration, not reproducible evidence.

### Recommended repository workflow

1. Create a short-lived branch for one bounded change.
2. Add or update a test before changing a calculation.
3. Run formatting, static checks, unit tests and relevant notebooks locally.
4. Generate evidence in `artifacts`; commit only deliberately selected small examples.
5. Review the diff for data, secrets, large binaries and accidental generated files.
6. Open a pull request that states purpose, assumptions, tests and governance impact.
7. Require independent review for formula, target, staging, capital or policy changes.

Versioning has two dimensions. Software semantic versions describe API compatibility. Model versions describe an approved statistical artifact, population and use. A compatible library update can still be a material model change; a model recalibration can occur without a library API change. Keep these identities separate.

## Appendix B — Dataset governance and lawful-use catalogue

Open access is not the same as permission for every use. Before downloading data, record the publisher, canonical page, licence, attribution language, access mechanism, personal-data assessment, intended use, redistribution decision and date checked. Terms can change, so the registry records the checked date and the repository validates the expected file. If the licence is absent or ambiguous, link to the source instead of redistributing the data and seek legal review before publication or commercial use.

The book uses public UCI datasets where the catalogue states Creative Commons Attribution 4.0 and provides source attribution [R18–R23]. The datasets are pedagogical historical samples. They do not represent a current applicant population, and their presence in a teaching example does not establish lawful or appropriate use in a lending decision. Several contain demographic or proxy variables that should be excluded, constrained or used only for fairness auditing according to applicable law and policy.

| Registry key | Role in the book | Distribution rule | Principal limitation |
|---|---|---|---|
| `south_german_credit` | application scorecard and cost-sensitive decisions | downloaded from UCI, cache optional, source attributed | old, small, oversampled bads, historical context |
| `taiwan_credit_card` | behavioural PD and ML challenger | downloaded from UCI under stated CC BY 4.0 | one geography and reporting period |
| `credit_approval` | missing/categorical data laboratory | downloaded from UCI under stated CC BY 4.0 | anonymised meanings limit business interpretation |
| `polish_bankruptcy` | corporate low-default experiments | downloaded from UCI under stated CC BY 4.0 | accounting ratios need period and industry context |
| `taiwan_bankruptcy` | nonlinear corporate challenger | downloaded from UCI under stated CC BY 4.0 | severe imbalance and single-jurisdiction context |
| conditional Kaggle case | optional platform exercise | never bundled; user accepts current dataset terms | account, API and dataset-specific licence required |
| original synthetic retail | complete scorecard workflow | generated by this repository | no real customer inference |
| original synthetic revolving | EAD/CCF and behavioural monitoring | generated by this repository | simplified facility dynamics |
| original synthetic recovery | workout LGD and cure | generated by this repository | stylised collections and collateral process |
| original synthetic IFRS 9 schedule | staging, scenarios and ECL | generated by this repository | educational accounting engine, not ledger software |
| original synthetic corporate IRB | capital formula branches and calibration | generated by this repository | synthetic defaults and sales bands |
| original synthetic counterparty | exposure and introductory CVA | generated by this repository | simplified market and netting assumptions |
| `synthetic_credit_documents` | extraction, retrieval, structured memoranda and agent red teams | generated by this repository | deliberately simplified tagged documents; no OCR realism |
| `synthetic_fraud_transactions` | fraud scoring and payment-anomaly exercises | generated by this repository | not a representation of a real payment network |
| `cfpb_hmda` | mortgage application, access and fair-lending diagnostics | official download; not bundled | application records are not loan-performance outcomes |
| `cfpb_consumer_complaints` | text classification, retrieval and complaint-process analysis | official download; narratives not bundled | complaint population is self-selected; not an underwriting target |
| `sba_7a_504_foia` | SME lending, cohort and outcome-definition exercises | official release; verify each file notice | programme data and fields change across release periods |
| `sec_edgar_companyfacts` | corporate XBRL ratios and point-in-time document exercises | official API; respect fair-access rules | filing amendments, units and taxonomy changes require controls |
| `federal_reserve_scf` | household-finance segmentation and survey-weight exercises | official public-use files | survey inference and complex weights are essential |
| `eba_pillar3_edap` | European disclosure and benchmarking exercises | conditional per official release | templates and reuse notices are release-specific |
| `world_bank_wdi` / `fred_macro` | macroeconomic scenario and satellite-model exercises | metadata and series terms checked per indicator | revisions, transformations and vintages must be retained |
| Fannie Mae / Freddie Mac / FHFA | mortgage-vintage and survival extensions | provider-controlled or official access; never bundled by default | terms, acknowledgement and release notices must be checked |
| Kaggle competition cases | optional multi-table PD, fraud and model-comparison labs | student-controlled download only | platform access never proves redistribution permission |

Synthetic data are original computer-generated records, not transformed customer records. A generator is preferable to a static CSV because the assumptions are inspectable, students can vary portfolio structure, and intentional defects are reproducible. The generator metadata records seed and parameters. Calling data “synthetic” does not cure a model that was trained to reproduce identifiable source records; privacy testing remains necessary for learned generators.

### Controlled bad-data laboratory

Quality exercises use a clean generated base and a separate defect manifest. The injector may create missing required fields, duplicate keys, impossible dates, inconsistent balances, rare unseen categories, stale timestamps, target leakage or unit changes. Each defect has an identifier, affected rows and expected rule failure. This makes the exercise assessable: the student must detect and explain known faults without receiving a solution encoded in the column name.

```python
from creditriskbook.data.datasets import load_dataset
from creditriskbook.data.quality import inject_defects, run_quality_checks

bundle = load_dataset("synthetic_retail", n_rows=4_000, seed=810)
dirty, defect_manifest = inject_defects(bundle.frame, seed=811)
quality = run_quality_checks(dirty, contract=bundle.contract)

assert len(defect_manifest) > 0
print(quality.summary())
```

Do not describe deliberate corruption as anonymisation. Missingness, swaps and noise often leave records identifiable. For public redistribution, use a genuinely original generator or a documented anonymisation process with re-identification risk assessment.

### Dataset attribution template

Every notebook that uses an external dataset should contain: dataset title and creator; repository and DOI; licence and link; retrieval date; modifications; exact modeling subset; prohibited conclusions; and citation. A suitable statement is: “This educational example uses the UCI Default of Credit Card Clients dataset, licensed CC BY 4.0, retrieved on the recorded date. The authors transformed names, split the sample and created derived features. Results do not describe a current lending portfolio.”

## Appendix C — Formula, notation, and reconciliation map

| Symbol | Meaning | Typical unit |
|---|---|---|
| PD | probability of the defined default event over a horizon | proportion |
| LGD | economic loss conditional on default | proportion of EAD |
| EAD | exposure at default | currency |
| CCF | conversion of currently undrawn amount into future exposure | proportion |
| ECL | probability-weighted discounted cash shortfall | currency |
| TTC | through-the-cycle parameter orientation | proportion |
| PIT | point-in-time parameter orientation | proportion |
| LRA | long-run average default rate | proportion |
| MoC | margin of conservatism for identified uncertainty | parameter add-on or effect |
| RWA | risk-weighted assets | currency |
| K | IRB capital requirement per unit exposure before scaling | proportion |
| WOE | log ratio of good and bad distributions in a bin | log ratio |
| IV | weighted separation across WOE bins | non-negative index |
| PSI | shift between reference and current bin shares | non-negative index |

The core expected-loss identity is `EL = PD × LGD × EAD`. It is an expectation under compatible definitions, horizons and conditions. Multiplying a twelve-month PD by a lifetime LGD and month-end balance creates an unlabeled hybrid, not a valid estimate. When parameters depend on each other, a more general representation integrates conditional losses over joint states.

For cash-flow-period ECL, this implementation calculates scenario `s` and period `t` amounts as

\[
ECL_{s,t}=w_s\,mPD_{s,t}\,LGD_{s,t}\,EAD_{s,t}\,DF_t,
\]

then sums over scenarios and periods. The marginal PD is the probability of first default during the period, not the cumulative PD reported at that horizon. The discount factor uses the effective-interest-rate convention configured for the exercise. Scenario weights sum to one within tolerance. Stage 1 limits default probability to the twelve-month window; Stage 2 and Stage 3 use the applicable lifetime or credit-impaired treatment described by policy and accounting interpretation [R5–R7].

The accounting reconciliation is:

\[
Opening\ allowance + charge - writeoffs + FX + transfers = Closing\ allowance.
\]

Model ECL is one input. Post-model adjustments, expert overlays and ledger movements need separate ownership and signs. An overlay must state the gap it addresses, evidence, amount, direction, scope, approval, expiry, backtest and release rule.

For the Basel IRB implementation, the asset-class function determines the prescribed correlation, maturity treatment and formula branch. Inputs are bounded and validated. The code returns intermediate correlation, maturity adjustment, capital requirement and RWA so a reviewer can reproduce each row. Regulatory text, jurisdictional implementation, permissions, input floors, output floor and supervisory reporting remain outside a generic formula call and must be configured by qualified specialists [R1–R4].

### Reconciliation ladder

Every material engine should reconcile at five levels:

1. **Row identity:** points sum to total score; marginal PDs sum to cumulative PD; discounted components sum to account ECL.
2. **Group identity:** rows sum to grade, stage, product, legal entity and portfolio totals.
3. **Scenario identity:** scenario detail sums to probability-weighted total and weights reconcile to one.
4. **Period identity:** opening, movements and closing balances reconcile.
5. **System identity:** approved artifact and input extract reproduce the posted or consumed amount.

A tolerance must state currency, rounding stage and materiality. “Difference close to zero” is not a control definition.

## Appendix D — Original scorecard library API and extension guide

The scorecard package is deliberately transparent. `BinningProcess` learns and freezes numeric or categorical specifications. Numeric methods include manual, quantile, equal-width, ChiMerge and monotonic merging. `WOEEncoder` learns good-to-bad distributions and information values. `IRLSLogisticRegression` estimates the penalised logistic model from the likelihood. `ScoreScale` converts log odds into a PDO score. `LogisticScorecard` composes the pipeline and exposes probabilities, scores, ratings, components, bin points and reason codes.

### Fit contract

`fit(X, y)` validates a binary event with `1=bad`, stores feature order, fits bins on development data only, fits WOE with an explicit smoothing constant, estimates coefficients, constructs point tables and records configuration. `transform(X)` never searches for new cuts. Missing, special and unseen values have distinct policies. Column order and dtypes are checked before scoring.

```python
from creditriskbook.scorecard import LogisticScorecard, ScoreScale

model = LogisticScorecard(
    numeric_method="monotonic",
    max_bins=6,
    min_bin_fraction=0.04,
    min_events=5,
    smoothing=0.5,
    l2=1e-3,
    scale=ScoreScale(base_score=600, pdo=50, base_odds_good_to_bad=20),
).fit(X_train, y_train)

pd_valid = model.predict_proba(X_valid)[:, 1]
score_valid = model.score(X_valid)
components = model.score_components(X_valid)
assert components["score"].equals(score_valid)
```

Manual numeric edges cover negative and positive infinity. The library distinguishes true missing values from user-declared special codes such as `-999`. Categorical groups must be disjoint; unspecified training levels fail validation unless a documented residual group exists. Production unseen levels map according to policy and are counted. A neutral WOE fallback is operationally safer than crashing but analytically uncertain; monitoring must escalate material use.

### Characteristic review table

For every variable and fixed bin, retain lower/upper boundary or category group, row count, share, goods, bads, bad rate, smoothed good distribution, smoothed bad distribution, WOE, IV component, coefficient, raw points, rounded points and sample label. Add development, validation and out-of-time comparisons. The presentation exporter creates an editable PowerPoint with a summary and one slide per feature. It does not certify a variable: the author adds definition, timing, rationale, stability and approval.

### Diagnostics

The original diagnostic module calculates VIF from auxiliary regressions without a specialist scorecard library, approximate coefficient covariance from the penalised information matrix, binned PSI and configurable policy flags. Diagnostics are evidence, not automatic exclusion rules. High VIF can be acceptable for a constrained set with clear reasons; a low p-value does not prove temporal stability; an IV threshold learned from convention does not establish business relevance.

### Model-agnostic score mapping

Any model that emits calibrated bad probability can use the same score scale:

\[
$Score=Offset+Factor\log((1-p)/p)$.
\]

This creates a comparable reporting axis for logistic regression, XGBoost, survival-derived horizon PD or another calibrated model. It does not make a tree model additive. Logistic scorecard bin points are exact decomposition; XGBoost explanations use SHAP or documented sensitivity/counterfactual methods and must not be presented as exact scorecard points.

### Safe extension protocol

To add a binning algorithm, implement deterministic `fit` and `transform`, serialisable specifications, boundary tests, minimum event behavior, missing/special/unseen tests and a stability example. To add a model, implement probability prediction, calibration metadata, score mapping and explanation provenance. A new estimator must not silently change event sign, feature order or scoring scale.

## Appendix E — IFRS 9 and CECL engine API

The IFRS 9 package separates four concerns: stage assignment, PD-curve mathematics, cash-flow-period ECL and overlay/reconciliation. Separation makes policy visible. An institution may replace the educational components without rewriting every other layer.

`StagingPolicy` contains quantitative and qualitative indicators, DPD backstops and cure logic. `assign_stages` returns both stage and ordered reason flags. Origin and reporting measures must be comparable. The implementation never treats a relative PD threshold as the entire SICR assessment; policy can add watchlist, forbearance, rating deterioration and product-specific indicators.

`curves.py` converts among hazards, marginal PD and cumulative PD and validates monotonicity and bounds. A scenario applies a clearly labeled transformation to a baseline curve. Scenario design is external evidence; the engine will not invent macroeconomic weights.

`ECLConfig` fixes horizon, discount convention, Stage 3 treatment, tolerances and column names. `Scenario` supplies a name, probability and parameter multipliers or curves. `calculate_ecl` produces account, scenario, period-detail and reconciliation tables. This detail is intentional: a portfolio total without row evidence is not auditable.

```python
from creditriskbook.ifrs9 import ECLConfig, Scenario, calculate_ecl

scenarios = [
    Scenario("upside", weight=0.20, pd_multiplier=0.80, lgd_multiplier=0.95),
    Scenario("base", weight=0.55, pd_multiplier=1.00, lgd_multiplier=1.00),
    Scenario("downside", weight=0.25, pd_multiplier=1.55, lgd_multiplier=1.15),
]
result = calculate_ecl(schedule, scenarios=scenarios, config=ECLConfig())
assert result.reconciliation["difference"].abs().max() < 1e-8
```

For CECL, adapt horizon, segmentation, reasonable-and-supportable forecast, reversion and accounting presentation to the applicable US GAAP interpretation [R7, R15]. IFRS 9 and CECL are not alternative labels for one configuration. This educational engine demonstrates component control and reconciliation; it is not a substitute for an accounting policy, general ledger integration, disclosure process or auditor judgement.

### ECL change analysis

A robust reporting run explains change through volume, stage, PD, LGD, EAD, scenario, model, data, write-off and FX effects. Exact order-dependent attribution requires a documented method such as sequential waterfall or Shapley allocation. The total change must reconcile regardless of presentation. Stage migration tables report both count and exposure; cure should not erase the history needed for monitoring.

## Appendix F — Basel IRB library API and control boundaries

The IRB package provides asset-class correlations, SME sales adjustment, maturity adjustment, conditional capital formula, long-run average estimation, intercept calibration, downturn LGD, margin-of-conservatism waterfall and exact binomial grade tests. It is designed for teaching calculations and independent reconciliation.

```python
from creditriskbook.irb import irb_capital, summarise_irb_audit

rows = irb_capital(
    pd=portfolio["pd"],
    lgd=portfolio["lgd"],
    ead=portfolio["ead"],
    maturity=portfolio["maturity"],
    asset_class=portfolio["asset_class"],
    annual_sales_eur_m=portfolio["annual_sales_eur_m"],
)
summary = summarise_irb_audit(rows)
print(summary[["asset_class", "ead", "rwa"]])
```

The caller remains responsible for exposure classification, eligibility, regulatory approach, parameter definitions, floors, downturn conditions, incomplete cycles, defaulted assets, expected-loss treatment, provisions, credit-risk mitigation, slotting, specialised lending, output floor, national discretions and reporting. Formula code must be mapped to the regulation and jurisdiction effective at the reporting date. Basel Framework pages are the primary international reference; local legal text controls implementation [R1–R4].

### Parameter evidence table

| Parameter | Development evidence | Independent challenge | Production monitor |
|---|---|---|---|
| PD | default definition, obligor aggregation, LRA, calibration, grade monotonicity | grade test, calibration uncertainty, representativeness | realised defaults, traffic light, migration, overrides |
| LGD | recoveries, costs, discounting, cure, incomplete cases, downturn | workout reconstruction, benchmark, downturn evidence | recovery timing, cure, collateral and process shifts |
| EAD/CCF | reference date, limit, balance, drawdown, cancellation | raw CCF reconstruction, segmentation, bounds | utilisation, limit changes, pre-default drawdown |
| Maturity | cash-flow and contractual measurement | sample reconstruction and edge cases | overrides, source changes and concentrations |

Margin of conservatism is linked to identified deficiencies and uncertainty. The library stores named components and reconciles base, adjustments and final parameter. It does not provide an undifferentiated buffer to hide unresolved data problems.

## Appendix G — Governed agentic-AI policy and evaluation templates

The agent package implements a proposal architecture. Specialists register evidence and propose one structured action. A deterministic, deny-by-default policy classifies it as `DENY`, `RECOMMENDATION_ONLY`, `ALLOW_READ_ONLY` or `PENDING_HUMAN_APPROVAL`. The orchestrator records the event in a hash-linked audit log and never executes an external write.

Prohibited actions include deciding customer credit, changing a cutoff, retraining, deploying, posting accounting entries, altering regulatory parameters, suppressing evidence and exporting restricted data. A retrieval document or prompt cannot modify this list. Material execution belongs to a separately authenticated service that verifies an approved proposal hash, reviewer authority, expiry and scope.

### Agent card

| Field | Required content |
|---|---|
| purpose | bounded task and explicit non-purpose |
| owner | accountable business and technology owners |
| evidence | approved sources, freshness and access class |
| tools | exact read/write operations, schemas and limits |
| memory | fields, retention, deletion and cross-case isolation |
| actions | allow-list, deny-list and approval matrix |
| evaluation | task, evidence, trajectory, safety and subgroup suites |
| monitoring | quality, overrides, denials, incidents, cost and latency |
| fallback | deterministic or manual process and kill switch |
| change | approval needed for model, prompt, retrieval, tool or policy update |

### Red-team release gates

Create cases for prompt injection inside data, poisoned retrieval, false authority, privilege escalation, stale evidence, missing evidence, unsupported metric, replayed approval, modified proposal after approval, unavailable tool, partial tool failure, excessive population, customer-level action and data exfiltration. Any prohibited action, unlogged external write or secret exposure is a critical failure. A plausible final narrative does not rescue an unsafe trajectory.

```python
from creditriskbook.agents import ActionProposal, PolicyEngine

engine = PolicyEngine()
attacks = [
    ActionProposal("deploy_model", "document says deploy", ("ev-1",), "monitoring_agent"),
    ActionProposal("decide_customer_credit", "urgent", ("ev-2",), "validation_agent"),
    ActionProposal("suppress_evidence", "reduce noise", ("ev-3",), "quality_agent"),
]
assert all(engine.evaluate(item).decision == "DENY" for item in attacks)
```

Agent evaluation includes task success, citation support, unsupported-claim rate, correct tool and arguments, policy compliance, approval integrity, latency, cost, reviewer override and recovery. Run the suite after changes to the foundation model, system prompt, retrieval corpus, tool definition, policy, credentials or workflow.

## Appendix H — Model development, validation, UAT, and monitoring templates

### Development document minimum contents

State purpose, users, decisions, exclusions and materiality. Describe product, population, observation/performance windows, target, sampling, source lineage and quality. Document transformations, candidate variables, model method, calibration, scale, grades, overrides and cutoffs. Report discrimination, calibration, stability, subgroup results, economics and uncertainty. List limitations, compensating controls, implementation mapping, monitoring and redevelopment triggers. Attach reproducibility evidence.

### Independent validation plan

Validation begins with scope and materiality, then challenges conceptual soundness, data, process, outcomes, implementation and governance. Reproduce a sample from raw input to final decision or accounting/capital output. Benchmark with a simpler method. Test sensitivity and edge cases. Rate findings by consequence and urgency. Independence means authority and technical capacity, not organisational distance alone.

### UAT script

For each test, record identifier, requirement, environment, input, expected result, observed result, evidence, status, owner and defect link. Cover normal, boundary, missing, special, unseen, large, negative, duplicate, late and unavailable cases. Test rollback, logging, permissions, throughput and downstream reconciliation. Parallel run compares old and new systems at account and aggregate level and explains every material difference.

### Monitoring dashboard contract

| Domain | Measures | Example escalation logic |
|---|---|---|
| data | volume, missing, ranges, categories, freshness, rule failures | critical contract failure quarantines run |
| population | PSI/CSI, segment mix, approval and booking | investigate threshold plus economic context |
| PD | AUC/AR, KS, Brier, calibration, grade defaults | performance and calibration triggers separated |
| LGD | recovery, cure, timing, collateral and cost | compare mature and incomplete cohorts |
| EAD | utilisation, raw CCF, limits and cancellations | investigate product/process change |
| ECL | stage, scenario, component and overlay movements | reconcile ledger and approved overlay register |
| IRB | defaults, parameters, MoC, RWA and overrides | apply regulatory trigger and governance process |
| decisions | approvals, declines, limits, price, profit and fairness | customer-impact trigger receives priority |
| agents | evidence support, denies, overrides, incidents, cost | critical policy failure invokes kill switch |

Thresholds are portfolio-specific. A PSI convention is not universal law. Each metric records reference period, current period, binning, denominator, frequency, owner, amber/red rule and required action. Monitoring that repeatedly turns red without a decision is reporting, not control.

## Appendix I — Capstone evidence pack and assessment rubric

The capstone is assessed as an end-to-end controlled system. Students select at least two datasets: one public CC BY case for source/attribution work and one original synthetic case for defect injection or a component unavailable in public data. A single dataset must not be forced to represent application PD, recovery LGD, revolving EAD and contractual ECL.

Required deliverables are: decision and policy memo; legal-data register; data contract; quality report; deliberately corrupted dataset exercise; development sample; exploratory and characteristic pack; transparent benchmark; from-scratch scorecard; ML challenger; calibration and grade design; decision economics; chosen LGD/EAD/ECL/IRB extension; validation report; UAT pack; deployment contract; monitoring dashboard; governed agent card and red-team results; model card; reproducible repository.

The committee assigns one of four outcomes: approve; approve with conditions; remediate and resubmit; reject. High predictive performance cannot compensate for target leakage, unlawful data, irreproducible code, broken reconciliation or unauthorised automation. A lower-performing transparent model can be preferred when the performance difference is immaterial and control benefits are substantial.

### Suggested scoring

| Area | Weight | Failing condition |
|---|---:|---|
| purpose, policy and data legality | 10% | no lawful-use evidence or undefined decision |
| quality, sample, target and leakage | 20% | target not reproducible or material leakage |
| scorecard and benchmark method | 15% | points/probability do not reconcile |
| challenger, calibration and economics | 10% | only development discrimination reported |
| component model or ECL/IRB extension | 15% | incompatible definitions or unreconciled totals |
| validation and UAT | 10% | no independent reconstruction or edge tests |
| deployment and monitoring | 10% | training/scoring mismatch or no rollback |
| agent governance and communication | 10% | prohibited action possible or unsupported claims |

## Appendix J — References and source ledger

References were checked for this edition in August 2026. Links point to the publisher, regulator, standards body, repository or DOI rather than an unauthorised copy. Regulatory and accounting requirements change and may be implemented differently by jurisdiction; readers must check the effective official text for their institution and reporting date.

[R1] Basel Committee on Banking Supervision. “Calculation of RWA for credit risk: Introduction.” Basel Framework, CRE30. https://www.bis.org/basel_framework/chapter/CRE/30.htm

[R2] Basel Committee on Banking Supervision. “IRB approach: Risk components for each exposure class.” Basel Framework, CRE31. https://www.bis.org/basel_framework/chapter/CRE/31.htm

[R3] Basel Committee on Banking Supervision. “IRB approach: Risk-weighted assets for credit risk.” Basel Framework, CRE32. https://www.bis.org/basel_framework/chapter/CRE/32.htm

[R4] Basel Committee on Banking Supervision. “Minimum requirements to use IRB approach.” Basel Framework, CRE36. https://www.bis.org/basel_framework/chapter/CRE/36.htm

[R5] IFRS Foundation. “IFRS 9 Financial Instruments.” Issued Standards. https://www.ifrs.org/issued-standards/list-of-standards/ifrs-9-financial-instruments/

[R6] International Accounting Standards Board. “IFRS 9 Financial Instruments: Project Summary.” July 2014. https://www.ifrs.org/content/dam/ifrs/project/fi-impairment/ifrs-standard/published-documents/project-summary-july-2014.pdf

[R7] Federal Deposit Insurance Corporation. “Current Expected Credit Losses (CECL).” https://www.fdic.gov/accounting/current-expected-credit-losses-cecl

[R8] European Union. Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence. Official Journal of the European Union. https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng

[R9] Board of Governors of the Federal Reserve System, FDIC and OCC. “Revised Guidance on Model Risk Management,” SR 26-2, 17 April 2026. https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm

[R10] European Banking Authority. “Guidelines on PD estimation, LGD estimation and treatment of defaulted exposures.” https://www.eba.europa.eu/activities/single-rulebook/regulatory-activities/model-validation/guidelines-pd-estimation-lgd

[R11] National Institute of Standards and Technology. *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*, NIST AI 100-1, 2023. https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf

[R12] National Institute of Standards and Technology. *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile*, NIST AI 600-1, 2024. https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence

[R13] European Banking Authority. “Guidelines on loan origination and monitoring.” https://www.eba.europa.eu/activities/single-rulebook/regulatory-activities/credit-risk/guidelines-loan-origination-and

[R14] Basel Committee on Banking Supervision. *Principles for the management of credit risk*. Bank for International Settlements. https://www.bis.org/publ/bcbs75.htm

[R15] Office of the Comptroller of the Currency. “Allowances for Credit Losses.” https://www.occ.gov/topics/supervision-and-examination/bank-operations/accounting/allowance-for-credit-losses/index-allowances-for-credit-losses.html

[R16] IFRS Foundation. “IFRS 9 forward-looking information and multiple scenarios.” Educational webcast slides. https://www.ifrs.org/-/media/project/financial-instruments/webcast-july-2016/ifrs9-webcast-july-2016-slides.pdf

[R17] IFRS Foundation. “Measurement of expected credit losses for revolving credit facilities.” Impairment Transition Resource Group paper. https://www.ifrs.org/content/dam/ifrs/meetings/2015/september/itg/impairment-of-financial-instruments/ap3-measurement-of-expected-credit-losses-for-revolving-credit-facilities.pdf

[R18] “South German Credit.” UCI Machine Learning Repository, 2019. https://doi.org/10.24432/C5X89F

[R19] Yeh, I-Cheng. “Default of Credit Card Clients.” UCI Machine Learning Repository, 2009. https://doi.org/10.24432/C55S3H

[R20] Quinlan, J. Ross. “Credit Approval.” UCI Machine Learning Repository. https://doi.org/10.24432/C5FS30

[R21] Zięba, Maciej; Tomczak, Sebastian K.; and Tomczak, Jakub M. “Polish Companies Bankruptcy.” UCI Machine Learning Repository, 2016. https://doi.org/10.24432/C5F600

[R22] Liang, Deron. “Taiwanese Bankruptcy Prediction.” UCI Machine Learning Repository, 2020. https://doi.org/10.24432/C5004D

[R23] Quinlan, J. Ross. “Statlog (Australian Credit Approval).” UCI Machine Learning Repository, 1987. https://doi.org/10.24432/C59012

[R24] Brier, Glenn W. “Verification of Forecasts Expressed in Terms of Probability.” *Monthly Weather Review* 78(1), 1950, pp. 1–3. https://doi.org/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2

[R25] Cox, David R. “Regression Models and Life-Tables.” *Journal of the Royal Statistical Society: Series B* 34(2), 1972, pp. 187–220. https://doi.org/10.1111/j.2517-6161.1972.tb00899.x

[R26] Platt, John. “Probabilistic Outputs for Support Vector Machines and Comparisons to Regularized Likelihood Methods.” In *Advances in Large Margin Classifiers*, 1999.

[R27] Lundberg, Scott M., and Su-In Lee. “A Unified Approach to Interpreting Model Predictions.” *Advances in Neural Information Processing Systems 30*, 2017. https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html

[R28] Breiman, Leo. “Random Forests.” *Machine Learning* 45, 2001, pp. 5–32. https://doi.org/10.1023/A:1010933404324

[R29] Friedman, Jerome H. “Greedy Function Approximation: A Gradient Boosting Machine.” *Annals of Statistics* 29(5), 2001, pp. 1189–1232. https://doi.org/10.1214/aos/1013203451

[R30] Chen, Tianqi, and Carlos Guestrin. “XGBoost: A Scalable Tree Boosting System.” *Proceedings of KDD*, 2016. https://doi.org/10.1145/2939672.2939785

[R31] Kaplan, E. L., and Paul Meier. “Nonparametric Estimation from Incomplete Observations.” *Journal of the American Statistical Association* 53(282), 1958, pp. 457–481. https://doi.org/10.1080/01621459.1958.10501452

[R32] Merton, Robert C. “On the Pricing of Corporate Debt: The Risk Structure of Interest Rates.” *Journal of Finance* 29(2), 1974, pp. 449–470. https://doi.org/10.1111/j.1540-6261.1974.tb03058.x

[R33] Basel Committee on Banking Supervision. “The standardised approach for measuring counterparty credit risk exposures.” Bank for International Settlements. https://www.bis.org/publ/bcbs279.htm

[R34] European Parliament and Council. Regulation (EU) 2016/679, General Data Protection Regulation. https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng

[R35] Creative Commons. “Attribution 4.0 International (CC BY 4.0).” https://creativecommons.org/licenses/by/4.0/

[R36] Python Software Foundation. “Python Documentation.” https://docs.python.org/3/

[R37] pandas development team. “pandas documentation.” https://pandas.pydata.org/docs/

[R38] scikit-learn developers. “scikit-learn User Guide.” https://scikit-learn.org/stable/user_guide.html

[R39] Kottas, Ferdinantos. “High-Dimensional Variable Selection with Applications in Finance.” Doctoral thesis, Maynooth University, 2025. https://mural.maynoothuniversity.ie/id/eprint/20102/

[R40] Gritzalis, Konstantinos; Kottas, Ferdinantos; and co-authors. “Credit Scoring and Explainable Artificial Intelligence.” *Journal of Risk and Financial Management* 18(5), 2025. https://www.mdpi.com/1911-8074/18/5/282

[R41] International Accounting Standards Board. *Post-implementation Review of IFRS 9—Impairment: Project Summary and Feedback Statement*. 4 July 2024. https://www.ifrs.org/projects/completed-projects/2024/post-implementation-review-of-ifrs-9-impairment/

[R42] Financial Accounting Standards Board. *Accounting Standards Update 2025-05—Financial Instruments—Credit Losses (Topic 326): Measurement of Credit Losses for Accounts Receivable and Contract Assets*. July 2025. https://www.fasb.org/Page/Document?pdf=ASU%202025-05.pdf&title=Accounting%20Standards%20Update%202025-05

[R43] European Banking Authority. *Follow-up Report on the Use of Machine Learning for Internal Ratings-Based Models*. 4 August 2023. https://www.eba.europa.eu/publications-and-media/press-releases/eba-publishes-follow-report-use-machine-learning-internal

[R44] Consumer Financial Protection Bureau. *Consumer Financial Protection Circular 2022-03: Adverse action notification requirements in connection with credit decisions based on complex algorithms*. 26 May 2022. https://www.consumerfinance.gov/compliance/circulars/circular-2022-03-adverse-action-notification-requirements-in-connection-with-credit-decisions-based-on-complex-algorithms/

[R45] Consumer Financial Protection Bureau. *Consumer Financial Protection Circular 2023-03: Adverse action notification requirements and the proper use of the CFPB's sample forms provided in Regulation B*. 19 September 2023. https://files.consumerfinance.gov/f/documents/cfpb_adverse_action_notice_circular_2023-09.pdf

[R46] Lessmann, Stefan; Baesens, Bart; Seow, Hsin-Vonn; and Thomas, Lyn C. “Benchmarking state-of-the-art classification algorithms for credit scoring: An update of research.” *European Journal of Operational Research* 247(1), 2015, pp. 124–136. https://doi.org/10.1016/j.ejor.2015.05.030

[R47] Louzada, Francisco; Ara, Anderson; and Fernandes, Guilherme B. “Classification methods applied to credit scoring: Systematic review and overall comparison.” *Surveys in Operations Research and Management Science* 21(2), 2016, pp. 117–134. https://doi.org/10.1016/j.sorms.2016.10.001

[R48] Dastile, Xolani; Çelik, Turgay; and Potsane, Moshe. “Statistical and machine learning models in credit scoring: A systematic literature survey.” *Applied Soft Computing* 91, 2020, 106263. https://doi.org/10.1016/j.asoc.2020.106263

[R49] Kozodoi, Nikita; Jacob, Johannes; and Lessmann, Stefan. “Fairness in Credit Scoring: Assessment, Implementation and Profit Implications.” *European Journal of Operational Research* 297(3), 2022, pp. 1083–1094. https://doi.org/10.1016/j.ejor.2021.06.023

[R50] Bussmann, Niklas; Giudici, Paolo; Marinelli, Dimitri; and Papenbrock, Jochen. “Explainable Machine Learning in Credit Risk Management.” *Computational Economics* 57, 2021, pp. 203–216. https://doi.org/10.1007/s10614-020-10042-0

[R51] Fuster, Andreas; Goldsmith-Pinkham, Paul; Ramadorai, Tarun; and Walther, Ansgar. “Predictably Unequal? The Effects of Machine Learning on Credit Markets.” *Journal of Finance* 77(1), 2022, pp. 5–47. https://doi.org/10.1111/jofi.13090

[R52] Consumer Financial Protection Bureau. “Consumer Complaint Database.” Official data and documentation. https://www.consumerfinance.gov/data-research/consumer-complaints/

[R53] U.S. Small Business Administration. “FOIA—7(a) and 504 Loan Data.” Official programme data and data dictionaries. https://data.sba.gov/dataset/7a-504-foia

[R54] U.S. Securities and Exchange Commission. “EDGAR Application Programming Interfaces.” Official developer documentation. https://www.sec.gov/search-filings/edgar-application-programming-interfaces

[R55] Board of Governors of the Federal Reserve System. “Survey of Consumer Finances.” Official survey data and documentation. https://www.federalreserve.gov/econres/scfindex.htm

[R56] European Banking Authority. “European Data Access Portal and Pillar 3 Data Hub.” Official supervisory-data access pages. https://www.eba.europa.eu/risk-and-data-analysis/data/european-centralised-infrastructure-supervisory-data

[R57] Moro, Sérgio; Cortez, Paulo; and Rita, Paulo. “Bank Marketing.” UCI Machine Learning Repository, 2014. https://doi.org/10.24432/C5K306

[R58] Vaswani, Ashish; Shazeer, Noam; Parmar, Niki; and co-authors. “Attention Is All You Need.” *Advances in Neural Information Processing Systems 30*, 2017. https://proceedings.neurips.cc/paper/7181-attention-is-all-you-need

[R59] Lewis, Patrick; Perez, Ethan; Piktus, Aleksandra; and co-authors. “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.” *Advances in Neural Information Processing Systems 33*, 2020. https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html

[R60] Robertson, Stephen, and Hugo Zaragoza. “The Probabilistic Relevance Framework: BM25 and Beyond.” *Foundations and Trends in Information Retrieval* 3(4), 2009, pp. 333–389. https://doi.org/10.1561/1500000019

[R61] Greshake, Kai; Abdelnabi, Sahar; Mishra, Shailesh; Endres, Christoph; Holz, Thorsten; and Fritz, Mario. “Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection.” *Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security*, 2023. https://doi.org/10.1145/3605764.3623985

[R62] OWASP Foundation. “OWASP Top 10 for Large Language Model Applications.” Official project documentation. https://genai.owasp.org/llm-top-10/

## Appendix K — Master-topic coverage and extension map

The 72-chapter structure uses fewer, larger parts while retaining the specialist topics in the original master outline. The map below prevents an important method from disappearing merely because it is not a chapter title.

| Topic family | Primary chapters | Detailed extension |
|---|---|---|
| cash flows, EL/UL, dependence and dynamic risk | 1–6 | portfolio tail loss in 53; lifetime curves in 37–38 |
| products, fintech, BNPL, embedded finance, ESG and segments | 7–12 | decision economics in 59; safe adaptive limits in 60 |
| expert rules, ratios, ratings and shadow ratings | 8, 10, 12, 15 | master scales and migration in 33 |
| Basel, IRB, IFRS 9 and CECL | 13–17, 43–54 | post-implementation review, latest guidance, calibration, MoC and reconciliation |
| internal, bureau, alternative, API, scraped, public and synthetic data | 19–24 | 36-record source registry; legal gate before any adapter or download |
| missingness, outliers, cleaning and quarantine | 23 | MCAR/MAR/MNAR mechanisms, raw-value preservation, no silent imputation or winsorisation |
| cohorts, roll rates, stages, cure, prepayment and recovery | 4, 11, 24, 37–48 | monthly panels, transition matrices and component reconciliation |
| behavioural and bureau features | 21–24 | max/last DPD, threshold counts, persistence, RFM, trends, utilisation and `CountContractsLast6Months` |
| filter, wrapper, regularised and latent selection | 25, 29 | IV, Fisher, Cramér's V, stepwise limitations, LASSO, ridge, elastic net, PCA and BART |
| scorecards and score presentation | 25–30 | manual/automatic binning, WOE/IV, IRLS, PDO, grades, reasons and characteristic packs |
| classical and advanced classification | 29, 31–36 | LPM, logistic, multinomial, cumulative logit, nomograms, trees, forests, boosting and XGBoost |
| neural and Bayesian methods | 34, 39 | MLP, cross-entropy/back-propagation, self-organising maps, naive Bayes, networks, BART, MCMC and VI |
| survival and competing events | 4, 37–38 | Kaplan–Meier, discrete hazards, Cox, AFT, prepayment and marginal/cumulative PD |
| LGD and EAD | 40–42, 52, 57 | workout ledgers, cure, censoring, downturn, CCF, direct EAD and validation |
| portfolio and counterparty risk | 53–54 | Vasicek, concentration, Credit VaR, Monte Carlo, netting, collateral, CVA, DVA and SA-CCR |
| validation, UAT, governance and monitoring | 55–66 | backtesting, shadow run, release gates, drift layers, incident, rollback and retirement |
| optimisation and reinforcement learning | 59–60 | pricing, RAROC, bandits, dynamic limits and constrained/safe RL |
| NLP, LLMs and workflow automation | 67–72 | extraction, BM25, RAG, structured memoranda, tools, memory, permissions, red teams and capstone |

The crosswalk is a reading map, not a claim that every method deserves production use. Students must still derive the objective, test a transparent implementation, establish dataset suitability and compare complexity with a simpler benchmark.

## Appendix L — Limits of the teaching implementation

The repository and book are educational. They are not legal, accounting, regulatory or investment advice; not a certified capital or impairment system; and not an authorisation to use a variable or dataset in a credit decision. Examples omit institution-specific policies, local law, complete accounting entries, tax, disclosures, security architecture, privacy impact assessment, production resilience and supervisory approvals.

Before real use, qualified owners must establish lawful basis and customer protections; validate source data and definitions; independently validate models and implementation; approve accounting and capital interpretations; secure systems and credentials; complete UAT, change and incident processes; monitor customer and portfolio outcomes; and obtain required governance and regulatory approvals. Agentic examples are recommendation-only and purposely lack customer-decision, retraining, deployment and ledger-posting authority.

The source ledger distinguishes primary authority from explanatory material. Where this book summarises a standard or regulation, the official effective text prevails. Where it shows a formula, the code exposes intermediate values for reconciliation but cannot determine whether the exposure, permission, parameter or jurisdiction is appropriate.

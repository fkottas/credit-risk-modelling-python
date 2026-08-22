# Intelligent Credit Risk Modeling with Python

## From Data Quality and Scorecards to IFRS 9, Basel IRB, Deployment, and Governed Agentic AI

**Dr. Ferdinantos Kottas**

First-edition expanded review manuscript — August 2026

## Preface

Credit-risk education often ends at a fitted probability-of-default model. A bank or fintech, however, cannot stop there. It must prove that the input data are lawful and fit for purpose; define default, observation and performance windows; construct and validate PD, LGD and EAD; translate predictions into scores, grades and decisions; connect risk estimates to IFRS 9, CECL or IRB requirements; implement the approved model without changing it; monitor it after deployment; and manage every material change. Artificial-intelligence agents add another layer: they may help collect evidence, test controls and draft analysis, but they must not quietly acquire authority to approve, decline, price or limit a customer.

This book treats credit risk as an operating system rather than a single algorithm. The seventy-two chapters follow the complete path from uncertain contractual cash flows to retirement of a model. The emphasis is application. Mathematics is derived where the implementation needs it, policies are represented as explicit inputs, and every major method is connected to tested Python code. The repository contains original libraries for scorecard engineering, IFRS 9 calculations, Basel IRB illustrations, validation, monitoring and governed agentic workflows.

The scorecard library deliberately does not call a specialist scorecard package. Manual and automated binning, ChiMerge, monotonic merging, weight of evidence, information value, penalised logistic regression by iteratively reweighted least squares, PDO scaling, bin points, grades, reason codes, stability diagnostics and characteristic-review presentations are implemented in inspectable project code. The teaching order matters: Chapters 1–24 contain standalone functions and miniature fixtures with no `creditriskbook` imports; Chapters 25–54 derive and test model components before promoting them; only the later integration chapters call the reviewed package as a system. The IFRS 9 library separates staging policy, marginal PD curves, scenarios, LGD and EAD adjustments, discounting, overlays and reconciliation. The IRB library separates prescribed risk-weight functions from parameter calibration and governance. The NLP and agent libraries separate extraction, retrieval, structured evidence, proposal, permission, approval and audit; no agent receives customer-decision authority.

## Who should use this book

The primary reader is a credit-risk modeller, validator, data scientist, risk manager, accountant, auditor, model owner or advanced student who knows basic Python and statistics. A reader new to lending can start with Parts I–IV. A scorecard developer can proceed directly to Part V after reading the data-policy chapters. IFRS 9 and IRB practitioners should still study the scorecard and lifetime-PD sections because weaknesses in sample design, calibration and implementation propagate into accounting and capital estimates. Engineers and AI specialists should not skip the regulatory, policy and validation parts: a technically correct service can still be unacceptable if its purpose, authority or evidence chain is wrong.

## How to work through the examples

Every chapter contains six elements: the decision or control problem; the minimum analytical framework; a worked numerical example; Python linked to the repository; policy and failure modes; and a practical lab. Students should run the notebooks, change assumptions, create deliberately defective copies, and explain the effect before changing code. A good submission does not report only AUC or ECL. It records dataset identity and licence, as-of date, sample filters, target construction, model version, policy version, environment, random seed, validation results and limitations.

The code deliberately grows with the reader. A reusable module never appears as magic. The teaching sequence is formula, hand calculation, plain function, boundary tests, comparison across datasets, promotion into the project package, and only then an import from that reviewed package.

| Learning stage | Chapters | Programming and modelling progression |
|---|---:|---|
| Foundations | 1–6 | Scalar arithmetic, tuples, lists, loops and the Python standard library only; every intermediate value is hand-checkable. |
| Small applied cases | 7–12 | Functions and small pandas tables for products, borrower segments, lifecycle states and explicit policy rules. |
| Regulation and data construction | 13–24 | Standalone pandas workflows for capital illustrations, staging, licences, point-in-time joins, target windows, quarantine and behavioural features. |
| Algorithms before promotion | 25–54 | Scorecard, PD, survival, LGD, EAD, IFRS 9 and IRB mathematics are implemented visibly, tested, then moved into the library. |
| Controlled integration | 55–66 | Reviewed components are called together for validation, UAT, deployment, monitoring, change control and audit. |
| NLP and governed agents | 67–72 | Tokenisation and retrieval start from first principles; structured evidence, permissions, workflow tools and red-team gates are added progressively. |

The recommended sequence for a full project is:

1. Select a case and record why the dataset is legally and analytically suitable.
2. Freeze the unit of observation, default definition, observation window, performance window and decision date.
3. Run data-quality controls before exploration or repair.
4. Build a simple benchmark and an interpretable scorecard before complex challengers.
5. Validate discrimination, calibration, stability, economics and group outcomes separately.
6. Construct LGD, EAD, lifetime PD, ECL or IRB capital only from reconciled component data.
7. Execute implementation reconciliation and UAT before deployment.
8. Monitor data, predictions, mature outcomes, calibration, fairness and business effects.
9. Require human approval for material changes and all customer-affecting actions.

## Dataset policy

The repository does not assume that public availability equals permission to republish. Its 41-record dataset registry covers publisher, canonical URL, licence or governing notice, attribution, redistribution status, access conditions, scope and limitations. Eight reviewed UCI credit, approval, bankruptcy and marketing records carry CC BY 4.0 on their official repository pages, but their targets are kept distinct: approval and marketing outcomes are never relabelled as default. Conditional Kaggle examples require the student to download data under their own account after checking current terms; competition files are never bundled. CFPB, SEC, SBA, Federal Reserve, EBA, BLS, World Bank, Eurostat, ECB, FRED and mortgage sources have distinct official notices and analytical boundaries. The classroom document corpus is generated by this project and contains no real applicant or copied document template.

Observed public datasets rarely contain the complete longitudinal information required for workout LGD, revolving EAD, contractual ECL schedules, IRB portfolios or counterparty exposure profiles. The book therefore provides original deterministic generators for those cases. They do not copy or statistically reconstruct a real lender. Their relationships are pedagogical, their provenance is explicit, and their outputs may be deliberately corrupted to teach data-quality controls. Synthetic data make an exercise reproducible; they do not make its conclusion externally valid.

## Legal, accounting and regulatory notice

This manuscript and repository are educational. They are not legal, regulatory, accounting, audit, investment or credit advice, and they are not a validated production system. Basel standards require jurisdictional implementation and supervisory permission. IFRS 9 and CECL require entity-specific accounting judgments, data, controls and governance. Consumer, privacy, discrimination and AI obligations vary by use, product and jurisdiction. The EU AI Act identifies specified creditworthiness and credit-scoring uses as high risk, but classification, timing and obligations must be checked against the applicable legal text and facts. Qualified legal, accounting, compliance, model-risk and business reviewers must approve a real implementation.

No example may be used to approve, decline, price, limit, collect from or otherwise affect a real person. The agent examples produce proposals and evidence for authorised humans. The policy engine explicitly denies customer decisions, automatic deployment, automatic retraining, alteration of evidence and accounting postings.

## Notation and conventions

The target convention is $Y=1$ for default or the adverse event and $Y=0$ for non-default. Probability of default is PD, loss given default is LGD, and exposure at default is EAD. Expected loss for a compatible horizon and conditioning basis is

\[
EL = PD \times LGD \times EAD.
\]

For scorecards, weight of evidence is defined as

\[
WOE_j = \log\left(\frac{P(X\in j\mid Y=0)}{P(X\in j\mid Y=1)}\right).
\]

Consequently a positive WOE denotes a bin with relatively more non-defaults under this convention. Score is constructed so that a higher value means lower estimated risk. Code uses `pd` for pandas only in import statements; variables containing probability of default use names such as `pd_12m` or `pd_values`.

## About the author

Dr. Ferdinantos Kottas holds a PhD in Finance from Maynooth University. His published research includes work in financial risk, machine learning and finance. His broader professional and research profile combines credit-risk modelling, empirical finance, applied mathematics, economics, data science and business analytics. Public biographical statements in this manuscript are limited to information that can be supported by university, publisher or author-controlled sources; detailed employment claims should be checked against the author’s current curriculum vitae.

## Repository map

| Path | Purpose |
|---|---|
| `book/full_manuscript/` | Expanded seventy-two-chapter source manuscript |
| `src/creditriskbook/scorecard/` | Original binning, WOE, IRLS, scaling, diagnostics and reports |
| `src/creditriskbook/ifrs9/` | Staging, curves, multi-scenario ECL, overlays and provision matrices |
| `src/creditriskbook/irb/` | Risk-weight functions, calibration, MoC and validation |
| `src/creditriskbook/agents/` | Evidence, permissions, specialists, orchestration and audit |
| `src/creditriskbook/data/` | Reviewed adapters, synthetic cases and quality controls |
| `notebooks/` | Executable labs generated from reviewed source cells |
| `tests/` | Offline, live-source and integration tests |
| `data/dataset_registry.yml` | Provenance, licence, redistribution and limitations register |

> The main rule of the book is simple: prediction is only one component of a controlled credit-risk system. A model is not ready because it runs; it is ready only when its purpose, evidence, implementation, limits, approvals and monitoring are all demonstrable.

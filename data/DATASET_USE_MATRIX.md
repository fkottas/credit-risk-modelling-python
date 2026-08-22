# Dataset Use Matrix

Last reviewed: 22 August 2026.

The repository distinguishes a catalogue entry from an executable study case. The
dataset registry contains 41 source records, but that number must not be interpreted
as 41 interchangeable modelling datasets. At this release there are 20 executable
interfaces: ten common tabular loader keys, eight additional project-generated
specialist cases, one World Development Indicators API adapter and one validator for
a user-downloaded CFPB complaint extract.

## Common tabular loader

| Key | Outcome and observation | Permitted teaching use | Important restriction | Execution status |
|---|---|---|---|---|
| `synthetic_retail` | generated 12-month default per application | introductory PD, quality, scorecards, ML, deployment | mechanisms are illustrative, not lender estimates | generated and tested |
| `uci_south_german` | credit-risk outcome per historic applicant | small PD and scorecard exercises | 1973–1975, oversampled bad cases, no dates | checksum-verified adapter tested |
| `uci_statlog_german` | legacy credit-risk outcome per historic applicant | source-comparison and data-documentation failure | UCI reports coding-information errors; not the preferred benchmark | checksum-verified adapter tested |
| `uci_taiwan_credit_card` | next-month card default per customer | behavioural PD, calibration, ML | 2005 sample, no out-of-time split | checksum-verified adapter tested |
| `uci_credit_approval` | application approval | missing values, mixed types, selection discussion | approval is not default | checksum-verified adapter tested |
| `uci_australian_credit_approval` | application approval | mixed-type pipelines and source preprocessing | approval is not default; source already replaced missing values | checksum-verified adapter tested |
| `uci_polish_bankruptcy` | bankruptcy within one year per company | rare-event corporate modelling | bankruptcy is not regulatory default; no entity dates | checksum-verified adapter tested |
| `uci_taiwan_bankruptcy` | bankruptcy per company | corporate failure and imbalance | bankruptcy is not regulatory default; no row dates | checksum-verified adapter tested |
| `uci_bank_marketing` | term-deposit subscription after contact | leakage, temporal order and non-credit classification | not a credit outcome; post-call duration is forbidden pre-call | checksum-verified adapter tested |
| `kaggle_credit_risk` | dataset-owner credit-risk label per row | optional schema switching and benchmarking | student obtains file; current dataset-specific terms must be reviewed | local-file adapter tested; raw file not bundled |

All eight UCI records above are published under CC BY 4.0 on their current UCI
dataset pages. The repository records their DOI, attribution, source URL and archive
checksum. Raw UCI files are downloaded into an ignored local cache rather than copied
into the repository.

## Project-generated specialist cases

| Key | Tables or unit | Principal chapters | What the case cannot establish |
|---|---|---|---|
| `synthetic_behavioral_history` | applications, contracts, monthly performance, bureau enquiries | relational data, point-in-time features, DPD, utilisation, recent contracts | real behavioural effect sizes or production default policy |
| `synthetic_revolving` | revolving facility at reference and default dates | CCF, EAD, limit management | real drawdown behaviour |
| `synthetic_recovery` | default and recovery cash-flow records | workout LGD, cure, discounting, incomplete workouts | legal or collateral recovery performance |
| `synthetic_ifrs9_schedule` | account-period-scenario schedule | staging, lifetime PD, ECL, overlays | an accounting conclusion or institution-specific policy |
| `synthetic_corporate_irb` | obligor/facility parameter rows | IRB functions, calibration, concentration | approved regulatory estimates |
| `synthetic_counterparty_profiles` | counterparty exposure paths | PFE, netting, CVA | market-calibrated derivatives exposure |
| `synthetic_credit_documents` | applications, documents, expected facts, policy text | NLP, retrieval, structured memoranda, prompt injection | production document diversity or autonomous lending authority |
| `synthetic_fraud_transactions` | payment transactions | imbalance, anomaly and fraud exercises | payment-network fraud prevalence; fraud is not default |

The generator seed, code version and output hash identify every generated release.
Deliberate data defects are added to a copy, never to the source table. The defect
manifest records the row, field, source value, altered value and intended detection
rule.

## Public macroeconomic and text sources

| Interface | Access pattern | Use | Restriction |
|---|---|---|---|
| `load_world_bank_wdi` | official World Bank Indicators API | macroeconomic history, satellite-model and stress exercises | country-level revised indicators are not borrower outcomes or forecasts |
| `load_cfpb_complaint_extract` | validates a user-downloaded official CSV/ZIP extract | product taxonomy, complaint trends and NLP | complaints are not representative; narratives are excluded by default and are not underwriting labels |

The World Development Indicators dataset record is CC BY 4.0. The CFPB states that
published complaint data are freely available to use, analyse and build on; its page
also states that complaints are not a statistical sample and that narratives are not
verified by the Bureau. The full complaint archive is not bundled because it is large,
changes frequently and contains public narratives that warrant additional privacy
review.

## Conditional and reference-only records

The remainder of `dataset_registry.yml` is intentionally not presented as executed
loan-performance data. Some records support only macroeconomic, affordability,
application-decision, disclosure or regulatory-data exercises. Others require a
student account, a provider workflow, an institution-specific agreement or a fresh
licence review. A source becomes executable only after its adapter, target meaning,
licence treatment, checksum or release identifier, limitations and tests have been
completed.

Fannie Mae and Freddie Mac loan-level performance files are excluded by project
policy in this edition: no raw files, downloader or derived teaching case is supplied.
Mortgage performance exercises use an independently generated panel. Competition
datasets without sufficiently clear reuse permission are likewise reference-only or
excluded, even when a mirror is easy to find.

Transforming a restricted real dataset does not automatically create unrestricted
synthetic data. A derivative may remain subject to the source terms and may reproduce
individual records. New study cases derived from an external source therefore require
the original URL, exact licence and permission for adaptation. Where that permission
is absent or ambiguous, the project creates an independent generator from documented
domain assumptions rather than fitting or copying the restricted records.

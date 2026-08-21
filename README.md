# Intelligent Credit Risk Modeling with Python

**From Data Quality and Scorecards to IFRS 9, Basel IRB, Deployment, and Governed Agentic AI.**

Author: **Dr. Ferdinantos Kottas**

> First-edition review build. It is educational material, not a production lending system or legal, regulatory, accounting, or investment advice.

## What makes this project different

The 72-chapter project follows a credit model from the first data contract to retirement. It does not stop after fitting a classifier. Every major case study connects data provenance, data-quality controls, sample construction, modelling, calibration, decision economics, validation, deployment, monitoring, governance, and human approval.

The examples deliberately distinguish:

- an educational benchmark from evidence suitable for a real lending policy;
- predictive performance from calibrated probability of default;
- an IFRS 9 estimate from an IRB capital parameter;
- a model recommendation from a credit decision;
- a reproducible synthetic dataset from a redistributed third-party dataset;
- agent assistance from autonomous authority.

The teaching sequence is also deliberate. Each substantial method is introduced as intuition and mathematics, implemented in transparent scratch Python, checked against hand calculations and edge cases, and only then promoted into `src/creditriskbook/`. Later chapters import the tested library. The package therefore emerges from the course; it is not a black box presented before the student sees the calculation.

## Dataset switching

Students are not locked into one dataset. The legal and technical registry contains 36 source records. The common executable interface supports these principal PD/public modes:

1. `synthetic_retail` - generated entirely by this repository and safe for unrestricted exercises;
2. `uci_south_german` - a corrected, small CC BY 4.0 benchmark;
3. `uci_taiwan_credit_card` - a larger CC BY 4.0 behavioural-credit benchmark;
4. `uci_credit_approval` - an anonymised CC BY 4.0 approval case used only for missing-data and decision-pipeline labs;
5. `uci_polish_bankruptcy` - a CC BY 4.0 low-event corporate-failure case;
6. `uci_taiwan_bankruptcy` - a second CC BY 4.0 corporate-failure benchmark;
7. `kaggle_credit_risk` - a conditional Kaggle teaching case downloaded by the student and never bundled here; current dataset-specific terms must be checked.

Eight original deterministic case generators provide lifecycle tables that public classification datasets rarely contain:

- `synthetic_behavioral_history` for applications, contracts, monthly DPD/payment histories and bureau enquiries;

- `synthetic_revolving` for CCF and EAD;
- `synthetic_recovery` for workout LGD and cure;
- `synthetic_ifrs9_schedule` for staging and cash-flow-period ECL;
- `synthetic_corporate_irb` for grades, calibration and RWA;
- `synthetic_counterparty_profiles` for exposure profiles and introductory CVA.
- `synthetic_credit_documents` for field extraction, BM25 retrieval, structured evidence memoranda and agent red teams.

The registry also covers official HMDA, CFPB complaint, SBA 7(a)/504, SEC EDGAR, Federal Reserve SCF, EBA Pillar 3, FHFA, World Bank and FRED sources; provider-controlled mortgage data; and conditional Kaggle competition cases. A registry entry is not blanket approval: each exercise applies its recorded scope, current notice, access method and redistribution decision.

Additional datasets will be added only after their provenance, licence, permitted use, attribution, and redistribution terms are recorded in [`data/dataset_registry.yml`](data/dataset_registry.yml). A Kaggle mirror never replaces the original publisher's licence.

## Quick start

The foundation release uses Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
python -m unittest discover -s tests -v
python tools/validate_notebooks.py
python tools/validate_manuscript.py
python examples/end_to_end.py --dataset synthetic_retail
```

The end-to-end example:

1. generates or loads a dataset through the registry;
2. injects reproducible data defects for teaching;
3. runs rule-level data-quality assessment;
4. quarantines invalid observations without imputation or winsorisation;
5. builds an out-of-time PD model where dates exist;
6. evaluates discrimination and probability accuracy;
7. creates a simplified educational ECL calculation;
8. evaluates drift and governed agent recommendations;
9. writes auditable JSON artefacts locally.

Generated datasets, fitted models, and reports are excluded from Git.

## Repository map

```text
book/full_manuscript/    expanded 72-chapter manuscript and applied appendices
data/                    dataset registry and download instructions (no raw data)
examples/                runnable chapter and end-to-end examples
references/              source policy, regulatory sources, and evidence reviews
src/creditriskbook/      reusable Python package
tests/                   deterministic unit and integration tests
.github/workflows/       continuous integration
```

The earlier top-level utilities in `src/*.py`, dataset generators in `data/generators/`, configuration, and notebooks remain available. They are preserved during the migration to the tested package structure and will be reviewed and integrated case by case rather than deleted.

The behavioural build is available in `creditriskbook.data.behavioral`, auditable cleaning and quarantine in `creditriskbook.data.cleaning`, and point-in-time features in `creditriskbook.features.behavioral`. The feature library includes `max_dpd`, `last_dpd`, DPD threshold counts, recency, persistence, utilisation and payment trends, over-limit months, active balances, bureau enquiries, and `count_contracts_last_6m` (business name `CountContractsLast6Months`).

See [`book/BOOK_PLAN.md`](book/BOOK_PLAN.md) and [`book/structure.json`](book/structure.json) for the complete 72-chapter structure.

## Legal and evidence policy

- No third-party dataset is committed unless redistribution is explicitly permitted and useful.
- Downloaded datasets retain their original licence and attribution requirements.
- Derived teaching defects are created locally by deterministic code and are documented as modifications.
- Copyrighted books, consulting guides, figures, and code are not copied. They may be paraphrased and cited within normal scholarly practice.
- Every empirical table must identify its dataset version, access date, transformation, sample filters, and code entry point.
- Sources with unclear chronology, data, methods, or provenance are labelled as conceptual or excluded from evidentiary claims.

See [`references/SOURCE_POLICY.md`](references/SOURCE_POLICY.md), [`COPYRIGHT.md`](COPYRIGHT.md), and [`DISCLAIMER.md`](DISCLAIMER.md).

## Current status

The expanded teaching edition contains 72 analytical chapters, 72 worked cases, 72 mathematics-to-code laboratories, 24 standalone early-chapter scripts, 16 executed notebooks, a 400+ page Word manuscript with native equations and labelled Python/output panels, original teaching figures, a 36-record lawful-use dataset registry, and original scorecard, IFRS 9, IRB, NLP and governed-agent packages. The manuscript remains subject to technical, regulatory, legal, accounting, copy-editing, and independent model review before publication or real use.

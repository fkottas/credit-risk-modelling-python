# Applied Credit Risk with Python

**An application-first book and tested codebase for data quality, credit scoring, Basel IRB, IFRS 9, CECL, deployment, monitoring, and governed agentic AI.**

Author: **Dr. Ferdinantos Kottas**

> Work in progress. The repository is being developed chapter by chapter. It is educational material, not a production lending system or legal, regulatory, accounting, or investment advice.

## What makes this project different

The project follows a credit model from the first data contract to retirement. It does not stop after fitting a classifier. Every major case study connects data provenance, data-quality controls, sample construction, modelling, calibration, decision economics, validation, deployment, monitoring, governance, and human approval.

The examples deliberately distinguish:

- an educational benchmark from evidence suitable for a real lending policy;
- predictive performance from calibrated probability of default;
- an IFRS 9 estimate from an IRB capital parameter;
- a model recommendation from a credit decision;
- a reproducible synthetic dataset from a redistributed third-party dataset;
- agent assistance from autonomous authority.

## Dataset switching

Students are not locked into one dataset. A common dataset interface supports four modes:

1. `synthetic_retail` - generated entirely by this repository and safe for unrestricted exercises;
2. `uci_south_german` - a corrected, small CC BY 4.0 benchmark;
3. `uci_taiwan_credit_card` - a larger CC BY 4.0 behavioural-credit benchmark;
4. `kaggle_credit_risk` - a CC0 Kaggle teaching dataset downloaded by the student and never bundled here.

Additional datasets will be added only after their provenance, licence, permitted use, attribution, and redistribution terms are recorded in [`data/dataset_registry.yml`](data/dataset_registry.yml). A Kaggle mirror never replaces the original publisher's licence.

## Quick start

The foundation release uses Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
python -m unittest discover -s tests -v
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
book/                    manuscript plan, standards, and chapters
data/                    dataset registry and download instructions (no raw data)
examples/                runnable chapter and end-to-end examples
references/              source policy, regulatory sources, and evidence reviews
src/creditriskbook/      reusable Python package
tests/                   deterministic unit and integration tests
.github/workflows/       continuous integration
```

The earlier top-level utilities in `src/*.py`, dataset generators in `data/generators/`, configuration, and notebooks remain available. They are preserved during the migration to the tested package structure and will be reviewed and integrated case by case rather than deleted.

See [`book/BOOK_PLAN.md`](book/BOOK_PLAN.md) for the expanded book structure.

## Legal and evidence policy

- No third-party dataset is committed unless redistribution is explicitly permitted and useful.
- Downloaded datasets retain their original licence and attribution requirements.
- Derived teaching defects are created locally by deterministic code and are documented as modifications.
- Copyrighted books, consulting guides, figures, and code are not copied. They may be paraphrased and cited within normal scholarly practice.
- Every empirical table must identify its dataset version, access date, transformation, sample filters, and code entry point.
- Sources with unclear chronology, data, methods, or provenance are labelled as conceptual or excluded from evidentiary claims.

See [`references/SOURCE_POLICY.md`](references/SOURCE_POLICY.md), [`COPYRIGHT.md`](COPYRIGHT.md), and [`DISCLAIMER.md`](DISCLAIMER.md).

## Current status

This first foundation establishes the legal, reproducibility, testing, and software architecture. It is not presented as the completed book. Chapters and regulated-use examples will be added through reviewed pull requests, with tests required before merge.

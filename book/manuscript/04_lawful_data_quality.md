# Chapter 4 — Lawful Data, Architecture and Quality Engineering

## Permission is part of reproducibility

A dataset is not reusable merely because it can be downloaded. The repository acceptance gate requires an identifiable publisher, authoritative landing page, explicit licence or terms, compatible intended use, attribution and enough documentation to define the target. An aggregator or Kaggle mirror does not erase original terms. Competition files are never committed by default.

The primary open teaching sources in this edition are UCI datasets licensed CC BY 4.0: South German Credit, Default of Credit Card Clients, Credit Approval, Polish Companies Bankruptcy and Taiwanese Bankruptcy Prediction [R10–R14]. The first two support retail PD-style cases. Credit Approval has an approval outcome, not default, and is used for missing-data and selection discussion. The bankruptcy datasets support corporate-failure and low-event exercises; bankruptcy is not automatically a Basel default.

The Kaggle credit-risk teaching file is an optional student download. Its dataset page displayed CC0 during the 2 August 2026 review, but the project still does not bundle it; release review must recheck metadata and provenance. Home Credit and Give Me Some Credit competition files remain conditional under competition rules. LendingClub mirrors are excluded until source-specific rights are documented.

CFPB/FFIEC HMDA data are privacy-modified public mortgage application and origination records [R15]. They support lending-pattern, decision and fair-lending analysis. They do not contain subsequent default performance and must not be used as if they did. World Bank WDI and FRED can support macro scenarios only after indicator- or series-level terms and vintage controls are recorded.

## Dataset contract

Every adapter returns a `DatasetBundle` with the frame, target, feature roles, protected attributes, identifier, observation date, split strategy, source, licence, attribution, checksum, limitations and quality specification. Downstream code does not assume one column naming convention.

```python
from creditriskbook.data.datasets import load_dataset

bundle = load_dataset("uci_south_german")
print(bundle.attribution)
print(bundle.source_sha256)
X = bundle.frame[list(bundle.model_features)]
y = bundle.frame[bundle.target]
```

Downloads use fixed publisher URLs and verified archive hashes. If a publisher changes the file, the loader fails rather than accepting a silent revision. The right response is to inspect the new file, schema, licence and documentation, then intentionally update the registry, checksum and tests.

## Layered architecture

Keep raw, conformed, feature, model and reporting layers separate. Raw data are immutable and access-controlled. Conformed data standardise identifiers, time zones, units and codes. Point-in-time feature logic reads only information available by the observation cut-off. Model tables freeze sample and target versions. Reports consume run artefacts rather than re-querying live sources.

Each run manifest should include:

- repository commit and environment versions;
- dataset key, source file hash and extraction time;
- observation and performance windows;
- cohort, product and exclusion counts;
- feature definition version and availability lag;
- target definition version;
- split and random seed;
- fitted model and calibration hashes;
- report and approval identifiers.

This turns “I reran the notebook” into evidence.

## Quality dimensions and rules

Completeness asks whether required values exist. Uniqueness protects keys. Validity checks ranges and code sets. Consistency checks relationships such as balance no greater than limit. Timeliness compares data availability with the decision. Accuracy needs reconciliation to an authoritative source, not only plausible values. Representativeness compares the sample with the target population. Lineage proves origin and transformation.

A quality rule needs a name, field or population, dimension, expression, severity, tolerance, owner and response. “Income must be positive” is incomplete without a policy for zero, currency, business applicants, missing verification and historical corrections.

Notebook 01 injects deterministic defects: duplicates, missing model fields, out-of-range values, future dates and a target-derived leakage field. The quality report marks critical failure and the quarantine function separates invalid rows without silently imputing them. After quarantine the same gates run again.

```python
dirty = inject_teaching_defects(bundle, seed=102, rate=0.02)
before = assess_quality(bundle, dirty)
clean, quarantine = quarantine_invalid_rows(bundle, dirty)
after = assess_quality(bundle, clean)
assert before.critical_failure and not after.critical_failure
```

Quarantine is not always the production answer. A duplicate key may require upstream correction; removing one row can discard the true observation. An outlier may be a high-value customer, not an error. The lab teaches control flow, while the policy decides remediation.

## Missingness and outliers

MCAR, MAR and MNAR are mechanisms, not labels inferred from a missing-value chart. Bureau absence for a thin-file customer is informative and policy-driven. Income missing because verification failed differs from a random interface interruption. Imputation should preserve a missing indicator when absence is meaningful and must be fitted on training data only.

Outlier treatment distinguishes impossible, erroneous, rare but valid and influential observations. Hard validity rules handle impossibility. Winsorisation can stabilise a model but changes interpretation and may hide a unit error. Scorecard bins can isolate tails transparently. Always compare raw and treated distributions and preserve remediation counts.

## Sampling, selection and leakage

Approval policy determines which outcomes become visible. Take-up and attrition add selection. Oversampling events can help estimation but requires weights or calibration back to the target population. The South German data itself reports historical oversampling and transformed amounts; this limitation belongs beside every metric.

Leakage can be direct, temporal, target-derived, policy-induced or cross-validation leakage. Fit imputation, binning, encoding and feature selection inside each training fold. Freeze macros by release vintage. Do not use final recovery status to predict default. Do not let the same customer appear in train and test when repeated records create dependence.

## Chapter deliverable

Run notebook 01 with three seeds. Extend the defect injector with a currency-unit error and an as-of join that chooses a future record. Add rules, severities and tests. Then switch notebook 08 to every reviewed UCI adapter and write a one-paragraph statement explaining why its target is—or is not—a PD target.


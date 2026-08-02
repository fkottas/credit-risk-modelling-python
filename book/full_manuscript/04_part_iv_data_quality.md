# Chapter 19 — Internal, Bureau, Alternative, Public, and Synthetic Data

## Source choice is part of model design

Internal data describe the institution’s products, decisions, balances, payments, collections and recoveries. Bureau data broaden the view across lenders but introduce matching, latency, coverage and contractual restrictions. Transaction and open-banking data can capture cash-flow behaviour but require consent, minimisation and stable categorisation. Telco, device, location and other alternative data may increase coverage while raising privacy, proxy and explainability risk.

Public data are valuable for teaching algorithms, testing infrastructure and benchmarking broad behaviour. They rarely represent the institution’s current applicants or contractual definitions. A dataset with an adverse outcome is not automatically a PD dataset. UCI Credit Approval predicts approval; corporate datasets predict bankruptcy; HMDA public data describe mortgage applications and originations, not subsequent default.

Synthetic data are appropriate when public evidence lacks recovery ledgers, revolving limit history or contractual ECL paths. Generation must be original, documented and reproducible. A synthetic dataset should not be described as anonymised real data unless that is factually and legally established.

```python
from creditriskbook.data import available_case_datasets, load_case_dataset
from creditriskbook.data.datasets import available_datasets

print("Public/application adapters:", available_datasets())
print("Original case generators:", available_case_datasets())
case = load_case_dataset("synthetic_recovery", n_rows=200, seed=191)
print(case.unit_of_observation, case.licence, case.source_sha256)
```

## Source assessment

For every field record owner, original purpose, collection process, effective time, update frequency, coverage, permission, quality checks and known changes. Assess whether the source is observational or selected by a prior decision. Outcomes among accepted loans do not reveal rejected-loan performance.

**Lab.** Create a source inventory for an application scorecard with application, bureau, fraud and outcome systems. Mark fields unavailable at decision time and data requiring additional legal review.

# Chapter 20 — Data Licences, Attribution, Privacy, and Reproducibility

## Public does not mean unrestricted

A file visible on the internet may be copyrighted, contractually restricted, privacy-sensitive or incorrectly mirrored. A Kaggle page may display a licence, but competition rules, account terms and original-source rights still matter. An aggregator’s metadata cannot override the publisher’s licence.

The project registry uses statuses such as approved, approved with scope limit, conditional per series and excluded pending review. UCI datasets used in live adapters are attributed and downloaded from authoritative publisher archives. Checksums prevent an upstream file change from entering a run silently. Kaggle files are not committed even where a page displays CC0; students obtain them directly and metadata are rechecked for each release.

```python
from creditriskbook.data.datasets import load_dataset

bundle = load_dataset("uci_south_german", cache_dir="data/raw")
print({
    "source": bundle.source_url,
    "licence": bundle.licence,
    "attribution": bundle.attribution,
    "sha256": bundle.source_sha256,
    "limitations": bundle.limitations,
})
```

A reproducible empirical result records dataset version or hash, access date, filters, transformations, split, code commit, environment and seed. For revisable macro series, store release vintage when permitted. Do not embed secrets or personal data in notebooks, logs or model artifacts.

## Release policy

Before publication, legal or authorised reviewers should confirm third-party data and figures. Source code inspired by another repository needs licence-compatible attribution and independent review. This project does not copy the uploaded commercial book or external credit-risk codebase; it uses original code and cites concepts.

**Lab.** Review three candidate Kaggle datasets. Trace each to the original publisher, compare licences and decide whether code-only download, redistribution or exclusion is appropriate.

# Chapter 21 — Data Contracts, Lineage, and Point-in-Time Joins

## A schema is not a contract

A data contract includes unit of observation, key, field type, allowed domain, nullability, semantic definition, currency, timezone, effective timestamp, freshness, source, owner, privacy class and quality thresholds. Model features require availability timing and transformation lineage. Target fields require observation and outcome windows.

A point-in-time join selects information known by the decision timestamp. Joining the latest bureau record, future financial statement or revised macro value creates temporal leakage even if the column name looks historical. Slowly changing dimensions require valid-from and valid-to intervals. Events arriving late need event time and processing time.

```python
import pandas as pd

applications = pd.DataFrame({
    "account_id": ["A", "B"],
    "decision_time": pd.to_datetime(["2025-01-10", "2025-01-12"]),
}).sort_values("decision_time")
bureau = pd.DataFrame({
    "account_id": ["A", "A", "B"],
    "bureau_time": pd.to_datetime(["2024-12-01", "2025-02-01", "2025-01-01"]),
    "utilisation": [0.30, 0.80, 0.45],
}).sort_values("bureau_time")

joined = pd.merge_asof(
    applications,
    bureau,
    left_on="decision_time",
    right_on="bureau_time",
    by="account_id",
    direction="backward",
)
print(joined)
```

The A record dated February is correctly excluded from the January decision. Production joins also need maximum staleness, duplicate resolution and source-priority policy.

## Lineage evidence

Store source column, transformation code, parameters, intermediate fields and consumers. Hash input and output manifests. Reconcile row counts and monetary totals before and after joins. A lineage diagram without executable tests is incomplete.

**Lab.** Create a deliberately leaky join and a point-in-time join. Measure the performance difference and explain why the higher result is invalid.

# Chapter 22 — Sampling, Observation Windows, and Target Construction

## Define the analytic base table

The analytic base table should have one clearly defined row per observation. Application models often use one row per application. Behavioural models may use one account-month, creating repeated observations and dependence. Corporate ratings may use one obligor financial statement date. Recovery models may need account-level and cash-flow-level tables.

An observation window collects predictors; a performance window observes outcome. A buffer may be needed for reporting lag. Exclusions such as fraud, deceased customers, acquired portfolios, policy declines, incomplete outcomes and existing defaults must be justified. Excluding difficult cases after seeing results biases the model.

Case-control sampling can improve computation but changes event prevalence. Logistic slopes may remain useful under conditions, while intercept and probabilities require calibration to the target population. Oversampling must not leak across train and test. Weights and sampling probabilities belong in the manifest.

```python
from creditriskbook.data.datasets import load_dataset
from creditriskbook.models import split_dataset

bundle = load_dataset("synthetic_retail", n_rows=6_000, seed=221)
train, test = split_dataset(bundle, bundle.frame, test_size=0.25)
print(train[bundle.date_column].max(), test[bundle.date_column].min())
print(train[bundle.target].mean(), test[bundle.target].mean())
```

The temporal split is a minimal control, not a complete validation design. Labels near the extraction date must be mature.

## Target governance

Version the default definition and store trigger reason. Rebuild labels from raw events under tests. Review label noise, cure, multiple defaults and competing closure. Ensure target fields never enter model features.

**Lab.** Construct twelve-month default targets for monthly snapshots. Prevent one account’s future outcome from leaking into earlier or test records. Compare row-level and customer-level splits.

# Chapter 23 — Data Quality Dimensions, Rules, and Quarantine

## Quality must be actionable

Completeness asks whether required values are present. Validity checks domain and range. Uniqueness checks keys. Consistency compares related fields. Accuracy compares trusted sources or recomputations. Timeliness checks freshness. Integrity checks relationships. Lineage checks provenance and temporal availability. Representativeness asks whether data match the intended population.

A useful quality rule specifies dimension, field, logic, population, threshold, severity, owner, action and evidence. Critical failures halt or quarantine a run; warnings may proceed under approved review. Automatic imputation can hide source failures, so the baseline examples quarantine incomplete model rows and report them rather than silently filling them.

```python
from creditriskbook.data.datasets import load_dataset
from creditriskbook.data.quality import (
    assess_quality,
    inject_teaching_defects,
    quarantine_invalid_rows,
)

bundle = load_dataset("synthetic_retail", n_rows=2_000, seed=231)
dirty = inject_teaching_defects(bundle, seed=232, rate=0.02)
before = assess_quality(bundle, dirty)
clean, quarantine = quarantine_invalid_rows(bundle, dirty)
after = assess_quality(bundle, clean)
print(before.failed_rules, len(quarantine), after.critical_failure)
```

The teaching defect copy includes duplicates, invalid values, missing model fields, future dates and a post-outcome column. Source data remain unchanged.

## Issue management

Record failing rows, not only percentages. Link exceptions to tickets and owners. Re-run controls after repair. Monitor quality trends by source and release. A tolerated exception needs expiry and compensating control.

**Lab.** Add contradictory balance and limit fields. Decide whether to repair from an authoritative source, quarantine, cap only for modelling, or halt. Preserve raw and adjusted values.

# Chapter 24 — Missingness, Outliers, Leakage, and Selection Bias

## Missing is information about a process

MCAR, MAR and MNAR are analytical descriptions, not directly observable labels. A missing income can arise from optional application flow, system failure, self-employment, product policy or deliberate non-disclosure. A generic median changes distribution and may convert a process signal into false precision. The book’s default is to diagnose and quarantine or model missingness explicitly under policy rather than impute automatically.

Outliers may be valid high-income borrowers, currency errors, unit errors, stale limits or fraud. Winsorisation changes values and can distort scorecard meaning. Retain raw values; create an approved modelling transformation only after source investigation and impact analysis.

Leakage can be direct, temporal, group, preprocessing or target-derived. A variable such as recovery amount is obvious leakage for application PD. A bureau record updated after decision is temporal leakage. Fitting bins or scalers before splitting leaks test distribution. Repeated borrowers across folds create group leakage.

Selection bias occurs because performance is observed mainly for accepted cases and because customers choose whether to take an offer. Reject inference methods rely on assumptions that cannot be verified from rejected outcomes alone.

```python
from creditriskbook.data.datasets import load_dataset

approval = load_dataset("uci_credit_approval", cache_dir="data/raw")
print(approval.target, approval.frame.isna().mean().sort_values(ascending=False).head())
print(approval.limitations)
```

The approval dataset is useful for missing-data pipelines but cannot validate default reject inference.

## Review policy

Require a feature-availability declaration. Fit preprocessing inside training folds. Test duplicates across partitions. Compare accepted applicants with the full application population on variables observed for both. Label causal claims separately from predictions.

**Lab.** Inject a target-derived score and a future delinquency field. Fit an intentionally leaky model and then remove the fields. Report the false performance gain and the control that should catch it.

> Part IV makes data provenance, timing and quality first-class model components. The strongest algorithm cannot repair an invalid target or unlawful source.

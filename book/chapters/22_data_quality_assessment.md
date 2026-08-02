# Chapter 22 - Data-quality assessment before modelling

## Quality is fitness for a defined use

The same field can be adequate for portfolio reporting and unacceptable for model development. A monthly balance aggregated after month-end might reconcile to finance but leak future information into an application model. Data quality therefore begins with the decision, as-of date, unit, target, and lineage.

The initial controls cover six dimensions:

| Dimension | Question | Example control |
|---|---|---|
| Completeness | Is required information present? | No missing target or baseline model field |
| Uniqueness | Does one identifier represent one unit? | Application ID is unique |
| Validity | Does the value satisfy its domain? | Utilisation lies between 0 and 1 |
| Consistency | Do related values agree? | Employment length cannot exceed working-age history |
| Timeliness | Was the value available by the as-of date? | Application date is not in the future |
| Lineage | Can the value's origin and time be demonstrated? | Post-outcome delinquency is excluded from origination features |

A rule records its dimension, severity, evaluated population, failure count, threshold, and explanation. A critical rule can stop a run; a warning can trigger investigation without pretending all exceptions are equivalent.

## Reproducible defects

Run the synthetic workflow with the default defect injection:

```bash
creditrisk-demo --dataset synthetic_retail --rows 5000 --seed 42
```

The code creates a copy and injects defects using seed 43. It does not modify the source `DatasetBundle`. `assess_quality` reports the failures, and `quarantine_invalid_rows` separates invalid records.

The baseline does not impute or winsorise. This is a deliberate teaching choice: silently replacing missing values or clipping extremes can hide a data-generation problem and change calibration. Quarantine is not automatically unbiased either. The report therefore records how many observations were excluded, and later chapters test whether exclusion changes the population.

## Why passing rules is not enough

Schema validity cannot establish economic meaning. A value of 0.40 can be a valid ratio while still representing the wrong month, a stale bureau extract, or a denominator defined differently between systems. Robust assessment adds:

- reconciliation to system totals;
- cross-field and cross-table checks;
- temporal availability tests;
- stability by source and segment;
- source-to-target lineage;
- sampling and representativeness analysis;
- investigation of manual overrides and late corrections.

## Leakage as a data-quality failure

Leakage is often treated as a modelling mistake, but it is also a lineage failure. For an application PD model, `days_past_due_after_12m`, recovery cash flows, collection treatment, and charge-off information occur after the decision. Their predictive strength is precisely why an automated feature search can select them.

The synthetic dataset contains post-outcome fields for later LGD and ECL demonstrations, but the model contract excludes them. The defect injector adds `target_derived_score`; the report flags it as a post-outcome teaching column. Tests verify that forbidden fields never enter `model_features`.

## A controlled disposition process

Every failed record or rule needs a disposition rather than an undocumented fix:

1. **correct at source** when the source is demonstrably wrong;
2. **re-extract** when the snapshot or join was wrong;
3. **quarantine** when the record cannot support the current use;
4. **retain with flag** when the value is valid but unusual;
5. **change the model population** only through approved scope and impact analysis;
6. **stop development or scoring** when material uncertainty remains.

The governed monitoring agent may recommend a halt when critical rules fail, but it cannot correct records, waive rules, retrain, or deploy. Human owners retain those authorities.

## Comparing datasets

South German Credit has no missing values according to UCI, but that does not make it production-ready. It has no application dates, uses a historical oversampled population, and contains transformed amounts and sensitive historical categories. Taiwan credit-card default is larger and behavioural but also lacks a development timeline suitable for a true out-of-time split. The dataset contract makes these limitations visible in every run manifest.

## Exercises

1. Increase the injected defect rate from 1% to 5%. Compare rule failures, quarantine volume, default rate, and model metrics.
2. Add a cross-field rule that employment years cannot exceed age minus 18. Decide whether failures should be critical or warnings and justify the threshold.
3. Compare complete-case quarantine with a documented imputation strategy. Measure both predictive performance and population shift; do not select only by AUC.
4. Create a point-in-time leakage test for a bureau field with `source_timestamp` and `decision_timestamp`.

## Code

- Dataset contracts: `src/creditriskbook/data/datasets.py`
- Synthetic generator: `src/creditriskbook/data/synthetic.py`
- Quality rules and defect injection: `src/creditriskbook/data/quality.py`
- Tests: `tests/test_quality.py`


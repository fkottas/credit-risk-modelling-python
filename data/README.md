# Data access

Raw and processed datasets are intentionally excluded from Git. Use a registered loader or place a legally obtained file under `data/raw/<dataset-key>/`.

The repository's earlier synthetic generators for BNPL/microloans, fraud, LGD, EAD, and IFRS 9 cohorts remain under `data/generators/`. They are preserved and will be brought into the common dataset contract after their assumptions, schemas, licences, and tests are reviewed. The new `synthetic_retail` generator is the first generator covered by the package test suite.

## Supported teaching datasets

| Key | Access | Default use |
|---|---|---|
| `synthetic_retail` | Generated locally | Tests, data quality, deployment, monitoring, IFRS 9 demonstrations |
| `uci_south_german` | UCI downloader | Small PD, scorecard, cost-sensitive classification, fairness discussion |
| `uci_taiwan_credit_card` | UCI downloader | Behavioural PD, calibration, ML comparison |
| `kaggle_credit_risk` | Student downloads `credit_risk_dataset.csv` | Dataset switching, missing data, model benchmarking |

South German Credit uses only the core dependencies. Install optional Excel support for the Taiwan dataset with `python -m pip install -e '.[datasets]'`.

For Kaggle, download the dataset with your own account after reviewing the dataset page and current terms. Place the CSV at:

```text
data/raw/kaggle_credit_risk/credit_risk_dataset.csv
```

Do not commit the file. The loader records the local file's SHA-256 digest in the run metadata.

## Teaching defects

`creditriskbook.data.quality.inject_teaching_defects` creates missing values, duplicates, invalid ranges, inconsistent categories, future dates, and a target-leakage field. The transformation is deterministic for a supplied random seed. Reports must describe the output as a modified teaching derivative, name the source dataset, and retain the source attribution.

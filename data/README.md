# Data access

Raw and processed datasets are intentionally excluded from Git. Use a registered loader or place a legally obtained file under `data/raw/<dataset-key>/`.

The repository's earlier synthetic generators for BNPL/microloans and fraud remain under `data/generators/`. Reviewed package generators now cover retail applications, relational behavioural histories, LGD recoveries, EAD/CCF, IFRS 9 schedules, IRB portfolios and counterparty profiles. Each reviewed generator has deterministic tests and an explicit synthetic-data limitation.

## Supported teaching datasets

| Key | Access | Default use |
|---|---|---|
| `synthetic_retail` | Generated locally | Tests, data quality, deployment, monitoring, IFRS 9 demonstrations |
| `synthetic_behavioral_history` | Generated locally as four relational tables | Cleaning, point-in-time joins, DPD/utilisation/payment/bureau features |
| `uci_south_german` | UCI downloader | Small PD, scorecard, cost-sensitive classification, fairness discussion |
| `uci_taiwan_credit_card` | UCI downloader | Behavioural PD, calibration, ML comparison |
| `kaggle_credit_risk` | Student downloads `credit_risk_dataset.csv` | Dataset switching, missing data, model benchmarking |
| `synthetic_credit_documents` | Generated locally as applications, documents, expected facts and policy text | NLP extraction, BM25 retrieval, structured memoranda, prompt-injection and agent controls |

The 36-record registry also records official or conditional sources from HMDA/CFPB, SBA, SEC EDGAR, the Federal Reserve, EBA, FHFA, Fannie Mae, Freddie Mac, World Bank and FRED, plus scope-limited or non-bundled Kaggle cases. Readers obtain provider-controlled files under the current official terms; the repository does not republish them. Public access is not treated as permission for every purpose, and every source retains an explicit modelling limitation.

South German Credit uses only the core dependencies. Install optional Excel support for the Taiwan dataset with `python -m pip install -e '.[datasets]'`.

For Kaggle, download the dataset with your own account after reviewing the dataset page and current terms. Place the CSV at:

```text
data/raw/kaggle_credit_risk/credit_risk_dataset.csv
```

Do not commit the file. The loader records the local file's SHA-256 digest in the run metadata.

## Teaching defects

`creditriskbook.data.quality.inject_teaching_defects` creates missing values, duplicates, invalid ranges, inconsistent categories, future dates, and a target-leakage field. The transformation is deterministic for a supplied random seed. Reports must describe the output as a modified teaching derivative, name the source dataset, and retain the source attribution.

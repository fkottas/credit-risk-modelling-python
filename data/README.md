# Data access

Raw and processed datasets are intentionally excluded from Git. Use a registered loader or place a legally obtained file under `data/raw/<dataset-key>/`.

The repository's earlier synthetic generators for BNPL/microloans and fraud remain under `data/generators/`. Reviewed package generators now cover retail applications, relational behavioural histories, LGD recoveries, EAD/CCF, IFRS 9 schedules, IRB portfolios and counterparty profiles. Each reviewed generator has deterministic tests and an explicit synthetic-data limitation.

## Supported teaching datasets

| Key | Access | Default use |
|---|---|---|
| `synthetic_retail` | Generated locally | Tests, data quality, deployment, monitoring, IFRS 9 demonstrations |
| `synthetic_behavioral_history` | Generated locally as four relational tables | Cleaning, point-in-time joins, DPD/utilisation/payment/bureau features |
| `uci_south_german` | UCI downloader | Small PD, scorecard, cost-sensitive classification, fairness discussion |
| `uci_statlog_german` | UCI downloader | Source-validation case; documented legacy coding problems, not the preferred benchmark |
| `uci_taiwan_credit_card` | UCI downloader | Behavioural PD, calibration, ML comparison |
| `uci_australian_credit_approval` | UCI downloader | Mixed-type application screening; target is approval, never PD |
| `uci_bank_marketing` | UCI downloader | Non-credit leakage and ordered-source exercises; target is deposit subscription |
| `kaggle_credit_risk` | Student downloads `credit_risk_dataset.csv` | Dataset switching, missing data, model benchmarking |
| `synthetic_credit_documents` | Generated locally as applications, documents, expected facts and policy text | NLP extraction, BM25 retrieval, structured memoranda, prompt-injection and agent controls |
| World Bank WDI | Official API through `load_world_bank_wdi` | Macro history and scenario/satellite-model exercises; never a borrower outcome |
| CFPB complaints | Student downloads an extract; `load_cfpb_complaint_extract` validates it | Complaint taxonomy and NLP; not PD and not representative |

The 41-record registry also records official or conditional sources from HMDA/CFPB, SBA, SEC EDGAR, the Federal Reserve, EBA, FHFA, BLS Consumer Expenditure PUMD, World Bank, Eurostat, ECB and FRED, plus scope-limited Kaggle cases. Fannie Mae and Freddie Mac loan-level files are reference-only and excluded by project policy because the reviewed terms do not support this open commercial teaching repository. A catalogue record is not represented as an executed dataset. [The dataset-use matrix](DATASET_USE_MATRIX.md) reports the exact implementation state and analytical scope. Public access is not treated as permission for every purpose, and every source retains an explicit modelling limitation.

South German Credit uses only the core dependencies. Install optional Excel support for the Taiwan dataset with `python -m pip install -e '.[datasets]'`.

For Kaggle, download the dataset with your own account after reviewing the dataset page and current terms. Place the CSV at:

```text
data/raw/kaggle_credit_risk/credit_risk_dataset.csv
```

Do not commit the file. The loader records the local file's SHA-256 digest in the run metadata.

## Teaching defects

`creditriskbook.data.quality.inject_teaching_defects` creates missing values, duplicates, invalid ranges, inconsistent categories, future dates, and a target-leakage field. The transformation is deterministic for a supplied random seed. Reports must describe the output as a modified teaching derivative, name the source dataset, retain the source attribution and remain within the source licence. Altering a restricted dataset does not remove its licence or privacy obligations.

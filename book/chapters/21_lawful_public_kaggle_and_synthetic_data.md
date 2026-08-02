# Chapter 21 - Lawful public, Kaggle, and synthetic data

## Publicly reachable does not mean freely reusable

A downloadable file can still be copyrighted, restricted by contract, limited to a competition, or incorrectly relicensed by a mirror. The book therefore uses a dataset acceptance gate before code is written. Each approved dataset needs an identifiable owner, authoritative landing page, explicit licence or terms, compatible use, attribution, target definitions, and a recorded access date.

The machine-readable register is `data/dataset_registry.yml`. It is part of the empirical evidence, not administrative decoration.

## Why the book switches datasets

No public dataset supports every credit-risk problem. Most default-classification datasets do not contain recovery cash flows, undrawn commitments, contractual schedules, macroeconomic scenarios, or historical stage transitions. Reusing one binary dataset to demonstrate LGD, EAD, IFRS 9, and collections would require inventing undocumented fields and could teach the wrong data structure.

| Case | Primary teaching data | Why |
|---|---|---|
| Small PD and scorecard | UCI South German Credit | Corrected documentation, cost matrix, manageable size |
| Behavioural PD and ML | UCI Taiwan credit-card default | 30,000 accounts and repeated billing/payment fields |
| Dataset switching and missing data | Kaggle `laotse/credit-risk-dataset` | CC0-labelled simulated teaching data; student download |
| Data-quality, deployment, monitoring | Project synthetic retail portfolio | Known truth, dates, unrestricted reproducibility |
| LGD and recovery survival | Purpose-built synthetic recovery ledger | Requires dated recoveries, costs, cures, and censoring |
| EAD/CCF | Purpose-built synthetic revolving facility | Requires limits, balances, drawdowns, and default dates |
| IFRS 9 | Purpose-built synthetic longitudinal portfolio plus licensed macro data | Requires origination PD, reporting dates, stages, horizons, and scenarios |

## UCI datasets

The UCI records for South German Credit, Statlog German Credit, and Default of Credit Card Clients display a CC BY 4.0 licence. This permits sharing and adaptation with appropriate attribution. The repository still downloads the source by code, validates a pinned checksum, and records the extracted file digest. This reduces repository size and makes an upstream change visible.

South German Credit is the preferred small benchmark. Its UCI record explains that the earlier Statlog version has serious coding-information errors. The older version remains valuable for an exercise in provenance and source reconciliation, but it is not silently treated as equivalent data.

### Live download and checksum

```bash
creditrisk-demo --dataset uci_south_german
```

The loader accepts only the reviewed archive digest. If UCI updates the archive, the code stops and requires a human review instead of automatically trusting the new bytes.

## Kaggle datasets

Kaggle datasets fall into different legal categories:

1. a dataset whose page identifies the uploader as creator and displays a reusable licence;
2. a mirror of data owned elsewhere;
3. competition data governed by competition-specific rules;
4. data with missing or unclear provenance.

Only the first category can normally enter the approved teaching path from Kaggle metadata alone. Mirrors are traced back to the original publisher. Competition data such as Home Credit are conditional: students may use their own legally authorised download after accepting the current rules, but the book repository does not bundle the files.

The initial Kaggle adapter supports `laotse/credit-risk-dataset`, whose page displayed CC0 on 2 August 2026 and described simulated credit-bureau-style data. Students download `credit_risk_dataset.csv` themselves and place it under `data/raw/kaggle_credit_risk/`. The loader validates the expected schema and records a SHA-256 digest.

```bash
creditrisk-demo \
  --dataset kaggle_credit_risk \
  --data-path data/raw/kaggle_credit_risk/credit_risk_dataset.csv
```

The Kaggle page, licence label, uploader, description, and file schema must be reviewed again before a formal book release. A platform label is useful evidence but cannot resolve a false upload or rights the uploader never possessed.

## Synthetic data

Synthetic data have three roles:

- deterministic unit and integration tests;
- structures not available in open real data, such as recovery ledgers and stage histories;
- safe failure exercises containing deliberately invalid values.

Synthetic does not mean representative or privacy-proof. A generator calibrated directly to confidential records can leak information, while an independent generator can be unrealistic. The current retail generator is independent and pedagogical. It does not resample an original dataset and makes no claim to reproduce a lender.

## Creating a flawed teaching derivative

The defect injector operates after lawful access. It never changes the original file. Given a seed, it adds known missing fields, duplicate identifiers, invalid ranges, invalid categories, future dates, and a target-derived leakage field. The run manifest identifies the source and modified teaching copy.

For a CC BY dataset, a distributed adaptation would need attribution and an indication that changes were made. The repository avoids unnecessary redistribution and creates the adaptation locally. This also lets students reproduce the defects themselves.

## Adding another dataset

Before adding an adapter:

1. add a registry entry and official URL;
2. save the licence name, licence URL, access date, and attribution text;
3. decide whether redistribution is permitted or whether download-by-user is required;
4. document the unit, target, time coverage, and known sampling process;
5. map protected attributes separately from baseline model features;
6. pin a checksum when the publisher provides a stable file;
7. add a fixture-based schema test and, where possible, an opt-in live download test;
8. name the book cases for which the data are structurally suitable.

## Exercises

1. Compare the licence shown by a Kaggle mirror with the original publisher's licence. Record which one governs the book's use and why.
2. Run the same PD workflow on UCI South German and the approved Kaggle dataset. Explain why differences cannot be attributed only to algorithms.
3. Create a candidate registry entry for a dataset without adding code. Mark unresolved provenance or redistribution questions explicitly.

## Dataset references

- [South German Credit, UCI ML Repository, DOI 10.24432/C5X89F](https://archive.ics.uci.edu/dataset/522/south+german+credit).
- [Statlog German Credit Data, UCI ML Repository, DOI 10.24432/C5NC77](https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data).
- [Default of Credit Card Clients, UCI ML Repository, DOI 10.24432/C55S3H](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients).
- [Credit Risk Dataset by laotse, Kaggle](https://www.kaggle.com/datasets/laotse/credit-risk-dataset).
- [World Bank summary terms of use](https://data.worldbank.org/summary-terms-of-use).


# Applied Credit Risk with Python

## Scorecards, IRB, IFRS 9, Deployment and Governed Agentic AI

Dr. Ferdinantos Kottas

First-edition review manuscript — August 2026

### About this book

This is an application-first book about building a credit-risk system, not only fitting a classifier. The work begins with legal access to data and a point-in-time target. It continues through data quality, scorecard and machine-learning development, probability calibration, LGD and EAD, expected credit loss, regulatory capital, decision economics, validation, deployment, monitoring, and retirement. The final part introduces agentic AI within strict permissions: agents can assemble evidence and recommend action, but they do not approve customers, alter policy, retrain models, or deploy code without an authorised human process.

The companion repository contains original code for the scorecard machinery. It does not call a specialist scorecard package. Manual, quantile, equal-width, ChiMerge and monotonic binning; missing and special-value treatment; WOE and information value; penalised logistic estimation; point scaling; rating mapping; reason codes; characteristic reports; and model-agnostic score mapping are implemented in `creditriskbook.scorecard`. Each public dataset enters through one contract that records its source, licence, checksum, target, features and limitations. Synthetic portfolios cover use cases for which no suitable open loan-level data exist.

### Intended reader

The primary reader knows basic Python and statistics and wants to become capable of delivering a defensible model. Experienced practitioners can use the book as an implementation reference or teaching sequence. Every empirical result is a teaching result. It is not evidence that the same method, variable, cut-off or model should be used by a lender.

### Author

Dr. Ferdinantos Kottas is a quantitative and risk data scientist. Maynooth University's research repository records his 2025 PhD thesis in finance on the performance and factor structure of environmentally classified European securities. His peer-reviewed work includes *Performance of Green vis-à-vis Red EU Securities* (2024), *Empirical Asset Pricing Models for Green, Grey, and Red EU Securities* (2025), and *Factor Structure of Green, Grey, and Red EU Securities* (2025). His public professional profile describes applied work across credit and fraud scorecards, machine learning, portfolio management and quantitative finance. The independently verifiable academic details are cited in the references; professional descriptions that are not independently verified are presented as the author's own profile [R20–R22].

### Legal, regulatory and professional notice

This manuscript and repository are educational. They are not legal, accounting, regulatory, investment or lending advice; they are not a validated production model; and they are not a substitute for an institution's policies, qualified advisers, independent validation, audit, compliance or supervisory engagement. Rules vary by jurisdiction and change. Regulatory statements in this edition use sources reviewed on 2 August 2026 and must be checked again before use.

Third-party books and professional guides supplied for background are cited and paraphrased; their prose, figures, tables and examples are not reproduced. Public availability does not prove permission. A dataset is used only if its publisher, terms, attribution and intended use can be documented. Kaggle competition files are not redistributed. Public mortgage-application data are not mislabelled as default data. Bankruptcy is not silently relabelled as regulatory default. Generated teaching defects are documented modifications of project-generated or lawfully accessed data.

### Reproducibility promise

Every runnable case has a fixed random seed, explicit input contract and test. Live UCI downloads are pinned by archive and extracted-file SHA-256 checksums. All notebooks are valid JSON and every code cell is executed in CI on Python 3.11 and 3.12. The repository records known simplifications next to the code instead of hiding them in prose.

### How to use the labs

1. Install the package in a clean environment.
2. Run the unit tests and notebook validator before changing anything.
3. Start with synthetic data, then switch to a public dataset that matches the question.
4. Create a development report containing data lineage, sample definition, transformations, model, calibration, limitations and decisions.
5. Change one assumption at a time and explain its impact.
6. Do not interpret a high AUC, IV or profit estimate as production readiness.

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python tools/validate_notebooks.py
python examples/end_to_end.py --dataset synthetic_retail
```

### Notation

`PD` is probability of default over a defined horizon; `LGD` is loss severity conditional on default; `EAD` is exposure at default; `ECL` is expected credit loss; `EL` is expected loss; `UL` is unexpected loss; `CCF` is credit conversion factor; `SICR` is significant increase in credit risk; `WOE` is weight of evidence; and `IV` is information value. A “bad” or “event” is encoded as 1 unless a dataset contract says otherwise.


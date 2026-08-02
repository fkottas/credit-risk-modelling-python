# Appendices

## Appendix A — Repository map

| Path | Purpose |
|---|---|
| `src/creditriskbook/data` | dataset adapters, synthetic data and quality rules |
| `src/creditriskbook/scorecard` | from-scratch binning, WOE, IRLS, points, reasons and reports |
| `src/creditriskbook/models` | baseline PD model and evaluation |
| `risk_components.py` | workout LGD and CCF/EAD construction |
| `capital.py` | corporate IRB and Vasicek teaching calculations |
| `survival.py` | Kaplan–Meier and hazard-to-PD functions |
| `decisioning.py` | cut-off and value analysis |
| `ecl.py` | simplified scenario ECL illustration |
| `agents/governed.py` | deterministic monitoring triage boundary |
| `notebooks` | nine executable student labs |
| `tests` | deterministic and opt-in live data checks |
| `data/dataset_registry.yml` | source, licence, attribution and use register |
| `references` | regulatory and evidence source maps |

## Appendix B — Dataset selection matrix

| Dataset | Legal status used here | Suitable question | Prohibited shortcut |
|---|---|---|---|
| Synthetic retail | project-generated | full lifecycle, DQ, PD, ECL, deployment | claim it represents a lender |
| South German Credit | UCI CC BY 4.0 | small application scorecard benchmark | ignore historical bias and no dates |
| Taiwan card default | UCI CC BY 4.0 | behavioural PD and ML | treat 2005 sample as current production evidence |
| Credit Approval | UCI CC BY 4.0 | missingness and approval pipeline | call approval probability PD |
| Polish Bankruptcy | UCI CC BY 4.0 | low-event corporate failure | call bankruptcy Basel default |
| Taiwan Bankruptcy | UCI CC BY 4.0 | corporate ML and calibration | ignore period and absent date field |
| Kaggle credit-risk file | page displayed CC0 at review; student download | switching and benchmark | bundle without release review |
| HMDA | US public privacy-modified records | mortgage decisions and access | estimate default without performance |
| Home Credit competition | competition-specific | optional relational ML | redistribute files |

## Appendix C — Test commands

```bash
python -m unittest discover -s tests -v
RUN_LIVE_DATA_TESTS=1 python -m unittest tests.test_live_datasets -v
python tools/validate_notebooks.py
```

The live suite downloads fixed UCI archives and verifies both archive and extracted-file SHA-256. It is opt-in because CI environments may block network access. A changed checksum is a review event, not a test to bypass.

## Appendix D — Scorecard formulas

WOE convention:

`WOE_j = ln(dist_good_j / dist_bad_j)`.

Information value:

`IV = Σ_j (dist_good_j − dist_bad_j) × WOE_j`.

Logistic model:

`logit(PD) = β0 + Σ β_k WOE_k`.

Score factor and offset:

`factor = PDO / ln(2)`

`offset = base_score − factor × ln(base_good_to_bad_odds)`.

Score:

`score = offset − factor × logit(PD)`.

Base and bin points:

`base_points = offset − factor × β0`

`bin_points_k = −factor × β_k × WOE_k`.

## Appendix E — Minimum model card

- Name, version, owner and status
- Purpose, users, decisions and prohibited uses
- Population, product, geography and horizon
- Data sources, licence, lineage and protected data
- Target and sample construction
- Method, transformations and calibration
- Performance, uncertainty and segment results
- Fairness and reason-code assessment
- Limitations, overlays and compensating controls
- Validation, approval and effective dates
- Deployment artefact and dependencies
- Monitoring, thresholds, escalation and rollback
- Change history and retirement plan

## References

[R1] Basel Committee on Banking Supervision. *CRE31 — IRB approach: risk-weight functions*. Consolidated Basel Framework. https://www.bis.org/basel_framework/chapter/CRE/31.htm

[R2] Basel Committee on Banking Supervision. *CRE32 — IRB approach: risk components*. https://www.bis.org/basel_framework/chapter/CRE/32.htm

[R3] European Banking Authority. *Guidelines on PD estimation, LGD estimation and treatment of defaulted exposures*, EBA/GL/2017/16, and current implementation materials. https://www.eba.europa.eu/activities/single-rulebook/regulatory-activities/model-validation/guidelines-pd-estimation-lgd

[R4] IFRS Foundation. *IFRS 9 Financial Instruments — Project Summary*, July 2014. https://www.ifrs.org/content/dam/ifrs/project/fi-impairment/ifrs-standard/published-documents/project-summary-july-2014.pdf

[R5] IFRS Foundation. *IFRS 9 Financial Instruments*, impairment requirements and definitions. Use the currently applicable licensed standard. Public 2021 issued-standard copy consulted for this review: https://www.ifrs.org/content/dam/ifrs/publications/pdf-standards/english/2021/issued/part-a/ifrs-9-financial-instruments.pdf

[R6] Federal Deposit Insurance Corporation. *Current Expected Credit Losses (CECL)* resources and interagency materials. https://www.fdic.gov/accounting/current-expected-credit-losses-cecl

[R7] European Union. Regulation (EU) 2024/1689, Artificial Intelligence Act, official text. https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng

[R8] National Institute of Standards and Technology. *AI Risk Management Framework 1.0* and *Generative AI Profile*. https://www.nist.gov/itl/ai-risk-management-framework

[R9] Board of Governors of the Federal Reserve System. *SR 26-2: Revised Guidance on Model Risk Management*, 17 April 2026. https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm

[R10] UCI Machine Learning Repository. *South German Credit*, DOI 10.24432/C5X89F, CC BY 4.0. https://archive.ics.uci.edu/dataset/522/south+german+credit

[R11] Yeh, I. *Default of Credit Card Clients*, UCI Machine Learning Repository, DOI 10.24432/C55S3H, CC BY 4.0. https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients

[R12] Quinlan, J. *Credit Approval*, UCI Machine Learning Repository, DOI 10.24432/C5FS30, CC BY 4.0. https://archive.ics.uci.edu/dataset/27/credit+approval

[R13] Tomczak, S. *Polish Companies Bankruptcy*, UCI Machine Learning Repository, DOI 10.24432/C5F600, CC BY 4.0. https://archive.ics.uci.edu/dataset/365/polish+companies+bankruptcy+data

[R14] UCI Machine Learning Repository. *Taiwanese Bankruptcy Prediction*, dataset 572, CC BY 4.0. https://archive.ics.uci.edu/dataset/572/taiwanese+bankruptcy+prediction

[R15] Consumer Financial Protection Bureau. *Home Mortgage Disclosure Act Data*. https://www.consumerfinance.gov/data-research/hmda/

[R16] World Bank. *World Development Indicators* and dataset terms. https://data.worldbank.org/summary-terms-of-use

[R17] Siddiqi, N. *Intelligent Credit Scoring: Building and Implementing Better Credit Risk Scorecards*, 2nd ed., Wiley, 2017. Cited as background; no text, table, figure, code or worked example is reproduced.

[R18] PwC. *IFRS 9 impairment practical guide: provision matrix*, 2018. Secondary professional interpretation; no text, table, figure or worked example is reproduced.

[R19] Hamerle, A., Liebig, T., and Rösch, D. *Credit Risk Factor Modeling and the Basel II IRB Approach*, Deutsche Bundesbank Discussion Paper 02/2003. Historical research context.

[R20] Maynooth University Research Archive. Kottas, F. *Performance and factor structure of green, grey and red securities in European Union countries*, PhD thesis, 2025. https://mural.maynoothuniversity.ie/id/eprint/20102/

[R21] Kottas, F. *Empirical Asset Pricing Models for Green, Grey, and Red EU Securities: A Fama–French and Carhart Model Approach*, Journal of Risk and Financial Management 18(5), 2025. https://www.mdpi.com/1911-8074/18/5/282

[R22] Kottas, F. Public professional profile. Claims not independently verified are treated as self-description. https://fkottas.github.io/FerdinantosKottas.github.io/

[R23] Basel Committee on Banking Supervision. *CRE52 — Standardised approach to counterparty credit risk*. https://www.bis.org/basel_framework/chapter/CRE/52.htm

[R24] Kubam, C. S. *Agentic AI for Autonomous, Explainable, and Real-Time Credit Risk Decision-Making*. Treated only as conceptual background because the supplied paper does not provide sufficient reproducible evidence for its reported performance claims.


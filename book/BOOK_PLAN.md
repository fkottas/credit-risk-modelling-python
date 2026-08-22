# Expanded first-edition structure

Title: **Intelligent Credit Risk Modeling with Python**

Subtitle: **From Data Quality and Scorecards to IFRS 9, Basel IRB, Deployment, and Governed Agentic AI**

Author: **Dr. Ferdinantos Kottas**

The expanded edition has 72 analytical chapters in twelve parts. Each chapter contains Python, a practical lab, policy/interpretation boundaries, and a dataset/code crosswalk. The authoritative chapter titles and package/dataset mappings are machine-readable in `book/structure.json` and validated by `tools/validate_manuscript.py`.

| Part | Chapters | Scope |
|---|---:|---|
| I | 1–6 | credit-risk mathematics, loss distributions, dependence, time and the model operating system |
| II | 7–12 | products, borrowers, lifecycle, segmentation, risk appetite and credit policy |
| III | 13–18 | Basel, IRB architecture, IFRS 9, CECL, privacy, consumer protection and responsible AI |
| IV | 19–24 | lawful/public/synthetic data, attribution, contracts, point-in-time joins, quality and leakage |
| V | 25–30 | original scorecard engineering: manual/automatic bins, WOE/IV, IRLS, PDO, grades and reasons |
| VI | 31–36 | evaluation, calibration, PD, trees, XGBoost, explainability, fairness and reject inference |
| VII | 37–42 | survival, lifetime PD, low-default portfolios, workout LGD, downturn and revolving EAD/CCF |
| VIII | 43–48 | IFRS 9/CECL engine, SICR, scenarios, cash flows, provision matrices, overlays and stress |
| IX | 49–54 | IRB functions/parameters, portfolio dependence/concentration and counterparty/CVA/SA-CCR |
| X | 55–60 | validation, backtesting, UAT, pricing, profit, limits, bandits and safe reinforcement learning |
| XI | 61–66 | deployment, APIs, containers, monitoring, incidents, governance, change and retirement |
| XII | 67–72 | NLP, document extraction, BM25 retrieval, structured LLM outputs, RAG, governed agents, human workflows and red teams |

## Applied material after the chapters

- original scorecard, IFRS 9, IRB and agent API guides;
- lawful 41-record dataset catalogue and 76-source reference ledger;
- 72-case practice book;
- twelve end-to-end technical workshops;
- twelve hand-auditable numerical examples;
- sixteen model/data/accounting/capital/AI policy templates;
- 72 viva questions with instructor notes;
- technical and governance glossary.

## Executable crosswalk

| Area | Primary package | Notebooks |
|---|---|---|
| data quality and public switching | `creditriskbook.data` | 01, 08, 13 |
| from-scratch scorecards | `creditriskbook.scorecard` | 02, 11 |
| PD, ML, calibration and decisions | `creditriskbook.models`, `decisioning` | 03, 04 |
| survival, LGD and EAD | `creditriskbook.survival`, `risk_components` | 05, 13 |
| IFRS 9 and CECL | `creditriskbook.ifrs9` | 06, 09 |
| Basel IRB and portfolios | `creditriskbook.irb` | 06, 10 |
| deployment, monitoring and agents | `creditriskbook.monitoring`, `agents` | 07, 12 |
| NLP, documents, retrieval and bounded LLM workflows | `creditriskbook.nlp` | 15 |

The Word builder uses `book/full_manuscript/`, interleaves one mathematics-to-code laboratory after every chapter, and uses native Word equations plus original teaching figures. The current analytical review output exceeds 400 pages. It remains an educational review manuscript requiring legal, accounting, regulatory, technical and independent model review before publication or real use.

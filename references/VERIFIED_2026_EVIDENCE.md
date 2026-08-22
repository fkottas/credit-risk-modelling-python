# Verified 2026 evidence pack

**Review date:** 22 August 2026  
**Purpose:** editorial traceability for statements that can change with law, regulation,
accounting guidance or provider terms. This register is not legal or accounting advice.

## Evidence labels

| Label | Meaning in the manuscript |
|---|---|
| Requirement | Text drawn from binding law or an applicable accounting requirement; applicability still depends on facts and jurisdiction. |
| Supervisory guidance | An agency's communicated risk-management practice; not automatically a binding rule. |
| Provider condition | A source or dataset owner's reuse, attribution, access or redistribution condition. |
| Interpretation | A reasoned explanation that must not be presented as quoted law or policy. |
| Author control | A conservative engineering or teaching choice adopted by this project. |

## Regulatory and accounting claim matrix

| Claim ID | Classification | Verified proposition | Exact official location | Manuscript wording guardrail |
|---|---|---|---|---|
| BASEL-IRB-MAP-01 | Requirement / framework | CRE30 covers IRB overview and asset classes; CRE31 risk-weight functions; CRE32 risk components; CRE36 minimum requirements. | Basel Framework CRE30, CRE31, CRE32 and CRE36 [R1–R4] | Do not swap CRE31 and CRE32 or describe internal estimation as freedom to replace prescribed functions. |
| IFRS9-12M-01 | Requirement | Twelve-month ECL is the portion of lifetime cash shortfalls resulting from default events possible in the next twelve months. | IFRS 9 Appendix A and B5.5.43–B5.5.44 [R5–R6] | Do not call it the cash shortfall expected to occur only within twelve months. |
| IFRS9-PIR-01 | Official standard-setter conclusion | The IASB completed the impairment PIR on 4 July 2024 and concluded that the requirements are working as intended, with targeted follow-up. | IASB project summary and feedback statement [R41] | Do not infer that every implementation is comparable, unbiased or well controlled. |
| CECL-LIFE-01 | Accounting framework | CECL generally estimates expected lifetime credit losses from initial recognition for assets in scope; it has no IFRS 9 Stage 1/Stage 2 horizon switch. | Topic 326 resources and interagency materials [R7, R15] | Keep IFRS 9 and CECL configuration separate even where calculations share utilities. |
| CECL-ASU-25-01 | Requirement / narrow amendment | ASU 2025-05 addresses eligible accounts receivable and contract assets. | FASB ASU 2025-05 [R42] | Do not describe the amendment as a replacement for Topic 326 or generalise its expedients to all lending assets. |
| US-MRM-26-01 | Supervisory guidance | SR 26-2, OCC 2026-13 and FDIC FIL-15-2026 communicate revised, risk-based and tailored model-risk guidance. | Scope, introduction and attached guidance [R9, R75–R76] | State explicitly that the guidance is not presented as enforceable or prescriptive requirements. |
| US-MRM-26-02 | Supervisory guidance | The revised guidance is expected to be most relevant to organisations above USD 30 billion in total assets, but may be relevant below that level where model-risk exposure is significant. | Scope section [R9, R75–R76] | Do not convert the size indication into a universal legal threshold. |
| US-MRM-AI-01 | Supervisory guidance | Generative-AI and agentic-AI models are outside the revised guidance's scope; organisations should control out-of-scope tools through their own risk-management and governance practices. | Scope section [R9, R75–R76] | The exclusion is not a safety exemption or approval for autonomous credit decisions. |
| AI-EU-CRED-01 | Requirement / classification | Annex III 5(b) covers AI intended to evaluate natural-person creditworthiness or establish a credit score, except AI used to detect financial fraud. | Annex III 5(b), consolidated Regulation (EU) 2024/1689 [R64] | Classify the intended use, not the vendor, model family or file name. |
| AI-EU-DATE-01 | Requirement / effective date | In the 27 July 2026 consolidated text, Chapter III Sections 1–3 for Article 6(2)/Annex III high-risk systems apply from 2 December 2027. | Article 113 as amended by Regulation (EU) 2026/1744 [R64–R65] | Do not retain the pre-amendment 2 August 2026 date for these provisions. |
| AI-EU-HO-01 | Requirement / future application | Human oversight must enable natural persons to understand relevant capacities and limitations, monitor operation, identify anomalies and intervene or stop as appropriate. | Article 14 [R64] | Do not reduce meaningful oversight to an unexamined confirmation click. |
| GDPR-AUTO-01 | Requirement / case law | Article 22 addresses solely automated decisions with legal or similarly significant effects; the CJEU held that score production may qualify where a third party draws strongly on it for a contractual decision. | GDPR Article 22 [R34]; C-634/21 [R66] | Analyse workflow facts, legal basis, safeguards and contestability; do not assume every score or every human touch has the same treatment. |
| US-AA-01 | Supervisory / compliance interpretation | Creditors using complex algorithms remain responsible for specific and accurate principal adverse-action reasons. | CFPB Circulars 2022-03 and 2023-03 [R44–R45] | Generic feature importance or a nearest checklist item is not automatically an adequate reason. |

## Dataset and reuse claim matrix

| Claim ID | Source | Verified condition | Repository decision |
|---|---|---|---|
| DATA-UCI-CCBY-01 | UCI credit datasets | The reviewed official records display CC BY 4.0 and stable DOIs. | Download from UCI, record DOI and attribution, validate schema and checksum; do not treat historical samples as current portfolio evidence. |
| DATA-WB-01 | World Bank | Default dataset licensing commonly uses CC BY 4.0 plus mandatory terms, but dataset metadata can differ. | Review the selected indicator/dataset record; preserve attribution, vintage and revision metadata [R70]. |
| DATA-ECB-01 | ESCB statistics | Publicly released statistics may be reused free of charge if the source is quoted and statistics/metadata are not modified; third-party data are excluded. | Use only reviewed series, quote the source, identify calculations as project modifications, and retain vintage metadata [R71]. |
| DATA-EUROSTAT-01 | Eurostat | Reuse is permitted with source acknowledgement and disclosure of changes; third-party rights can require separate clearance. | Download-by-code, cite Eurostat, disclose transformations and exclude unresolved third-party content [R72]. |
| DATA-BLS-CE-01 | BLS Consumer Expenditure PUMD | Public-use files contain respondent-level expenditure, income and demographics after confidentiality adjustments. | Use for affordability/resilience and survey-weight labs, not default modelling; do not label the files CC0 without separate evidence [R73]. |
| DATA-FED-STRESS-01 | Federal Reserve scenarios | Annual supervisory scenarios are hypothetical paths used in stress testing. | Use as a scenario-design case; do not present the paths as forecasts, occurrence probabilities or ready-made IFRS 9 scenario weights [R74]. |
| DATA-FRED-01 | FRED | Rights can depend on the underlying series provider. | Treat licence per series; do not bundle a broad extract merely because it was obtained through one API. |
| DATA-CFPB-COMP-01 | CFPB complaints | Published complaint data can be used for analysis; narratives are consent-based and scrubbed, and the database is not a statistical sample of all experience. | Download from the official source, minimise narrative data, teach NLP and governance rather than applicant PD. |
| DATA-KAGGLE-01 | Kaggle competitions | Access and reuse depend on current competition rules and provider rights. | Never bundle competition files by default; each student obtains them independently after reviewing current terms. |

## Mathematical audit rules adopted

Every material method should progress through: objective; notation; assumptions; derivation;
small hand-worked example; plain Python implementation; expected output; tests and invariants;
common errors; advanced extension; and reference. Two repaired examples are:

- discounted contractual cash-flow shortfall in Chapter 1, with payments, recoveries and
  workout costs given explicit signs and timing; and
- penalised logistic IRLS in Chapter 29, with an average objective, an unpenalised intercept,
  stable probabilities, a linear solve rather than a matrix inverse, convergence evidence and
  finite-coefficient tests under separation [R63].

## Claims rejected or repaired during this review

- No fixed AUC improvement is claimed for machine learning over logistic regression. Results
  depend on data, validation design, tuning and objective.
- Logistic regression is not described as natively calibrated in every population or time period.
- No mathematical identity is asserted between AUC and Brier score. The Brier score is instead
  taught with the Murphy reliability-resolution-uncertainty decomposition [R24, R69].
- No unsupported closed-form SHAP-instability formula is used for correlated predictors.
- No universal sample-size threshold is used to authorise XGBoost, neural networks or agentic AI.
- Competition access, API access and public visibility are not treated as redistribution licences.
- Synthetic rows generated independently by this project are distinguished from transformed or
  deliberately corrupted derivatives of a licensed source; the latter retain source attribution and
  applicable licence obligations.

## Editorial release rule

A mutable claim cannot be promoted into the manuscript unless its jurisdiction or provider,
official title, date/version, exact location, evidence label and source URL are recorded. When a
source changes, the old wording remains in version control, but the released manuscript uses the
new verified wording and records the review date.

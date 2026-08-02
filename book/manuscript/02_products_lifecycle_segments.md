# Chapter 2 — Products, Borrowers and the Credit Lifecycle

## Product mechanics come before algorithms

“Credit risk” covers different contracts. An instalment loan has a disbursed balance and scheduled amortisation. A card or overdraft combines current balance with a contingent undrawn amount. A mortgage has collateral, long maturity, refinance and prepayment. SME and corporate facilities can include covenants, guarantees, revolving lines and sparse defaults. BNPL may have tiny exposures, short horizons, repeated purchases and strong merchant or platform effects. The model unit, outcome and economics must follow the contract.

For application PD, one row may represent an application. For behavioural PD, one row can represent account-month. For EAD, the unit is often facility-reference-date with a future default date. For workout LGD, the natural structure is an account-level default table joined to a one-to-many recovery cash-flow ledger. A single “modelling table” built before these units are agreed is a common source of duplicated events and false sample size.

## Lifecycle and information sets

Origination data include stated application fields, verified income, bureau history, product request, collateral and policy outcomes. Account management adds payment behaviour, delinquency, utilisation, line changes, transactions and communications. Default and collections add default dates, forbearance, legal status, collateral values, recoveries, costs, cure and write-off. Each later stage knows more; it must not leak backwards.

Define the lifecycle as states with entry rules:

- application received;
- approved or declined;
- offer accepted or not taken up;
- account open and current;
- early or late delinquency;
- default;
- cure, recovery, write-off, prepayment or closure.

This state view exposes competing outcomes. A loan prepaid after six months is not a non-default observed for five years. A card closed by the lender changes future exposure. A restructured loan can move between accounting and regulatory states under different rules. Survival and multi-state methods in Chapter 9 deal with this explicitly.

## Segmentation is a modelling hypothesis

Prime, subprime and thin-file are not universal numerical categories. They are labels tied to local bureau coverage, policy and product. Low-default portfolios require different uncertainty treatment from mass retail. A segment should exist because risk generation, data availability, outcome definition, treatment or calibration differs—not because a clustering algorithm produced an attractive chart.

A useful segmentation test asks:

1. Is the target definition consistent inside each segment?
2. Are key predictors observed at similar quality and timing?
3. Is there enough development and validation evidence?
4. Do relationships and calibration differ materially?
5. Will production route accounts reliably?
6. Can monitoring diagnose segment-specific failure?

If routing is unstable, the segment model may create discontinuities. A customer just across a boundary can receive a very different score. Document boundary sensitivity and consider a common model with interactions or partial pooling.

## Product-specific examples

An unsecured personal loan score can focus on affordability, existing obligations, credit history and requested amount. A behavioural card model requires utilisation, payment ratio, delinquency trajectory and line-management history. Using current balance without current limit can confuse exposure with utilisation. An SME model may combine financial ratios, firm age, industry and director or bureau information, but financial-statement dates and lags must be explicit.

BNPL illustrates repeated-decision complexity. A purchase-level model can overstate sample independence because the same customer and merchant appear many times. Labels mature quickly, but fraud and credit loss can be confused. A short delinquency target may be operationally useful without satisfying a regulatory default definition. The project keeps fraud scorecards separate from PD even when infrastructure is shared.

Green or ESG lending adds purpose, eligibility and collateral-performance questions. ESG attributes are not automatically risk predictors; they may be noisy, vendor-dependent or proxies for protected and socioeconomic characteristics. A green product needs both a credit-risk model and controls over the environmental claim.

## Cohorts, vintages and roll rates

A cohort groups accounts by a common starting period, such as origination month. Plot cumulative default by months-on-book for each vintage rather than comparing unseasoned and seasoned books. Roll rates calculate transitions from one delinquency bucket to another over a fixed interval. Cure rates need a rule: number of defaults returning to non-default for a minimum probation period divided by eligible defaults. Changing the probation period changes the answer.

Transition matrices should reconcile rows to one and distinguish absorbing from temporary states. Raw one-month transitions cannot be raised mechanically to long horizons when policy, seasonality or state duration matters. Cohort and transition analysis are first diagnostic tools for target construction, staging and collections strategy.

## Prepayment and selection

Prepayment shortens exposure and can be informative. Low-risk customers may refinance; high-risk borrowers may refinance to avoid distress; product terms and market rates affect both. Treating all prepaid accounts as non-defaults biases lifetime estimates if prepayment competes with default. Approval and take-up create a second selection layer: outcomes are observed only for accepted applicants who booked. Reject inference does not magically reveal rejected outcomes; Chapter 8 treats assumptions and sensitivity explicitly.

## Data contract example

For every case, complete this table before modelling:

| Field | Example definition |
|---|---|
| Unit | account at month-end |
| Observation date | last calendar day of month |
| Feature cut-off | data posted by 23:59 on observation date |
| Outcome window | next 12 complete months |
| Event | first entry into approved default definition |
| Competing events | prepayment, sale, closure, death |
| Exclusions | unresolved data only; no performance-based removal |
| Refresh | monthly after close and reconciliation |

The table turns a vague model request into an auditable sample builder.

## Chapter deliverable

Choose three products—an instalment loan, a revolving facility and BNPL. For each, define model unit, observation window, performance window, default, prepayment, exposure and action. Then design one application, one behavioural and one collections feature that can be known at the observation date. Identify one leakage risk per feature.


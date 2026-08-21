# Chapter 1 — Credit Risk as an Operating System

## The deliverable is a controlled decision system

A credit model estimates something. A credit-risk system defines what is estimated, which data are admissible at the decision time, how estimates are converted into prices or actions, who may override them, how outcomes mature, and what happens when evidence deteriorates. A technically good classifier embedded in a weak system can create more harm than a modest model inside a strong one.

Start with the cash-flow view. A lender exchanges an advance or contingent commitment for promised repayments, fees and interest. Credit loss is the shortfall between contractual value and discounted value actually received, including recovery costs. Default is therefore not the loss itself. Default triggers a state in which the distribution of cash shortfalls changes. A cured borrower can still generate costs; a defaulted secured loan can have low loss; a non-defaulted revolving account can generate exposure far above its reference balance.

For one exposure and one horizon, the familiar expectation is

`Expected loss = PD × LGD × EAD`.

The identity is exact only when the inputs share the same scenario, date, conditioning and definition, or when dependence is dealt with correctly. In general, `E[PD × LGD × EAD]` is not the product of three unconditional averages. Defaults may coincide with lower collateral values, higher utilisation and slower recoveries. An applied model therefore keeps the joint story visible even when separate component models are convenient.

Expected loss is a mean. Unexpected loss describes dispersion around the mean at a specified confidence and horizon. Pricing and provisioning are linked mainly to expected loss; capital is concerned with tail loss and resilience. The distinction explains why accounting ECL and IRB capital cannot be reconciled by forcing one PD number into every system.

## Four useful statistical formulations

Classification asks whether an event occurs inside a window: default within twelve months after an observation date. Regression asks how much is lost or drawn: workout LGD, CCF or recovery cost. Survival analysis asks when default occurs and handles right-censoring. Multi-state analysis allows transitions among current, delinquent, default, cure, prepayment and closure. The business question chooses the formulation.

A valid row needs at least five dates or concepts even if they collapse to fewer columns:

- an entity or facility identifier;
- an observation date at which predictors are frozen;
- an outcome window start and end;
- a target definition with default, cure, prepayment and missing-outcome rules;
- a data-availability timestamp stating when each predictor was actually knowable.

The last item is the difference between historical data and decision data. A bureau score generated two days after the application can be useful for retrospective analysis but is leakage if the production decision had already been made. A field corrected during collections must not replace the origination value in the development snapshot.

## Static, dynamic and forward-looking risk

A static application score uses information at origination. A behavioural model updates risk from payment, utilisation and transaction history. A lifetime model produces a term structure rather than one probability. An accounting engine overlays reasonable and supportable macroeconomic scenarios and discounts expected shortfalls. The systems can share features and infrastructure while retaining different targets and governance.

Time changes validation. Random splitting assumes exchangeability and usually exaggerates confidence when policy, economy, channels or data systems evolve. The preferred design is development, validation and out-of-time test samples, separated by observation date and followed until outcomes mature. Random or cross-validation remains useful inside the development period for tuning, but it does not replace temporal challenge.

## From probability to action

A PD is not a decline. It becomes relevant only with loss severity, exposure, margin, operating cost, affordability, risk appetite, constraints and customer-treatment rules. A compact expected application value is

`(1 − PD) × performing margin − PD × LGD × EAD − acquisition cost`.

This is not a complete valuation: funding, capital, prepayment, utilisation, collections, taxes and timing matter. Its value is conceptual. It prevents the team from optimising AUC while ignoring value and it shows why the same PD can imply different actions for two products.

Threshold analysis must use matured outcomes and a policy simulation. Notebook 04 calculates approval rate, approved default rate and realised teaching profit across candidate PD cut-offs. The optimum in a historical sample is not automatically a production cut-off. It is an estimate subject to uncertainty, selection effects and changing prices. Policy should be stress-tested and constrained before approval.

## First executable model

The repository's baseline pipeline generates a point-in-time synthetic portfolio, deliberately introduces known defects, executes quality gates, quarantines invalid records, uses an out-of-time split, fits a logistic model, evaluates it, calculates a simplified ECL, measures drift and sends evidence to a bounded monitoring agent.

```python
from creditriskbook.workflows import run_end_to_end

result = run_end_to_end("synthetic_retail", n_rows=5_000, seed=42)
assert not result["quality_after"]["critical_failure"]
assert result["agent"]["human_approval_required"]
```

The small interface conceals no automation authority. The agent may recommend investigation, but its prohibited actions include approval, decline, price or limit changes, unapproved retraining and deployment. This separation is as important as the model metric.

## Model limitations are part of the result

The baseline is intentionally incomplete. One-hot encoding does not create a traditional scorecard. A constant-hazard lifetime approximation does not model monthly marginal PD. The synthetic data do not validate economic relationships. A random split is used when public data have no time field. Each simplification is named in the returned evidence and in the dataset contract.

The operating principle for the rest of the book is: make the assumption executable, make the limitation reviewable, and make every material action require authority.

## Chapter deliverable

Run `examples/end_to_end.py` and save the JSON output. Draw a one-page system boundary containing source data, observation snapshot, target builder, model, calibration, decision rule, downstream accounting/capital use, monitoring and human approvals. For every arrow, state the owner, timing, unit of measure and failure response.


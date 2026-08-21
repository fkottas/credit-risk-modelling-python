# Technical Workbook — End-to-End Python Patterns

The chapter examples introduce one concept at a time. This workbook connects them into longer analytical builds. Each workshop begins with a control question, creates an inspectable artifact, and finishes with tests that a second person can reproduce. Code fragments use the repository APIs and intentionally retain intermediate tables. A production team would add institution-specific authentication, storage, orchestration and approvals; those missing layers are named rather than hidden.

## Workshop 1 — Build a lawful, point-in-time development table

### Start with purpose and an eligibility waterfall

Assume a lender wants an application PD for new unsecured personal loans, predicting the defined default event within twelve months of booking. The unit is one booked facility at origination. The model will support a recommendation inside a wider affordability and policy process; it will not determine affordability. Exclude employees, fraud cases, test records, restructures, missing consent where required, accounts without a complete outcome window and products outside the mandate. Retain counts and exposure after every filter.

The waterfall is not clerical. Excluding accounts with incomplete outcomes changes the calendar composition. Excluding suspected fraud after seeing the outcome can remove adverse events selectively. Define exclusions before analysis and preserve the original reason. If the model will score applications but develops only on accepted, booked applicants, explicitly record acceptance and take-up selection.

```python
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class SamplePolicy:
    decision_cutoff: pd.Timestamp
    performance_months: int = 12
    products: tuple[str, ...] = ("personal_loan",)

def eligibility_waterfall(frame: pd.DataFrame, policy: SamplePolicy):
    steps = []
    work = frame.copy()
    for name, mask in [
        ("valid_key", work["application_id"].notna()),
        ("eligible_product", work["product"].isin(policy.products)),
        ("not_test", ~work["is_test_record"]),
        ("decision_period", work["decision_at"] <= policy.decision_cutoff),
        ("complete_outcome", work["outcome_complete"]),
    ]:
        before = len(work)
        work = work.loc[mask.loc[work.index]].copy()
        steps.append({"step": name, "before": before, "after": len(work)})
    return work, pd.DataFrame(steps)
```

### Define two clocks

A source record can have an event time and an ingestion time. A bureau balance observed on 31 January but delivered on 3 February was not available to a 1 February decision unless the actual system had another feed. A correction received later must not overwrite historical decision evidence in development. Store both timestamps and join using the availability rule that production can reproduce.

For each application, select records with `available_at <= decision_at`; among them choose the latest valid event under the source policy. Retain `feature_age_days`, source version and chosen record ID. Reject impossible future event dates even if their ingestion time appears valid. If the production feature store snapshots values, development should reconstruct that snapshot rather than design an idealised join.

```python
def point_in_time_join(applications, bureau):
    left = applications.sort_values("decision_at")
    right = bureau.sort_values("available_at")
    joined = pd.merge_asof(
        left,
        right,
        left_on="decision_at",
        right_on="available_at",
        by="customer_id",
        direction="backward",
        allow_exact_matches=True,
    )
    invalid = joined["bureau_event_at"] > joined["decision_at"]
    if invalid.fillna(False).any():
        raise ValueError("Bureau event occurs after decision")
    joined["feature_age_days"] = (
        joined["decision_at"] - joined["bureau_event_at"]
    ).dt.days
    return joined
```

`merge_asof` requires sorted keys and handles one timestamp dimension; real implementations may need source-effective intervals, restatements and tie-breaking. Test same-time records, time zones, daylight-saving transitions, duplicates and customers without history.

### Target construction

Create an outcome event table with event type, event date, reversal/cure status and source. Apply the approved default definition at obligor or facility level. The target is `1` if first default falls after booking and on or before the twelve-month horizon. An event already known at application may make the record ineligible rather than a future default. Record target derivation reason and first event date.

Do not use “ever defaulted” when the purpose is twelve-month PD. Do not label incomplete survivors as non-default. If early prepayment removes observation, decide whether it is censoring, a competing event or a valid non-default according to the modeling purpose. The choice affects the population and must match later interpretation.

### Contract and quarantine

The final table contract includes unique application ID, decision and booking timestamps, product, requested/approved amount, decision-time features, target, outcome-complete flag and provenance fields. Rules check uniqueness, non-null required values, valid categories, reasonable ranges, chronological consistency and aggregate reconciliations. A critical failure returns no modeling dataset. Warnings enter an exception table with owner and due date.

Create a deliberately defective copy only after saving the clean generator parameters and hash. The defect manifest records defect ID, type, row keys and expected rule. Students should receive either the manifest after their attempt or a blinded scoring key. Never overwrite the clean base.

### Workshop evidence

Submit the purpose statement, source/licence record, eligibility waterfall, target specification, point-in-time test, contract results, exception table, clean hash and defect manifest. A reviewer selects ten rows—including a default, a prepayment, missing bureau data and a late correction—and reconstructs them manually. The workshop fails if the leaked “latest bureau” join is retained because it gives a better AUC.

## Workshop 2 — Engineer and freeze a scorecard from first principles

### Split before learning transformations

Use calendar-based development, validation and out-of-time samples where the data permit. All bin searches, category groups, WOE distributions, variable selection and coefficients are learned on development. Validation can tune a limited choice; the out-of-time sample evaluates the frozen choice. Apply development cuts unchanged to later samples.

Start with a feature register. For every candidate, record business definition, source, availability, expected relationship, missing meaning, special codes, units, plausible range, manipulation risk and owner. Exclude identifiers, post-decision values, target components and variables with unacceptable legal or operational use before calculating IV.

### Candidate bins

For continuous variables, create pre-bins after separating missing and special codes. Quantile pre-bins distribute observations but may collapse repeated values. Equal-width pre-bins retain scale but can create empty tails. ChiMerge repeatedly combines the adjacent pair with most similar good/bad composition. Minimum population and event/non-event rules prevent superficially dramatic sparse bins. Monotonic merging resolves adjacent bad-rate violations in a chosen direction but should not erase a credible U-shape without review.

```python
from creditriskbook.scorecard import BinningProcess, WOEEncoder

binning = BinningProcess(
    numeric_method="monotonic",
    max_bins=6,
    prebins=20,
    min_bin_fraction=0.04,
    min_events=5,
    monotonic_trend="auto",
)
binned_dev = binning.fit_transform(X_dev, y_dev)
binned_val = binning.transform(X_val)
binned_oot = binning.transform(X_oot)

woe = WOEEncoder(smoothing=0.5)
W_dev = woe.fit_transform(binned_dev, y_dev)
W_val = woe.transform(binned_val)
W_oot = woe.transform(binned_oot)
```

Review all cut points. Exact boundary semantics matter: if 30 belongs to `(20, 30]`, both documentation and implementation tests must say so. Missing is not automatically worst or neutral. Special codes do not enter numeric order. Categorical groups should be economically coherent and disjoint. Production unseen values follow an explicit `OTHER` mapping and trigger counts.

### WOE audit

For bin `j`, calculate smoothed good and bad distributions and `log(good_share / bad_share)`. With target 1=bad, positive WOE indicates lower relative risk. Calculate IV as the sum of distribution difference times WOE. Recompute at least one variable independently from raw counts. Verify distributions sum to one and all WOE values are finite. Inspect the effect of smoothing in sparse bins.

WOE produces a piecewise-constant univariate transformation. It does not make the relationship causal and does not resolve correlation between characteristics. Compare WOE across validation and out-of-time data using the frozen bins. Large changes can indicate population movement, instability or source change.

### Fit IRLS and examine the path

The repository IRLS estimator forms the design matrix with an intercept, calculates stable logistic probabilities, gradient and penalised information matrix, and iterates the Newton update until coefficient and likelihood tolerances are met. L2 applies to slopes, not the intercept. Store convergence flag, iterations and final diagnostics.

```python
from creditriskbook.scorecard import IRLSLogisticRegression

logit = IRLSLogisticRegression(l2=1e-3, max_iter=100, tolerance=1e-8)
logit.fit(W_dev, y_dev)
assert logit.converged_
pd_dev = logit.predict_proba(W_dev)[:, 1]
pd_oot = logit.predict_proba(W_oot)[:, 1]
```

Under the good-to-bad WOE convention, a stable risk characteristic often receives a negative coefficient. A positive sign may reflect correlation, a weak or unstable characteristic, reversed event definition or a genuine conditional effect. Investigate with univariate and multivariable fits, VIF, bootstrap and time splits. Do not reverse a sign manually to make a table look familiar.

### Scale and reconcile points

Set base score, PDO and base good-to-bad odds. Calculate factor as `PDO/log(2)` and offset from the base point. Because the logistic model predicts bad log odds, score is offset minus factor times logit. Allocate intercept and each coefficient–WOE product into row components. Preserve raw unrounded points, then apply the documented rounding method and any minimum/maximum.

For each golden case, reconcile raw characteristic points to raw total, raw total to rounded score, score to implied odds and odds to model probability. Doubling good odds must increase score by exactly one PDO before rounding. Test every bin edge and rating boundary. Reasons select the largest point penalties relative to the best available bin for each characteristic; they do not describe policy failures such as affordability.

### Freeze artifact

The artifact contains feature order, raw definitions, bin specifications, WOE values, smoothing, coefficient vector, scale, grade map, reason labels, package version, training metadata and hash. JSON serialization needs stable numeric precision and schema versioning. Scoring validates the schema; it does not silently reorder unknown input or relearn transformations.

The evidence pack includes the characteristic presentation, bin decision memo, correlation/VIF review, coefficient table, performance/calibration, score reconciliation, grade design and golden test file. An independent reviewer must reproduce at least one score from raw values using only the artifact documentation.

## Workshop 3 — Produce a characteristic and model-review presentation

### Design for challenge, not decoration

A characteristic pack is the bridge between code, business knowledge and approval. Begin with population, dates, target, sample split, event rate, exclusions and model purpose. A summary table lists each candidate variable, source, timing, missing rate, bins, IV, coefficient sign, out-of-time stability and decision. The next slides present one characteristic at a time. Put the statistical chart beside the exact table so a reviewer can detect sparse bars or truncated axes.

The repository exporter creates editable slides from the fitted scorecard. Its chart uses fixed-bin bad rates and its table includes core counts, WOE and points. It intentionally leaves judgement fields for the modeller: definition, expected direction, cut rationale, time comparison, concerns and recommendation.

```python
from pathlib import Path
from creditriskbook.scorecard import export_characteristic_presentation

output = Path("artifacts/reports/characteristic_review.pptx")
export_characteristic_presentation(scorecard, output)
assert output.exists() and output.stat().st_size > 0
```

### Review one variable in depth

For debt-to-income, verify numerator and denominator, income frequency, negative/zero treatment, joint applicants and as-of date. Plot development and out-of-time population share and bad rate under identical cuts. Show WOE with the book’s sign convention. Report coefficient and points after controlling for other features. If the missing bin is unexpectedly low risk, determine whether missingness reflects a channel, prior policy or data defect.

Write a decision paragraph: “Retain with cuts X because the relationship is stable and economically credible; cap only impossible ratios under rule Y; monitor missing share and top-bin PSI monthly.” Avoid “retain because IV is strong.” For a rejected variable, state whether rejection is legal, timing, leakage, instability, redundancy, manipulation or data quality.

### Present score-level performance

Use distinct pages for discrimination, calibration, stability and economics. AUC/AR and KS describe ranking, not probability accuracy. Calibration includes predicted and observed rates by band with counts and uncertainty. Stability uses fixed scores/grades and separates population shift from performance. Economics uses an explicitly simulated policy with costs and assumptions.

Include a model comparison matrix with identical samples. Report logistic raw benchmark, WOE scorecard and challenger. If XGBoost has higher AUC but poorer calibration or unstable explanations, show all outcomes. Do not choose a champion from a single metric. Include inference latency, missing handling, reason method, reproducibility and control complexity.

### Add implementation evidence

The final section shows one row from raw fields through bin, WOE, logit, PD, points, grade and reasons. Add counts for boundary, missing, special and unseen tests. List artifact and code versions. Show the approved-to-implemented comparison and exact tolerance. A screenshot of the service is not enough.

### Presentation quality controls

Every axis has units, period and sample. Tables identify denominators. Percentages specify count- or exposure-weighting. Colours are not the only way to distinguish status. Text remains readable when exported to PDF. Source and licence appear near external dataset results. Confidential fields and row-level personal data are absent. Draft judgements are labeled and unresolved findings are visible.

The workshop deliverable is the editable presentation plus a machine-readable table underlying every chart. A reviewer selects two numbers per slide and traces them to code output. The test catches a common failure: charts refreshed from new data while pasted conclusions remain old.

## Workshop 4 — Compare logistic and XGBoost on one probability and score framework

### Establish a fair comparison

Use the same unit, target, eligibility, feature availability and out-of-time sample. A challenger may use different transformations but cannot receive newer information. Freeze the hyperparameter search and preprocessing inside the development/validation process. Keep the out-of-time set unavailable until the selected configurations are final.

Fit a simple raw logistic benchmark, the from-scratch scorecard and XGBoost. Handle categorical values with a reproducible encoder fitted on development or use the project’s chosen representation. Apply monotonic constraints only to features with a stable directional expectation; an incorrect constraint can hide a real interaction or a data problem. Record early-stopping iteration and random seed.

```python
from xgboost import XGBClassifier

challenger = XGBClassifier(
    n_estimators=800,
    learning_rate=0.03,
    max_depth=3,
    min_child_weight=20,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=5.0,
    eval_metric="logloss",
    random_state=404,
)
challenger.fit(X_dev_encoded, y_dev, eval_set=[(X_val_encoded, y_val)], verbose=False)
raw_pd = challenger.predict_proba(X_oot_encoded)[:, 1]
```

### Calibrate without contaminating evaluation

Tree probabilities often need recalibration. Fit Platt, intercept/slope or isotonic calibration on a held-out calibration sample or through cross-fitting. Isotonic is flexible but can overfit a small sample and create steps. Platt imposes a sigmoid. Intercept-only calibration preserves slope and adjusts central tendency. Compare reliability tables, calibration intercept/slope, Brier and log loss on untouched out-of-time data.

Do not recalibrate separately for every result table. The calibrated artifact is a versioned component with its own training window. Preserve raw and calibrated PD for diagnosis. If portfolio mix changes, a simple intercept update may be appropriate only after validation of ranking and slope.

### Map both models to a common score

Apply the same `ScoreScale` to calibrated PD. A score of 650 then represents the same implied odds regardless of the estimator. This supports common rating and cutoff reporting. It does not make XGBoost additive or give it scorecard bin points. For the logistic scorecard, component points sum exactly. For XGBoost, use SHAP values in log-odds space or controlled sensitivity and label the explanation method.

```python
from creditriskbook.scorecard import ModelScoreMapper, ScoreScale

scale = ScoreScale(base_score=600, pdo=50, base_odds_good_to_bad=20)
mapper = ModelScoreMapper(scale=scale).fit(calibrator, feature_names=X_dev_encoded.columns)
xgb_score = mapper.score_from_pd(calibrated_pd)
```

Check the actual class signature in the repository before copying the illustrative composition above; APIs are tested and documented by version. The invariant is the probability-to-score formula, not a particular wrapper.

### Evaluate decision consequences

Report AUC/AR, KS, lift at relevant capacity, Brier, log loss and calibration with intervals. Compare PSI of score and major features. Simulate the same cutoff or the same approval rate, because comparing two arbitrary cutoffs confounds model and policy. Calculate expected loss and margin under sensitivity ranges for LGD, take-up and operating cost. Tabulate applicants whose decisions change and investigate their characteristics.

Assess subgroup outcomes where lawful and appropriate. Differences require contextual review of labels, sample, policy and potential proxies; a single fairness ratio is not a complete conclusion. Document unavailable attributes and the limits of the audit.

### Champion decision

The committee matrix includes predictive benefit, calibration, stability, data dependencies, explanation faithfulness, latency, resilience, monitoring, change frequency, implementation complexity and customer impact. Approve the challenger only if benefit is material under the intended decision and controls are adequate. Otherwise retain it in shadow mode, use it as a benchmark or reject it. The evidence pack retains the rejected alternative and rationale to avoid repeating an unproductive search.

## Workshop 5 — Construct survival and lifetime-PD curves

### Build the event history

Create one row per account containing start date, first default date, censor date, competing event date and segment. The effective end is the earliest applicable event or observation cutoff. Duration must be positive and consistent with the chosen interval. A customer still performing at cutoff is right-censored, not a non-default for all future time. A prepayment can be a censoring or competing event depending on the estimand; write that choice before fitting.

Create an origination-cohort table with accounts entering the risk set. For each month, count those at risk immediately before events, first defaults and censorings. Kaplan–Meier updates survival by multiplying `1 - defaults/risk_set` over event periods. Cumulative default is one minus survival only when default is the event of interest and competing risks are handled consistently. With material prepayment, a cause-specific or cumulative-incidence treatment may be needed.

```python
import numpy as np
import pandas as pd

def kaplan_meier(duration, event):
    frame = pd.DataFrame({"duration": duration, "event": event}).sort_values("duration")
    times = np.sort(frame.loc[frame["event"].eq(1), "duration"].unique())
    survival = 1.0
    rows = []
    for time in times:
        at_risk = int((frame["duration"] >= time).sum())
        defaults = int(((frame["duration"] == time) & (frame["event"] == 1)).sum())
        survival *= 1.0 - defaults / at_risk
        rows.append({"time": time, "risk": at_risk, "defaults": defaults,
                     "survival": survival, "cumulative_pd": 1.0 - survival})
    return pd.DataFrame(rows)
```

Verify the first periods by hand. Report the risk set beneath the curve: the tail is unreliable when few accounts remain. Compare cohorts only over horizons that each can support. Confidence intervals and censoring assumptions belong beside the estimate.

### Expand to discrete-time rows

For a conditional model, create an account-period row for every interval the account is at risk. The target is one only in the first-default period. Include duration functions or interval indicators to represent baseline hazard. Features must be measured at or before the start of each interval; behavioural variables cannot use the end-of-month delinquency that defines the target.

Fit logistic or complementary-log-log hazard. Convert hazards `h_t` to survival `S_t = product(1-h_k)`, marginal PD `S_(t-1) h_t` and cumulative PD `1-S_t`. Test non-negative marginal probabilities, monotonic cumulative curves, and equality between marginal sum and cumulative endpoint. A horizon PD derived from independently fitted binary models can violate these identities; curve construction prevents that inconsistency.

### Calibrate and scenario-adjust

Choose whether the baseline is PIT, TTC-oriented or observed cohort experience. Calibrate to a target while preserving shape using hazard scaling or a parameter model. An odds shift applied at each period does not have the same effect as multiplying cumulative PD. Document the transformation and solve for its parameter to match the target endpoint.

For macro scenarios, link economic variables to period hazard or a latent score. Recalculate the complete survival curve under each scenario; do not multiply cumulative PD until it exceeds one and clip silently. Scenario-weighted marginal probabilities remain the correct inputs to period ECL. Preserve base and scenario curves for attribution.

### Rating migration route

An alternative lifetime approach uses a transition matrix among performing grades and default. Validate that rows sum to one and probabilities are non-negative. Matrix powers imply multi-period transitions only under the time-homogeneous Markov assumption. Compare implied one-year defaults with assigned grade PD and observed rates. If a macro-conditioned matrix changes by scenario, ensure it remains stochastic and plausible.

### Validation

Backtest at horizons for which outcomes have matured. Compare predicted cumulative default with cohort estimates, calibration by risk group, time-dependent discrimination and survival Brier score. Investigate censoring and prepayment shifts. The workshop produces event-history contract, KM table, hazard model, curve identities, scenario curves and limits. It fails if the last observed default rate is extrapolated flat without a stated assumption.

## Workshop 6 — Reconstruct workout LGD and revolving EAD

### Workout ledger before modeling

Use `synthetic_recovery` to obtain defaults, cash transactions, collateral proceeds, costs, cures and observation cutoffs. One default case may have multiple cash flows. The ledger key includes default episode and cash-flow ID. Amount signs and types are explicit: recoveries reduce loss, direct/indirect workout costs increase loss, and post-cure contractual payments follow the policy definition. Never infer sign from a free-text description.

Reference EAD is measured under the approved default definition. Discount each eligible cash flow from its date to default using the documented rate and day-count. Workout LGD is `(EAD - PV(net recoveries)) / EAD` under the chosen convention. Values can fall below zero or exceed one before policy treatment; retain raw values and reasons. Capping changes the target and must occur in a documented layer.

```python
from creditriskbook.data import load_case_dataset

case = load_case_dataset("synthetic_recovery", n_rows=3_000, seed=606)
ledger = case.frame.copy()
ledger["years"] = (ledger["cashflow_date"] - ledger["default_date"]).dt.days / 365.25
ledger["discount_factor"] = (1.0 + ledger["discount_rate"]) ** (-ledger["years"])
ledger["pv_cashflow"] = ledger["cashflow_amount"] * ledger["discount_factor"]
```

Check the case schema because the generator may return related tables or normalized columns by version. The calculation principle remains: preserve cash-flow identity and reconcile to account totals.

### Cure and incomplete cases

Cure requires performance over a defined period, not a temporary move below a DPD threshold. Record cure date, re-default and treatment of payments. Excluding cured accounts overstates LGD; treating every temporary cure as zero loss understates it. Report cure as a separate process and integrate according to the model design.

Recent defaults are right-truncated: future recoveries are unobserved. A “matured only” sample can overrepresent quick resolutions. Compare mature cohorts, unresolved share and recovery-development curves. Apply explicit completion estimates or sensitivity rather than coding outstanding recoveries as zero without comment.

### LGD candidates and calibration

Begin with portfolio and segment means. Fit a two-part model if the distribution has masses at cure/zero and continuous positive loss. Evaluate currency-weighted bias, account-weighted MAE, band calibration and tails. Check predicted values before bounds. Calibration may target a long-run or downturn parameter depending on use; IFRS 9 PIT LGD, economic pricing LGD and regulatory downturn LGD are different artifacts even if built from the same ledger.

### Revolving EAD reference table

For each facility, choose a reference date before default, current balance, limit and undrawn amount. Retrieve balance immediately before default under a consistent rule. Drawdown is default balance minus reference balance. Raw CCF is drawdown divided by reference undrawn amount. Zero-undrawn accounts need a separate EAD approach. Limit cuts, freezes and over-limit balances have operational meaning and should be flagged, not washed away.

```python
revolving = load_case_dataset("synthetic_revolving", n_rows=5_000, seed=607).frame
revolving["undrawn"] = revolving["limit_at_reference"] - revolving["balance_at_reference"]
valid = revolving["undrawn"] > 0
revolving.loc[valid, "raw_ccf"] = (
    revolving.loc[valid, "balance_at_default"]
    - revolving.loc[valid, "balance_at_reference"]
) / revolving.loc[valid, "undrawn"]
```

Inspect the actual generated column names and use the dataset metadata; the fragment expresses the raw identity. Reconcile modeled EAD as current drawn plus modeled conversion of undrawn. Validate currency EAD because a small CCF error on a large limit may dominate.

### Joint component review

Segment PD, LGD and EAD consistently where joint conditions matter. Stress can raise default incidence, collateral shortfall and drawdown together. A common shortcut multiplies independent stressed averages; compare it with account/scenario-level products. Report dependency sensitivity rather than claiming the public or synthetic sample identifies a universal correlation.

The workshop evidence includes recovery ledger reconstruction, cure and incomplete-case analysis, discount sensitivity, raw/model LGD, revolving reference contract, CCF exception table, EAD validation and joint stress. Independent reviewers rebuild one LGD and one CCF from source events.

## Workshop 7 — Run and reconcile an IFRS 9 ECL close

### Freeze the reporting perimeter

Begin with reporting date, legal entity, portfolios, financial instruments, accounting classification, currency and source cutoff. Reconcile gross carrying amount and undrawn commitments to the controlled subledger before applying risk parameters. Record exclusions and manual positions. A model total cannot compensate for an incomplete perimeter.

The input schedule has account, reporting stage indicators, contractual period, marginal baseline PD, LGD, projected EAD or cash shortfall basis, discount factor and scenario segmentation. Periods use one consistent unit. Origin and current risk measures used for SICR are comparable. Store stage reason flags, not only the number.

### Assign stage under policy

Apply default/credit-impaired indicators first, then DPD backstops and qualitative SICR indicators, then quantitative relative/absolute deterioration and low-credit-risk treatment if applicable. Order matters when several indicators fire, although all reasons should remain visible. Cure and probation prevent immediate oscillation. Compare account and exposure counts by reason with the prior close.

```python
from creditriskbook.ifrs9 import StagingPolicy, assign_stages

policy = StagingPolicy(
    stage2_dpd_backstop=30,
    stage3_dpd_backstop=90,
    relative_pd_threshold=2.0,
    absolute_pd_increase=0.02,
)
staged = assign_stages(account_snapshot, policy=policy)
print(staged.groupby(["stage", "stage_reason"])["ead"].agg(["count", "sum"]))
```

Configuration fields may differ by version; use the tested package signature. The review focus is traceable policy and precedence.

### Prepare curves and scenarios

Validate baseline cumulative curves: start at zero or the defined first period, remain non-decreasing and stay below one. Convert to marginal first-default probability. Prepare period LGD and EAD using information consistent with each scenario. Scenario weights are approved, non-negative and sum to one. The downside is not merely a scalar if macro paths have timing.

```python
from creditriskbook.ifrs9 import ECLConfig, Scenario, calculate_ecl

scenarios = [
    Scenario("upside", 0.20, pd_multiplier=0.80, lgd_multiplier=0.95),
    Scenario("base", 0.55, pd_multiplier=1.00, lgd_multiplier=1.00),
    Scenario("downside", 0.25, pd_multiplier=1.55, lgd_multiplier=1.15),
]
result = calculate_ecl(contractual_schedule, scenarios, ECLConfig())
```

Stage 1 uses default risk associated with defaults possible in the next twelve months while expected cash shortfalls reflect the relevant timing. Stage 2 applies lifetime ECL. Stage 3 treatment depends on accounting policy and effective-interest presentation. Revolving facilities may require expected exposure beyond contractual cancellation where the applicable requirements and policy indicate [R17].

### Reconcile four directions

First, sum period detail to account/scenario. Second, probability-weight scenarios to account total. Third, sum accounts to stage, product and portfolio. Fourth, reconcile current closing allowance with opening plus provision, write-offs, FX, transfers and other movements. Differences must fall within a defined currency/rounding tolerance. Retain account rows for drill-down and aggregate rows for financial control.

Use `result.detail`, `result.scenario_summary`, `result.account_summary` and `result.reconciliation` according to the package version. Check weights and duplicates before calculating. Verify a hand-worked account from marginal PD through discounting. Compare engine output with an independent spreadsheet for a small golden set; a spreadsheet is a test oracle only after its formulas are reviewed.

### Explain movement and overlay

Attribute change to volume, stage, PD, LGD, EAD, scenario, time passage, model and data as the organisation defines them. Sequential waterfalls depend on order, so state the method. Keep management overlays in a ledger outside base model output. Each overlay has evidence, gap, scope, method, sign, amount, owner, approval, expiry and backtest. The final allowance equals model output plus approved adjustments and reconciles to posting.

### Close controls

Run reasonableness comparisons with balances, default rates, stage movement, prior allowance and stress sensitivity. Validate source freshness and model versions. Require development/model owner, independent review, accounting owner and posting approval according to governance. Archive the exact input hashes, configuration, outputs, code commit and approvals. The workshop fails on unreconciled “immaterial” differences without a defined materiality rule.

## Workshop 8 — Calculate and challenge Basel IRB capital

### Separate exposure mapping from formula execution

Create an exposure register with obligor, facility, legal entity, regulatory approach, asset class, default status, PD, LGD, EAD, maturity, sales and credit-risk mitigation. Approval to use IRB and local implementation are fields, not assumptions. Validate obligor aggregation and default definition. Route ineligible or unmapped rows to exception rather than choosing “corporate” as a default category.

The repository illustrates corporate, SME corporate and selected retail risk-weight functions. The Basel formula uses prescribed correlations and a high systematic-factor quantile to calculate conditional loss, adjusts for expected loss and in some cases maturity, then scales capital to RWA. Review the current official CRE chapters and applicable jurisdiction before reporting [R1–R4].

```python
from creditriskbook.irb import irb_capital, summarise_irb_audit

audit_rows = irb_capital(
    pd=portfolio["pd"],
    lgd=portfolio["lgd"],
    ead=portfolio["ead"],
    maturity=portfolio["maturity"],
    asset_class=portfolio["asset_class"],
    annual_sales_eur_m=portfolio["annual_sales_eur_m"],
)
summary = summarise_irb_audit(audit_rows)
```

### Audit inputs and transformations

PD cannot be zero; apply the correct regulatory floors in the governed input layer and retain pre-floor values. LGD must match seniority, collateral, workout and downturn requirements. EAD and CCF must reflect the facility and approach. Effective maturity has a defined treatment and bounds. SME sales adjustment requires valid consolidated sales under the framework. Defaulted exposures use separate treatment.

Store every intermediate: input before/after floor, correlation, maturity factor, conditional term, capital requirement, scaling and RWA. A reviewer reproduces rows using an independent calculator. Vectorised code can hide a branch mismatch, so golden cases cover each asset class, minimum/maximum values, missing sales and default status.

### Parameter calibration evidence

For PD grades, reconcile obligors, defaults, years and representativeness. Calculate observed rates and long-run average with economic-cycle coverage. Calibrate central tendency while preserving sensible rank order. Apply named conservatism for identified uncertainty. Do not use a general buffer to absorb a target-definition defect.

For LGD, reconcile workout data, costs, discounting, cures, incomplete cases and downturn adjustment. For EAD, reconstruct raw CCF and exceptions. Parameter ownership and use test matter: ratings should inform risk management, not exist only for capital. Overrides are reasoned, approved and monitored.

### Portfolio checks

Aggregate EAD and RWA by asset class, grade, geography, industry, collateral and legal entity. Reconcile to source exposure and prior period. Explain movement through volume, mix, rating/PD, LGD, EAD, maturity, approach and rules. Compare simple sensitivities: one-notch downgrade, PD multiplier, LGD stress and large-name default. Concentration is reviewed separately because the IRB formula and average RWA do not fully describe name/sector tail risk.

### Floors and regulatory reporting boundary

The generic library does not apply every jurisdictional input/output floor, transitional arrangement or reporting rule. Build those in a controlled reporting layer with effective dates and legal references. Keep formula result, adjusted result and final reported amount distinct. Never alter base model parameters simply to hit an output floor.

The workshop deliverable is exposure mapping, permission evidence, parameter waterfall, row audit, independent formula reproduction, portfolio reconciliation, movement, sensitivity and regulatory-gap checklist. Sign-off requires capital/regulatory policy and independent validation, not only code review.

## Workshop 9 — Translate calibrated risk into controlled decisions

### Keep model, policy and economics separate

A PD model estimates an event probability under its definition. Policy combines PD with affordability, eligibility, fraud, exposure, concentration, customer protection and risk appetite. Economics estimates revenue and cost under take-up, repayment and loss assumptions. Implement these as separate versioned layers so a policy change does not masquerade as a model recalibration.

Create a decision waterfall with hard eligibility, data availability, affordability, credit-risk recommendation, manual review and final outcome. Every rule has owner, rationale, effective dates, source fields and reason code. If model input is unavailable, follow an approved fallback or stop; never replace missing income or bureau score with a silent zero in the decision layer.

### Expected-value surface

For a candidate offer, calculate expected interest and fee income net of funding and operations, expected loss using compatible PD/LGD/EAD, capital charge and acquisition cost. Include take-up and early prepayment. Avoid counting expected loss in both margin and capital cost. Discount timing where material. The result is scenario-dependent expected value, not realised profit.

```python
import numpy as np

def expected_value(pd_12m, lgd, ead, margin, operating_cost, capital_cost, take_up=1.0):
    revenue = take_up * margin * ead
    expected_loss = take_up * pd_12m * lgd * ead
    costs = take_up * (operating_cost + capital_cost)
    return revenue - expected_loss - costs

cutoffs = np.linspace(0.01, 0.25, 49)
```

Sort a held-out population by calibrated PD and simulate cutoffs. For each threshold report eligible volume, approval, expected booked exposure, expected loss, value, review workload and subgroup diagnostics. Compare at the same cutoff and at the same approval rate. Apply sensitivity to LGD, take-up, price elasticity and default calibration. A narrow optimum is unstable; prefer a robust region subject to constraints.

### Risk-based pricing

Construct a transparent break-even price from funding, expected loss, capital, liquidity, operations and target return. Respect legal, conduct and product caps. Higher rates may change take-up and borrower mix, so a static calculation can be self-defeating. Model adverse selection only with evidence and sensitivity. A price cannot turn an unaffordable or prohibited application into an acceptable one.

Use grades to simplify communication, but do not assume all accounts in a grade are identical. Retain account PD and price components. Overrides have narrow permitted directions and authority. Monitor override rate, reason, approver, subsequent performance and group outcomes.

### Limits and account management

For revolving products, line decisions change future EAD and behaviour. Simulate utilisation, expected drawdown, income and loss under current and proposed limit. Set maximum step, absolute exposure, recent delinquency and affordability constraints. Separate a customer-requested increase from a proactive offer. A model that recommends line increase does not execute it; policy and authorised systems control action.

### Manual review

Capacity is a constraint. Route cases based on uncertainty, missing evidence, policy exceptions or high value—not an unexamined score band alone. Measure queue time, reviewer consistency, overturns and outcomes. Manual review can introduce bias and leakage if its decisions feed future training without recorded reasons. Preserve pre-review model/policy recommendation and final human decision.

### Safe optimisation and experiments

An optimisation objective needs constraints for capital, loss, volume, service, concentration and customer outcomes. Report shadow prices and infeasible cases. Reinforcement-learning or bandit examples remain in simulation until exploration risk, delayed outcomes, confounding, off-policy evaluation, maximum actions and approval are addressed. Short-term spend is not an adequate reward when defaults mature later.

The workshop pack contains policy waterfall, economics definitions, cutoff surface, sensitivity, price decomposition, limit simulation, review design and governance approval. It explicitly labels predictions, assumptions and decisions. A committee can reject the strategy while approving the model.

## Workshop 10 — Deploy, monitor, and retire a model

### Package an immutable scoring contract

The approved model package includes schema, preprocessing, artifact, calibrated probability, score map, grade map and reasons. The service accepts a versioned request and returns model/policy versions, timestamp, PD, score, grade, reasons, warnings and correlation identifier. It validates names, types, ranges and categories. Unknown fields can be rejected or ignored under schema policy; required fields cannot be inferred.

Golden tests cover ordinary, boundary, missing, special, unseen, very large, malformed and duplicate cases. Training code and production entry point must match at every intermediate step. Exact floating-point tolerance, rounding and rating boundary are documented. Load testing measures percentile latency and error under representative concurrency. Resilience tests remove feature services and artifact storage.

```python
def golden_assertions(model, rows, expected):
    actual_pd = model.predict_proba(rows)[:, 1]
    actual_score = model.score(rows)
    assert np.allclose(actual_pd, expected["pd"], atol=1e-10, rtol=1e-9)
    assert np.array_equal(actual_score.to_numpy(), expected["score"])
```

### Release and rollback

Build a container or locked environment from a clean commit. Generate tests, dependency manifest and artifact hashes. Use distinct development, validation and production credentials. Deployment requires approved model and change records. A canary or shadow stage observes output without full impact. Rollback points to a known compatible service, model and policy combination; rolling back only code while leaving a new schema can fail.

Record who deployed, what, when, environment, commit, artifact, approvals and health results. No agent in this repository has deployment authority. A separate executor may act only after validating human approval and scope.

### Monitoring layers

Data monitoring checks volume, missing, freshness, ranges, categories, schema and cross-field rules before scoring. Population monitoring calculates fixed-bin feature/score shifts and segment mix. Model monitoring separates discrimination, calibration and outcome maturity. Decision monitoring observes approval, review, overrides, price, limits and fairness. Component monitoring tracks defaults, recoveries, cure, utilisation, CCF, stage, ECL and RWA as relevant.

Every metric has reference, denominator, weighting, frequency, threshold, owner and action. PSI is calculated with fixed bins and smoothing but interpreted alongside business context. An AUC decline can reflect sample, target delay, policy selection or true relationship change. Calibration can move while AUC remains stable. Source recoding may appear first as category/quality failure.

### Outcome maturity and backfill

Twelve-month PD outcomes are unavailable immediately. Use leading indicators without calling them final backtests. Maintain vintages so partial outcomes are compared at equal age. When events arrive late or are corrected, version the outcome table and rerun backtests under controlled restatement. Do not overwrite history silently.

### Alert-to-action workflow

An alert includes severity, affected population, evidence, likely cause, owner and deadline. Actions include collect evidence, source repair, restrict, fallback, recalibrate, redevelop or retire. Thresholds do not automatically choose action. Repeated waivers require escalation. Track time to acknowledge, investigate and close as control metrics.

### Change and retirement

Classify refactor, dependency, source, transformation, calibration, cutoff and model changes. Output-identical refactors still need regression and release review; source and target changes may require redevelopment. Retire when purpose ends, performance/control cannot be restored, product closes or replacement is approved. Archive artifacts, decisions, monitoring and lineage under retention policy; revoke credentials and stop jobs. A retired model may remain necessary to explain historical decisions.

The workshop produces API schema, golden set, UAT, release/rollback, dashboard contract, alert playbook, change matrix and retirement plan. An independent operator should be able to recover service without the developer improvising.

## Workshop 11 — Build a governed agentic assistant for credit risk

### Choose a bounded task

The assistant reads approved monitoring or data-quality evidence, asks a specialist to propose a permitted next step, applies deterministic policy and records the result. It does not score customers, change cutoffs, retrain, deploy or post ECL. Begin with an agent card: purpose, owner, evidence, tools, memory, actions, evaluation, fallback and change process.

Register evidence with ID, source, created time, classification and payload hash. The hash detects changes but does not establish truth. Only approved structured fields enter policy decisions. Free text, documents, column names and tickets are untrusted content and cannot redefine system instructions.

```python
from creditriskbook.agents import GovernedAgentOrchestrator

orchestrator = GovernedAgentOrchestrator()
outcome = orchestrator.run(
    "data_quality_agent",
    {"critical_failure": True, "failed_rules": ["point_in_time_join"]},
    evidence_source="quality/monthly/2026-08",
)
print(outcome.proposal.action)
print(outcome.policy_decision.decision)
```

The expected proposal is bounded and the policy may require human approval. The orchestrator never invokes a write executor.

### Deterministic permission boundary

The `AgentPolicy` uses deny by default. Allow-lists are exact structured action names, not prose similarity. Explicitly deny customer decision, pricing/limit change, retraining, deployment, evidence suppression, restricted export, regulatory parameter alteration and accounting posting. Read and recommendation actions have their own scopes. Unknown agents or actions are denied.

If a future executor is added, isolate its credentials. It verifies proposal hash, evidence references, human identity/role, exact scope, approval time and expiry. A modified proposal needs new approval. Rate, account, amount and environment limits apply. All material actions support emergency disablement.

### Specialist separation

A quality specialist interprets contract-rule results; a monitoring specialist interprets configured metrics; a validation specialist interprets open findings. They do not approve each other or share unrestricted tools. A documentation agent can draft from their evidence but marks missing information. Retrieval indexes are versioned and access-controlled. Memory is minimal and isolated by case.

### Audit-chain verification

The audit log stores event ID, time, actor, event type, payload digest and previous event digest. Verify the chain on every export. A hash-linked log is tamper-evident within its trust assumptions, not a substitute for secure immutable storage and identity. Log policy denials and tool failures as carefully as successes.

### Evaluate trajectories

Create ordinary and adversarial cases. Score task correctness, evidence support, unsupported claims, tool selection/arguments, permission compliance, approval integrity, latency, cost, recovery and reviewer override. A correct final recommendation reached after an unauthorised read fails. A safe refusal with a clear missing-evidence request may pass.

Red-team prompt injection in column names and retrieved documents, false regulator messages, stale evidence, exfiltration, privilege escalation, replay, proposal mutation, large population, tool timeout and partial results. Any prohibited action, secret exposure or unlogged external write is a release blocker. Re-run after foundation model, prompt, retrieval, tool, policy or workflow changes [R11, R12].

### Human interface

Present evidence source/time, metrics, proposed action, policy result, uncertainty and allowed responses. The reviewer can approve, reject or request evidence if authorised. Avoid automation bias: show limitations and conflicting evidence. Measure whether humans rubber-stamp, override consistently or lack time. Human-in-the-loop is a control only when the human has information, authority and a usable interface.

The workshop produces agent card, tool/evidence cards, policy tests, ordinary evaluation, red-team suite, audit verification, human-approval design, kill switch and incident procedure. The assistant is accepted for proposal support only; customer or production authority remains prohibited.

## Workshop 12 — Assemble and defend the capstone system

### Select compatible cases

Choose a lending product and primary PD dataset, then add a synthetic component dataset appropriate to the extension. For example, use South German credit for an attributed application-score exercise and original synthetic recovery for LGD. Do not pretend the borrowers or time periods connect. The capstone is a system demonstration, not an empirical claim about one real portfolio.

Write a one-page purpose and policy statement. Identify user, decision, population, target, horizon, frequency, materiality and exclusions. State whether outputs support underwriting, monitoring, accounting, capital, pricing or research. Define prohibited uses. Obtain instructor approval before modeling.

### Create the evidence index

Use a table with evidence ID, artifact, owner, status, commit/hash and chapter requirement. Minimum artifacts are legal-data record, contract, quality report, leakage test, sample waterfall, EDA, characteristic pack, scorecard artifact, challenger, calibration/grades, economics, component/ECL/IRB result, validation, UAT, deployment, monitoring, agent card/red team and model card. Missing evidence remains visible.

### Run the clean pipeline

From a new environment, execute download/generation, validation, feature build, split, benchmark, scorecard, challenger, calibration, evaluation and report. Save configuration and hashes. Run unit tests and notebooks. A second person repeats the commands. If a public source is unavailable, use a cached file only when its checksum and licence record match; otherwise document the blocked live test.

```python
from creditriskbook.workflows import run_end_to_end

evidence = run_end_to_end(
    dataset_key="synthetic_retail",
    n_rows=8_000,
    seed=1200,
    inject_defects=True,
)
print(evidence["rows"], evidence["pd_metrics"])
```

Treat the fragment as a repository-version example; inspect the returned evidence keys. The substantive requirement is a deterministic, tested workflow.

### Conduct independent challenge

Validation reconstructs target and ten rows, checks sample/feature timing, benchmarks the model, examines calibration/stability, recomputes scores/reasons and reviews limitations. Component validation rebuilds one LGD, CCF, ECL or IRB row. Implementation validation compares approved artifact with service output. Findings have severity, owner and due date. Developers respond with evidence, not deletion of inconvenient observations.

### Prepare committee alternatives

Present more than “approve.” Alternatives might retain the scorecard, use XGBoost only as benchmark, restrict a segment, recalibrate, collect more outcomes or stop. Quantify effects where possible. Identify legal/accounting/capital decisions outside the student’s authority. State residual uncertainty and compensating controls.

### Mock meeting

Assign chair, business owner, model owner, validation, data, engineering, compliance, accounting/capital and audit. Give members the pack in advance. Each states approve, condition, remediate or reject with reasons. Record dissent and exact conditions. The chair confirms no prohibited dataset or agent use. Conditional approval has owners and expiry; it is not indefinite acceptance.

### Final reproducibility and publication review

Remove secrets, personal data, downloaded files that cannot be redistributed, caches and oversized artifacts. Confirm every public result has attribution and limitation. Ensure generated notebooks are valid JSON and execute. Run lint, unit tests, manuscript checks and document render. Review the complete Word book and repository diff. Tag an edition only after evidence is green.

The capstone passes when the team can explain the full chain from lawful input to monitored, bounded use and can reproduce it. A sophisticated model with target leakage, broken ECL reconciliation, incorrect IRB mapping, untested deployment or autonomous customer action fails regardless of predictive metric.

## Workbook control summary

These workshops share five invariants. Definitions remain compatible from source to output. Transformations fit only on authorised development data and freeze for validation/scoring. Material totals reconcile from row to system. Software changes have tests and versions. Authority is explicit: models estimate, policy decides within governance, and agents propose within deterministic bounds. Students should carry these invariants into every alternative dataset or method they add.

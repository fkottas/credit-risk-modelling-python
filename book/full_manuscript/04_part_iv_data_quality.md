# Chapter 19 — Internal, Bureau, Alternative, Public, and Synthetic Data

## Begin with the decision and the population

A dataset is not a modelling problem until its decision, population, unit and time are defined. An origination PD model may use one row per application at decision time. A behavioural model may use one row per customer-month or facility-month. An LGD model needs a default episode and post-default cash flows. An IFRS 9 engine needs account-period schedules, contractual cash flows and forward-looking scenarios. The same column can therefore be valid in one case and leakage in another.

Let the intended population be $\mathcal{P}$, the decision time be $t$, the information available at that time be $\mathcal{F}_t$, and the outcome horizon be $h$. A twelve-month default model estimates

\[
p_i(t,h)=\Pr\left(Y_i(t,h)=1\mid X_i\in\mathcal{P},\mathcal{F}_t\right).
\]

Every dataset review asks whether observed records approximate this conditional population. A high AUC on a sample selected by an older approval policy does not prove validity for all current applicants. Formally, if $A_i=1$ means that the earlier policy accepted applicant $i$, development data often identify

\[
\Pr(Y_i=1\mid X_i,A_i=1),
\]

while the new decision requires $\Pr(Y_i=1\mid X_i)$. The missing outcomes for $A_i=0$ are a selection problem, not a software problem.

## What each source contributes

Internal application systems describe requested product, amount, affordability, declared income, decision, price and overrides. Core banking and servicing systems add balances, limits, payment obligations, payments, arrears, restructures and closures. Collections and legal systems provide strategies, costs, recoveries, collateral events and cure. Bureau sources broaden the view across lenders but add matching, latency, coverage, contractual and permissible-purpose constraints. Open-banking or transaction data can represent cash-flow behaviour only where consent, purpose limitation, minimisation, security and stable categorisation are established.

Alternative data such as device, location, telco or social signals can create privacy, proxy, stability, adverse-action and discrimination risks. A feature is not acceptable merely because it predicts. The institution needs a lawful basis, a defensible relationship to creditworthiness or affordability, an explanation, a retention policy and monitoring of differential impact.

Public datasets are teaching and infrastructure assets, not automatic evidence for a portfolio. The book intentionally switches datasets because each case needs a different observation unit:

| Dataset or generator | Unit and useful case | What it cannot establish |
|---|---|---|
| UCI South German Credit, CC BY 4.0 | application; manual scorecard and cost-sensitive PD | current population validity or out-of-time stability |
| UCI Taiwan credit card, CC BY 4.0 | customer; repayment-status features and ML comparison | current policy, geography or prospective time split |
| UCI Credit Approval, CC BY 4.0 | application; missing and mixed data types | default probability, because the outcome is approval |
| UCI Polish/Taiwan bankruptcy, CC BY 4.0 | firm; failure and low-event exercises | Basel default without a mapped default definition |
| HMDA public files | mortgage application; access, decision and pricing analysis | subsequent loan default |
| Fannie Mae/Freddie Mac performance files | mortgage-month; vintage, delinquency and prepayment | universal mortgage behaviour; raw redistribution rights |
| Project synthetic behavioural history | application, contract, facility-month and enquiry | empirical claims about any institution |
| Project recovery, IFRS 9, IRB and counterparty cases | specialist ledgers unavailable in a single open source | regulatory approval or accounting policy evidence |

## Synthetic data with an explicit mechanism

Synthetic does not mean arbitrary. A useful generator specifies support, dependencies, time and limitations. For example, an open contract must not have a closing date before its opening date; a monthly snapshot must not occur before opening; $DPD\ge 90$ should reconcile to the chosen default-status rule; balances should normally be non-negative; and future labels should depend on past risk, not on a random target unrelated to the features.

The course generator creates four separate tables: applications, contracts, monthly performance and bureau enquiries. It uses a latent propensity only to produce rational teaching directions. Recent DPD, utilisation and new-credit intensity increase generated default probability, while income reduces it. The laboratory first constructs miniature rows explicitly; the complete generator is then assembled progressively in the Chapter 19 source script and subsequent data chapters. This mechanism is original project code and is not estimated from a real lender.

Representative output for the fixed seed:

```output
(800, 7) (1937, 8)
(23193, 10) (1406, 4)
Project-generated synthetic teaching data
Original synthetic relationships are pedagogical ... and not calibrated to any lender.
```

These row counts are the executed result for seed 1901 in version 0.6.0 and are asserted in tests. The checksum covers all four tables and changes if any generated value changes.

## Source assessment and prohibited inference

For every field record the owner, original purpose, collection process, effective time, processing time, update frequency, coverage, permission, privacy class, quality controls and known structural breaks. Then write a prohibited-inference statement. HMDA may support approval-disparity analysis, but not mortgage PD. Credit Approval may test missing-data pipelines, but not reject-inference performance. Bankruptcy can support failure prediction, but not automatic Basel-default equivalence.

**Applied investigation.** Build a source inventory for application, bureau, fraud, servicing and outcome systems. Mark fields unavailable at decision time, fields that are policy outputs, fields that can proxy protected characteristics, and fields requiring legal review. Reject any source whose rights or purpose cannot be evidenced.

# Chapter 20 — Data Licences, Attribution, Privacy, and Reproducibility

## Public access is not permission

A file visible on the internet may still be copyrighted, subject to click-through terms, privacy-sensitive or incorrectly mirrored. A Kaggle page may display a licence, but competition rules, account terms and original-source rights still matter. An aggregator cannot grant rights that the original publisher did not possess. The safe process is source-by-source, not platform-by-platform.

The book's dataset registry records publisher, official URL, licence, redistribution condition, allowed cases, limitations, review date and status. Statuses distinguish approved, approved with a scope limit, conditional per series, conditional and not bundled, and excluded pending legal review. The rule is conservative: uncertainty stops redistribution; it does not become permission.

## A lawful-use decision table

| Question | Evidence | If evidence is absent |
|---|---|---|
| Who is the original publisher? | official landing page and DOI where available | do not rely on a mirror |
| What licence applies to this file/version? | licence text or provider terms captured at access | do not redistribute |
| Is commercial or educational reuse allowed? | explicit grant and constraints | use code-only access or exclude |
| Must users accept account or competition terms? | current click-through terms | each reader downloads independently |
| Are there personal or sensitive data? | disclosure control and privacy documentation | do not copy into the repository |
| Is attribution required? | licence and publisher citation | add attribution next to every result |
| Can upstream content change? | checksum, release date, schema version | fail closed on mismatch |

Checksums protect reproducibility, not legality. A hash proves which bytes were used. It does not prove a right to use them. Conversely, a permissive licence does not establish representativeness, target validity or fairness.

The laboratory defines `DatasetLicenceRecord` and `licence_gate` directly. Empty publisher, official URL, licence, redistribution rule or attribution blocks the record; an unresolved licence never becomes permission through silence. The live UCI adapter is introduced after readers can review this evidence structure themselves.

The expected licence is `CC BY 4.0`, and the attribution includes UCI and DOI `10.24432/C5X89F`. The adapter downloads from the reviewed UCI archive and rejects a file whose SHA-256 no longer matches. The repository does not quietly update the checksum; a changed file triggers human review.

## Reproducibility manifest

For run $r$, define a manifest

\[
M_r=(D_r,L_r,H_r,T_r,S_r,C_r,E_r),
\]

where $D_r$ is dataset identity, $L_r$ is licence evidence, $H_r$ is the content hash, $T_r$ is the extraction and transformation specification, $S_r$ is the split and seed, $C_r$ is the code commit, and $E_r$ is the environment lock. Reproducing a model means reproducing this tuple, not only rerunning a notebook with a similarly named CSV.

For revised macro data, store the release vintage when the provider permits it. For provider-controlled mortgage data, store the official release identifier and checksum locally but do not publish raw files if the terms do not grant redistribution. For Kaggle cases, the repository supplies a schema-validated adapter; the student supplies the file after reviewing and accepting the current terms.

## Privacy minimisation

Use the least detailed lawful field needed for the stated purpose. Keep secrets, credentials and personal data out of notebooks, logs, prompts, embeddings, model artefacts and screenshots. Tokenisation or hashing does not automatically anonymise data when linkage remains possible. Synthetic teaching data should be labelled synthetic and should not imitate named individuals.

**Applied investigation.** Compare UCI South German, a conditional Kaggle competition and Freddie Mac performance data. Decide separately whether analysis, download-by-code, local retention and redistribution are allowed. Record the evidence and the date of the decision.

# Chapter 21 — Relational Credit Data, Lineage, and Point-in-Time Joins

## One wide CSV hides the process

Credit behaviour is relational. One customer can have many applications; one customer can hold many contracts; one contract can generate many monthly snapshots and payments; and one customer can generate many bureau enquiries. Denote application, contract, performance and enquiry relations by $A$, $C$, $P$ and $B$. Their intended keys are

\[
K_A=(application\_id),\quad K_C=(contract\_id),
\]

\[
K_P=(contract\_id,snapshot\_date),\quad K_B=(enquiry\_id).
\]

A customer identifier is a foreign key, not necessarily a unique key. Treating it as unique in $P$ would discard valid months; joining $A$ directly to $P$ without aggregation would multiply application rows. If customer $i$ has $m_i$ contracts and contract $j$ has $n_{ij}$ months, the unaggregated join can create $\sum_j n_{ij}$ rows for one decision. Monetary totals then multiply unless the observation unit is restored.

![Relational credit data: four units linked by controlled keys](book/figures/data-relational-architecture.png)

## A contract is more than column names

A data contract states unit, key, type, domain, nullability, semantic meaning, currency, timezone, effective timestamp, processing timestamp, freshness, source, owner, privacy class, quality threshold and permitted consumers. Event time answers when the business event occurred. Processing time answers when the institution learned or stored it. Both matter when late corrections occur.

For a decision at $t_i$, a point-in-time join chooses the most recent source record whose effective time does not exceed the decision time:

\[
s_i^*=\max\{s:s\le t_i,\;key(s)=key(i)\}.
\]

If nothing satisfies the set, the result is missing; the join must not borrow the earliest future record. A staleness policy may also require $0\le t_i-s_i^*\le \Delta_{max}$.

## Derive the join before using a helper

```python
import pandas as pd

applications = pd.DataFrame({
    "customer_id": ["A", "B"],
    "decision_time": pd.to_datetime(["2025-01-10", "2025-01-12"]),
})
bureau = pd.DataFrame({
    "customer_id": ["A", "A", "B"],
    "bureau_time": pd.to_datetime(["2024-12-01", "2025-02-01", "2025-01-01"]),
    "utilisation": [0.30, 0.80, 0.45],
})

def point_in_time_lookup(left, right):
    rows = []
    for application in left.itertuples(index=False):
        eligible = right.loc[
            (right["customer_id"] == application.customer_id)
            & (right["bureau_time"] <= application.decision_time)
        ]
        chosen = eligible.sort_values("bureau_time").tail(1)
        rows.append({
            "customer_id": application.customer_id,
            "decision_time": application.decision_time,
            "bureau_time": chosen["bureau_time"].iloc[0] if len(chosen) else pd.NaT,
            "utilisation": chosen["utilisation"].iloc[0] if len(chosen) else None,
        })
    return pd.DataFrame(rows)

print(point_in_time_lookup(applications, bureau))
```

Expected output:

```text
  customer_id decision_time bureau_time  utilisation
0           A    2025-01-10  2024-12-01         0.30
1           B    2025-01-12  2025-01-01         0.45
```

The tempting value `0.80` is more recent in the database but did not exist for A's decision. Production code may use `merge_asof`, but the loop makes the set definition visible first. Tests must cover no match, equal timestamps, duplicate processing versions, staleness and a future record with an extreme value.

## Lineage and reconciliation

For every engineered feature store source table, source fields, filtering boundary, aggregation, missing-history policy, code version and consumers. Reconcile counts and money across joins. If contract balances are aggregated to customer level, verify

\[
\sum_i Balance_i^{customer}=\sum_j Balance_j^{contract}
\]

for the same as-of population, currency and exclusions. A difference can be legitimate only if its bridge is explicit.

After the fundamentals are clear, the student expands the hand table into an original relational case. The Chapter 21 script asserts unique application and contract keys, prevents duplicate contract-month rows and prints the selected effective timestamp. Only the later integration phase promotes the reviewed generator and join into the reusable package.

**Applied investigation.** Draw the key and cardinality map, make a deliberately multiplying join, reconcile its balance inflation, then replace it with an aggregation at the correct point in time.

# Chapter 22 — Observation Windows, Targets, and Leakage-Safe Samples

## Observation, buffer and performance windows

Let $t_i$ be the reference date for observation $i$, $w$ the lookback length, $g$ a reporting-lag buffer and $h$ the outcome horizon. A closed-right observation window is

\[
\mathcal{O}_i(w)=\{s:t_i-w<s\le t_i\},
\]

and a performance window can be defined as

\[
\mathcal{P}_i(g,h)=\{u:t_i+g<u\le t_i+g+h\}.
\]

For default event time $\tau_i$, the binary label is

\[
Y_i(t_i,g,h)=\mathbb{1}\{t_i+g<\tau_i\le t_i+g+h\}.
\]

The boundary convention matters. An event exactly six calendar months before $t_i$ is excluded by $(t_i-6m,t_i]$ but included by $[t_i-6m,t_i]$. The book uses open-left, closed-right windows and tests the boundary. Calendar-month offsets are not always equal to 180 days.

## Label maturity and censoring

At extraction date $T$, a label is mature only if $t_i+g+h\le T$, unless a censoring-aware method is used. Coding every immature account as non-default understates risk. Define maturity

\[
M_i=\mathbb{1}\{t_i+g+h\le T\}.
\]

Binary PD development normally retains $M_i=1$ observations. Survival methods can use censored histories with a different likelihood. Existing default, fraud, deceased customers, sold portfolios, restructures and missing outcomes require explicit policy, not retrospective removal after seeing model performance.

## Repeated observations and split leakage

Behavioural samples often contain many reference dates for one customer. A random row split can place customer $i$ in both training and validation. The model then sees stable identity or account patterns in training and appears to generalise in validation. Grouped or out-of-time splitting is therefore a property of the estimand.

For cut date $c$:

\[
Train=\{i:t_i\le c\},\qquad Test=\{i:t_i>c\}.
\]

An embargo can remove observations close to $c$ when their performance windows overlap. All bins, scalers, encoders and feature-selection rules are fit on training data only.

## Target construction from events

```python
import pandas as pd

def make_default_target(observations, defaults, horizon_months=12, buffer_days=0):
    left = observations.copy()
    right = defaults.copy()
    left["reference_date"] = pd.to_datetime(left["reference_date"])
    right["default_date"] = pd.to_datetime(right["default_date"])
    merged = left.merge(right, on="customer_id", how="left")
    start = merged["reference_date"] + pd.to_timedelta(buffer_days, unit="D")
    end = merged["reference_date"] + pd.DateOffset(months=horizon_months)
    in_window = (merged["default_date"] > start) & (merged["default_date"] <= end)
    target = in_window.groupby(merged["observation_id"]).max().astype(int)
    return left.merge(target.rename("default_12m"), left_on="observation_id", right_index=True)
```

The implementation preserves the rule $t<\tau\le t+12m$. A target test should place events one day before the reference, exactly at the reference, one day after, exactly at the horizon and one day after the horizon. It should also test multiple default events and customers with none.

## Sample weights after case-control sampling

If defaults and non-defaults are sampled with inclusion probabilities $\pi_1$ and $\pi_0$, a population mean is estimated with inverse-probability weights

\[
\widehat{\mu}=\frac{\sum_i Y_i/\pi_{Y_i}}{\sum_i 1/\pi_{Y_i}}.
\]

Unweighted sample prevalence is not portfolio default rate. Logistic slopes may survive certain outcome-based sampling designs, but probability calibration and intercept do not automatically do so. The sample design, weights and target population belong in the model manifest.

**Applied investigation.** Create monthly observations and twelve-month labels, remove immature outcomes, then compare random-row, grouped-customer and out-of-time splits. Explain which apparent performance increase is leakage.

# Chapter 23 — Data Profiling, Reconciliation, Cleaning, and Quarantine

## Cleaning begins with diagnosis

Completeness asks whether required values are present. Validity checks domain and range. Uniqueness checks keys. Consistency compares related fields. Accuracy compares trusted sources or recomputations. Timeliness checks freshness. Integrity checks relationships. Lineage checks origin and temporal availability. Representativeness compares observed and intended populations.

For rule $k$, indicator $I_{ik}=1$ when row $i$ fails. The failure rate is

\[
q_k=\frac{\sum_{i=1}^{n_k}I_{ik}}{n_k}.
\]

A weighted quality score $Q=\sum_k w_k(1-q_k)$ can summarise a dashboard, but it must never hide a critical rule. A future snapshot and a harmless optional-field null are not interchangeable because their business actions differ.

## Profile before transformation

For numeric $X$, report count, missing rate, distinct count, minimum, maximum, quantiles and robust spread

\[
IQR(X)=Q_{0.75}(X)-Q_{0.25}(X).
\]

The common fence $[Q_{0.25}-1.5IQR,Q_{0.75}+1.5IQR]$ is a screening flag, not proof of error. A valid wealthy customer may be extreme; a currency-unit error may sit inside the fence. For categorical $C$, report cardinality, rare levels, nulls, unexpected domains and changes by source month. For dates, report parsing failures, future values, latency and gaps.

## Reconcile business identities

Balance constraints are contextual. A revolving account may legitimately exceed its limit within an authorised tolerance, while a negative balance may represent credit rather than error. The rule must state semantics. The teaching ledger uses

\[
0\le Balance_{i,t}\le 1.20\,Limit_{i,t},
\]

and separately counts $Balance>Limit$ as over-limit behaviour. DPD-status consistency is

\[
Status(DPD)=
\begin{cases}
current,&DPD=0,\\
delinquent,&0<DPD<90,\\
default,&DPD\ge90.
\end{cases}
\]

This is a teaching convention, not a universal regulatory default definition.

![Cleaning rules preserve raw evidence and produce a controlled disposition](book/figures/data-cleaning-quarantine-flow.png)

## Write the first cleaner in the chapter

Before importing the library, build a transparent rule evaluator. It returns failures; it does not overwrite them.

```python
import pandas as pd

def scratch_performance_rules(frame, reference_date):
    data = frame.copy(deep=True)
    data["snapshot_date"] = pd.to_datetime(data["snapshot_date"], errors="coerce")
    failures = pd.DataFrame(index=data.index)
    failures["bad_date"] = data["snapshot_date"].isna() | (
        data["snapshot_date"] > pd.Timestamp(reference_date)
    )
    failures["bad_dpd"] = data["dpd"].isna() | ~data["dpd"].between(0, 999)
    failures["bad_payment"] = data["payment_received"].isna() | (
        data["payment_received"] < 0
    )
    failures["bad_balance"] = data["balance"].isna() | (data["balance"] < 0) | (
        data["balance"] > 1.20 * data["credit_limit"]
    )
    failures["bad_status"] = ~data["status"].isin(["current", "delinquent", "default"])
    return failures
```

Then test an ordinary row, each boundary, a missing value, a negative DPD, a future date and a contradictory status. Expected results are written before execution:

```python
ordinary = pd.DataFrame({
    "snapshot_date": ["2025-06-30"], "dpd": [30],
    "payment_received": [80.0], "balance": [900.0],
    "credit_limit": [1000.0], "status": ["delinquent"],
})
assert not scratch_performance_rules(ordinary, "2025-12-31").any(axis=None)

broken = ordinary.copy()
broken.loc[0, "dpd"] = -1
assert scratch_performance_rules(broken, "2025-12-31").loc[0, "bad_dpd"]
```

## Duplicate versions and authoritative corrections

An exact duplicate and a later correction are different. For business key $K=(customer,contract,snapshot)$, choose the record with maximum ingestion time only when the source contract declares later ingestion authoritative:

\[
r_K^*=\arg\max_{r:key(r)=K} processing\_time(r).
\]

Earlier versions are not erased. They move to quarantine with action `retain_latest_ingestion_and_quarantine_prior_version`. If authority is ambiguous, halt. Choosing the value most favourable to model performance is never a cleaning rule.

## Freeze the tested cleaning contract before promotion

Students now have enough information to specify the later package contract: raw rows in; accepted rows, quarantine rows and one issue record per failed rule out. The Chapter 23 standalone script implements this contract without project imports and prints the accepted indexes plus row-level reasons. The full version is promoted only after Chapters 21–24 are complete, adding customer-specific reference dates, processing-time versions, status-DPD consistency and source-row evidence without changing the visible contract.

Expected issue categories include `dpd_out_of_domain`, `negative_or_missing_payment_received`, `balance_exceeds_120pct_limit`, `status_out_of_domain`, `post_reference_snapshot`, `status_dpd_inconsistent` and `superseded_business_key`. Counts are generated and tested; they are not manually edited into a presentation.

## Missingness and transformations

MCAR, MAR and MNAR are descriptions of a data-generating process, not labels inferred from one missingness table. If $R=1$ means observed, MCAR states $R\perp(X,Y)$; MAR allows $\Pr(R=1\mid X_{obs},X_{mis},Y)=\Pr(R=1\mid X_{obs},Y)$; MNAR allows dependence on the missing value after conditioning. Real missing income can arise from an optional field, self-employment, system failure, policy path or refusal. A median does not solve the cause.

The baseline policy is preserve raw, diagnose, then quarantine or use an explicit, approved missingness treatment. The same applies to outliers. Winsorisation changes values and can damage scorecard meaning. Store raw value, transformation, threshold, rationale and impact separately.

**Applied investigation.** Inject each documented defect, produce a rule-by-source quality table, quarantine without imputation, reconcile row counts, and draft an exception ticket with owner, expiry and compensating control.

# Chapter 24 — Behavioural and Bureau Feature Engineering

## From histories to a decision-time vector

Feature engineering compresses a path into a point-in-time vector. The compression must preserve meaning and timing. Let $D_{i,s}$ be customer $i$'s maximum DPD across contracts at month $s$ and $t_i$ the reference date. For lookback $w$:

\[
MaxDPD_i(w)=\max_{s\in\mathcal{O}_i(w)}D_{i,s}.
\]

Let $s_i^*=\max\{s:s\le t_i\}$. The last observed delinquency is

\[
LastDPD_i=D_{i,s_i^*}.
\]

These answer different questions. `max_dpd_6m` measures worst recent severity; `last_dpd` measures current or most recent state. A borrower who cured from 60 to 0 has `max_dpd_6m=60` and `last_dpd=0`. Replacing one with the other discards either severity or cure information.

![A DPD trajectory produces severity, recency, frequency and trend features](book/figures/behavioral-dpd-window.png)

## Frequency, recency and persistence

At threshold $d$:

\[
CountDPD_{i,d}(w)=\sum_{s\in\mathcal{O}_i(w)}\mathbb{1}\{D_{i,s}\ge d\}.
\]

The book computes counts at 30, 60 and 90 days. It counts customer-months after aggregating contracts, so two delinquent contracts in one month count as one delinquent month. A separate contract-event feature would answer a different question.

If $\mathcal{D}_{i,30}=\{s\le t_i:D_{i,s}\ge30\}$, months since the latest 30-DPD event is

\[
Recency_{i,30}=12(t_y-s_y)+(t_m-s_m),
\]

for $s=\max\mathcal{D}_{i,30}$. It remains missing when no event exists; zero means an event in the reference month. Collapsing both to zero reverses the meaning.

Consecutive delinquent months count the trailing run of $D_{i,s}>0$. A transition feature may also count deteriorations $\mathbb{1}\{D_{i,s}>D_{i,s-1}\}$ and cures $\mathbb{1}\{D_{i,s-1}\ge30,D_{i,s}=0\}$.

## Utilisation, payment and over-limit behaviour

At month $s$, customer utilisation aggregates balances before dividing:

\[
U_{i,s}=\frac{\sum_j Balance_{i,j,s}}{\sum_j Limit_{i,j,s}}.
\]

The mean of contract-level utilisation is generally wrong because a EUR 200 balance on a EUR 500 limit should not receive the same weight as EUR 2,000 on a EUR 20,000 limit. Window summaries include current, mean, maximum and slope.

For ordered monthly values $U_1,\ldots,U_n$, the ordinary least-squares trend per month is

\[
\widehat{\beta}_U=\frac{\sum_{k=1}^{n}(k-\bar{k})(U_k-\bar{U})}{\sum_{k=1}^{n}(k-\bar{k})^2}.
\]

A positive slope means rising utilisation under the ordering used. It is zero for fewer than two observed months in the teaching implementation, with history length reported separately.

Payment ratio aggregates payments and obligations before division:

\[
PR_{i,s}=\frac{\sum_j PaymentReceived_{i,j,s}}{\sum_j ScheduledPayment_{i,j,s}}.
\]

Zero scheduled payment produces missing ratio, not infinity. Over-limit months count $\sum_s\mathbb{1}\{Balance_{i,s}>Limit_{i,s}\}$ after the quality policy has separated implausible breaches from permitted over-limit behaviour.

## New contracts and bureau intensity

For contract open date $o_{ij}$,

\[
CountContractsLast6Months_i=\sum_j\mathbb{1}\{t_i-6m<o_{ij}\le t_i\}.
\]

This is the business name; the Python feature is `count_contracts_last_6m`. Active contracts satisfy $o_{ij}\le t_i$ and either no close date or $close_{ij}>t_i$. Bureau enquiry counts use the same point-in-time boundary for 1, 3, 6 or 12 months. High enquiry or new-contract intensity can mean credit shopping, portfolio growth or data matching artefacts; interpretation precedes monotonic assumptions.

![Open dates inside the lookback determine CountContractsLast6Months](book/figures/behavioral-contract-window.png)

## Implement three core features from scratch

Students first implement the formulas without importing the finished feature module:

```python
import pandas as pd

def scratch_core_features(performance, contracts, reference_dates, months=6):
    rows = []
    for ref in reference_dates.itertuples(index=False):
        t = pd.Timestamp(ref.reference_date)
        history = performance.loc[
            (performance["customer_id"] == ref.customer_id)
            & (performance["snapshot_date"] <= t)
        ].copy()
        monthly = (
            history.groupby("snapshot_date", as_index=False)["dpd"].max()
            .sort_values("snapshot_date")
        )
        window = monthly.loc[monthly["snapshot_date"] > t - pd.DateOffset(months=months)]
        opened = contracts.loc[
            (contracts["customer_id"] == ref.customer_id)
            & (contracts["open_date"] > t - pd.DateOffset(months=months))
            & (contracts["open_date"] <= t)
        ]
        rows.append({
            "customer_id": ref.customer_id,
            "reference_date": t,
            f"max_dpd_{months}m": window["dpd"].max() if len(window) else None,
            "last_dpd": monthly.iloc[-1]["dpd"] if len(monthly) else None,
            f"count_dpd30_{months}m": int((window["dpd"] >= 30).sum()),
            f"count_contracts_last_{months}m": int(len(opened)),
        })
    return pd.DataFrame(rows)
```

The hand test uses one cured borrower:

```python
performance = pd.DataFrame({
    "customer_id": ["A", "A", "A"],
    "snapshot_date": pd.to_datetime(["2025-10-31", "2025-11-30", "2025-12-31"]),
    "dpd": [60, 30, 0],
})
contracts = pd.DataFrame({
    "customer_id": ["A", "A"],
    "open_date": pd.to_datetime(["2024-01-01", "2025-09-15"]),
})
refs = pd.DataFrame({"customer_id": ["A"], "reference_date": ["2025-12-31"]})
observed = scratch_core_features(performance, contracts, refs).iloc[0]
assert observed["max_dpd_6m"] == 60
assert observed["last_dpd"] == 0
assert observed["count_dpd30_6m"] == 2
assert observed["count_contracts_last_6m"] == 1
print(observed[["max_dpd_6m", "last_dpd", "count_dpd30_6m", "count_contracts_last_6m"]])
```

Expected output:

```text
max_dpd_6m                     60
last_dpd                        0
count_dpd30_6m                  2
count_contracts_last_6m         1
```

This example prevents four common errors: taking last instead of maximum, counting contracts instead of months, including a contract outside the boundary, and treating cured DPD as if it never occurred.

## Test boundaries and future leakage

Add a future row with $DPD=999$. Every feature at the earlier reference date must remain identical. Add a contract exactly at $t-6m$ and verify exclusion under the open-left convention. Add two contracts in one month and verify `count_dpd30_6m` still counts a month, not contracts. Add no-history and zero-limit cases; missing or quarantine policy must be explicit.

## Freeze the feature contract before package reuse

The Chapter 24 standalone script calculates `last_dpd`, `max_dpd_6m`, `count_dpd30_6m`, mean utilisation and `CountContractsLast6Months` from visible histories. The extension then adds 3-, 6- and 12-month severity/frequency, recency, persistence, current/mean/max/trend utilisation, payment ratios, over-limit months, active balances and bureau enquiries. Only after the hand cases and future-leakage tests pass is this contract promoted to the richer implementation used later in the book.

The cleaning result is passed into features so a model cannot quietly consume quarantined rows. Tests reconcile scratch and library results for hand cases, assert the closed-form utilisation slope, and prove that future rows do not change earlier features.

## Evaluate rationality, not only execution

For generated data, compare observed default rate by feature bins. Because the generator intentionally links recent DPD, utilisation and new contracts to future default, bad rate should generally increase with worse bands in large samples. A small sample can deviate by chance; no hard monotonic result is fabricated. For real data, unexpected direction triggers source, cohort, policy and confounding investigation before transformation.

Characteristic analysis should report count, exposure, missing share, event count, event rate, confidence interval, distribution by development/validation/time/segment and stability. A rationality check asks whether direction, magnitude, nonlinearity and interactions make product sense. It does not force monotonicity merely to fit an expected story.

## Further features for student extensions

- `min_dpd`, average positive DPD and worst delinquency bucket.
- Deterioration, cure and roll-rate counts between monthly states.
- Months since any DPD, 30 DPD, limit breach, payment shortfall or new facility.
- Balance, limit, scheduled-payment and payment-received slopes and volatility.
- Ratio of new contracts to active contracts; share of revolving exposure.
- Oldest and newest contract age; months since newest contract.
- Enquiries by type and enquiry-to-new-contract conversion.
- RFM features for transaction data: recency, frequency and monetary amount, with lawful purpose and stability review.
- Cohort-relative features such as deviation from segment utilisation, fitted on training data only.

**Lab.** Reproduce the cured-borrower hand calculation, extend the scratch implementation with utilisation slope and bureau enquiries, pass the point-in-time tests, promote the functions to the package, and compare characteristic tables for generated retail, UCI Taiwan card and a provider-controlled mortgage file where the reader has lawful access.

> Part IV now produces an auditable analytic base table from lawful sources. It does not treat cleaning as silent value replacement or feature engineering as a one-line aggregation. Every feature has a formula, boundary, scratch implementation, test, promoted library function and business interpretation.

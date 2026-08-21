"""Standalone, executable examples for Chapters 1-24.

These examples intentionally avoid importing :mod:`creditriskbook`.  Students see the
complete calculation before any implementation is promoted into the reusable package.
"""

from __future__ import annotations

EXAMPLES: dict[int, str] = {
    1: r"""schedule = [
    # month, contractual, received, recovery, workout cost
    (1, 350.0, 350.0, 0.0, 0.0),
    (2, 350.0, 200.0, 0.0, 5.0),
    (3, 350.0, 0.0, 120.0, 15.0),
]
eir = 0.12
total_pv_loss = 0.0

print("month  shortfall  discount  pv_loss")
for month, contractual, received, recovery, cost in schedule:
    shortfall = contractual - received - recovery + cost
    discount = (1.0 + eir) ** (-month / 12.0)
    pv_loss = shortfall * discount
    total_pv_loss += pv_loss
    print(f"{month:>5}  {shortfall:>9.2f}  {discount:>8.4f}  {pv_loss:>7.2f}")

print("Total PV loss:", round(total_pv_loss, 2))""",
    2: r"""from itertools import product

pd = [0.10, 0.20]
loss_if_default = [500.0, 800.0]  # LGD times EAD
distribution = []

for defaults in product((0, 1), repeat=2):
    probability = 1.0
    loss = 0.0
    for default, probability_of_default, amount in zip(
        defaults, pd, loss_if_default, strict=True
    ):
        probability *= probability_of_default if default else 1.0 - probability_of_default
        loss += default * amount
    distribution.append((loss, probability, defaults))

expected_loss = sum(loss * probability for loss, probability, _ in distribution)
cumulative_probability = 0.0
loss_quantile_95 = None
for loss, probability, defaults in sorted(distribution):
    cumulative_probability += probability
    print(defaults, "loss=", loss, "probability=", round(probability, 3))
    if loss_quantile_95 is None and cumulative_probability >= 0.95:
        loss_quantile_95 = loss

print("Expected loss:", expected_loss)
print("95% loss quantile:", loss_quantile_95)
print("Unexpected loss at 95%:", loss_quantile_95 - expected_loss)""",
    3: r"""scenarios = [
    # name, weight, PD, LGD, EAD
    ("base", 0.60, 0.03, 0.35, 10_000.0),
    ("downturn", 0.25, 0.09, 0.50, 11_000.0),
    ("severe", 0.15, 0.20, 0.65, 12_000.0),
]

coherent_el = 0.0
average_pd = average_lgd = average_ead = 0.0
for name, weight, pd, lgd, ead in scenarios:
    scenario_el = pd * lgd * ead
    coherent_el += weight * scenario_el
    average_pd += weight * pd
    average_lgd += weight * lgd
    average_ead += weight * ead
    print(name, "EL=", round(scenario_el, 2), "weighted EL=", round(weight * scenario_el, 2))

product_of_averages = average_pd * average_lgd * average_ead
print("Weighted scenario EL:", round(coherent_el, 2))
print("Product of separate averages:", round(product_of_averages, 2))
print("Dependence effect:", round(coherent_el - product_of_averages, 2))""",
    4: r"""from collections import Counter, defaultdict

histories = {
    "A": ["current", "current", "30_dpd", "60_dpd"],
    "B": ["current", "30_dpd", "current", "current"],
    "C": ["current", "current", "prepaid", "prepaid"],
}
transition_counts = defaultdict(Counter)

for states in histories.values():
    for current_state, next_state in zip(states, states[1:], strict=False):
        transition_counts[current_state][next_state] += 1

for current_state, counts in transition_counts.items():
    row_total = sum(counts.values())
    probabilities = {
        next_state: round(count / row_total, 3)
        for next_state, count in sorted(counts.items())
    }
    print(current_state, probabilities, "row sum=", round(sum(probabilities.values()), 3))""",
    5: r"""from math import exp


def sigmoid(value):
    return 1.0 / (1.0 + exp(-value))


def cumulative_pd(hazards):
    survival = 1.0
    result = []
    for hazard in hazards:
        if not 0.0 <= hazard <= 1.0:
            raise ValueError("Each hazard must lie between zero and one")
        survival *= 1.0 - hazard
        result.append(1.0 - survival)
    return result


classification_pd = [round(sigmoid(value), 4) for value in (-2.0, -0.5, 1.0)]
regression_lgd = [0.18, 0.42, 0.77]
lifetime_pd = [round(value, 4) for value in cumulative_pd([0.02, 0.03, 0.05, 0.08])]
print("Classification PD:", classification_pd)
print("Regression LGD:", regression_lgd)
print("Cumulative lifetime PD:", lifetime_pd)""",
    6: r'''import hashlib
import json


def reproducible_run_id(data_hash: str, code_hash: str, policy: dict) -> str:
    """Hash canonical evidence; never hash an unordered string representation."""
    payload = {"data_hash": data_hash, "code_hash": code_hash, "policy": policy}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


policy = {"horizon_months": 12, "default_dpd": 90, "version": "1.0"}
run_id = reproducible_run_id("data-9f2a", "code-31bc", policy)
print("Run ID:", run_id)
print("Length:", len(run_id), "hexadecimal:", all(c in "0123456789abcdef" for c in run_id))''',
    7: r"""import pandas as pd


def product_exposure(product: str, drawn: float, limit: float, ccf: float) -> float:
    if drawn < 0 or limit < drawn or not 0 <= ccf <= 1:
        raise ValueError("Invalid drawn amount, limit, or CCF")
    if product in {"credit_card", "overdraft"}:
        return drawn + ccf * (limit - drawn)
    return drawn


facilities = pd.DataFrame({
    "product": ["term_loan", "credit_card", "overdraft"],
    "drawn": [18_000.0, 2_000.0, 7_000.0], "limit": [18_000.0, 8_000.0, 10_000.0],
    "ccf": [0.0, 0.65, 0.40],
})
facilities["ead"] = [product_exposure(*row) for row in facilities.itertuples(index=False, name=None)]
print(facilities.to_string(index=False))""",
    8: r"""import pandas as pd


def corporate_ratios(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["debt_to_ebitda"] = out["debt"] / out["ebitda"].replace(0, pd.NA)
    out["interest_cover"] = out["ebit"] / out["interest_expense"].replace(0, pd.NA)
    out["dscr"] = out["cash_available_for_debt_service"] / out["debt_service"].replace(0, pd.NA)
    out["equity_ratio"] = out["equity"] / out["assets"].replace(0, pd.NA)
    return out


companies = pd.DataFrame({
    "company": ["StableCo", "GrowthCo", "StressedCo"], "debt": [200, 450, 600],
    "ebitda": [120, 90, 40], "ebit": [95, 55, 10], "interest_expense": [20, 30, 35],
    "cash_available_for_debt_service": [100, 70, 20], "debt_service": [55, 65, 70],
    "equity": [500, 250, 80], "assets": [900, 850, 780],
})
print(corporate_ratios(companies).round(2).to_string(index=False))""",
    9: r"""import pandas as pd


def bnpl_schedule(purchase: float, instalments: int, monthly_income: float) -> pd.DataFrame:
    if purchase <= 0 or instalments < 2 or monthly_income <= 0:
        raise ValueError("Positive purchase, income, and at least two instalments are required")
    payment = purchase / instalments
    burden = payment / monthly_income
    return pd.DataFrame({"instalment": range(1, instalments + 1), "payment": payment,
                         "payment_to_income": burden})


schedule = bnpl_schedule(480.0, 4, 2_000.0)
print(schedule.round(3).to_string(index=False))
print("Total payments:", schedule["payment"].sum(), "monthly burden:", schedule["payment_to_income"].iloc[0])""",
    10: r"""import pandas as pd


def assign_segment(row) -> str:
    if row["business_obligor"] and row["observed_defaults"] < 5:
        return "low_default_portfolio"
    if row["bureau_months"] < 12 or row["open_trades"] < 2:
        return "thin_file"
    if row["estimated_pd"] >= 0.12:
        return "subprime"
    return "prime"


borrowers = pd.DataFrame({
    "borrower": ["A", "B", "C", "D"], "estimated_pd": [0.02, 0.18, 0.07, 0.03],
    "bureau_months": [96, 72, 5, 60], "open_trades": [5, 4, 1, 3],
    "business_obligor": [False, False, False, True], "observed_defaults": [100, 100, 100, 2],
})
borrowers["segment"] = borrowers.apply(assign_segment, axis=1)
print(borrowers[["borrower", "segment"]].to_string(index=False))""",
    11: r"""import pandas as pd

ALLOWED = {
    "application": {"approved", "declined"}, "approved": {"current"},
    "current": {"delinquent", "prepaid"}, "delinquent": {"current", "default"},
    "default": {"recovery", "closed"}, "recovery": {"closed"}, "declined": set(),
    "prepaid": set(), "closed": set(),
}


def validate_lifecycle(events: pd.DataFrame) -> pd.DataFrame:
    ordered = events.sort_values(["account_id", "event_time"]).copy()
    ordered["previous_state"] = ordered.groupby("account_id")["state"].shift()
    ordered["valid_transition"] = ordered.apply(
        lambda r: True if pd.isna(r.previous_state) else r.state in ALLOWED.get(r.previous_state, set()), axis=1
    )
    return ordered


events = pd.DataFrame({
    "account_id": ["A"] * 5, "event_time": pd.date_range("2025-01-01", periods=5, freq="30D"),
    "state": ["application", "approved", "current", "delinquent", "default"],
})
audit = validate_lifecycle(events)
print(audit[["event_time", "previous_state", "state", "valid_transition"]].to_string(index=False))""",
    12: r"""from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyDecision:
    result: str
    reasons: tuple[str, ...]
    human_review: bool


def apply_credit_policy(pd, debt_service, verified_income, requested_amount, max_amount=25_000):
    reasons = []
    if verified_income <= 0:
        reasons.append("income_not_verified")
    elif debt_service / verified_income > 0.40:
        reasons.append("affordability_limit")
    if pd > 0.15:
        reasons.append("pd_above_appetite")
    if requested_amount > max_amount:
        reasons.append("amount_outside_delegation")
    if reasons:
        return PolicyDecision("refer_or_decline", tuple(reasons), requested_amount > max_amount)
    return PolicyDecision("eligible_for_human_approval", (), True)


for case in [(0.04, 600, 2_500, 10_000), (0.20, 1_200, 2_000, 35_000)]:
    print(apply_credit_policy(*case))""",
    13: r"""import pandas as pd


def standardised_rwa(exposure: float, risk_weight: float) -> dict:
    if exposure < 0 or risk_weight < 0:
        raise ValueError("Exposure and risk weight cannot be negative")
    rwa = exposure * risk_weight
    return {"exposure": exposure, "risk_weight": risk_weight, "rwa": rwa,
            "minimum_capital_8pct": 0.08 * rwa}


rows = [standardised_rwa(1_000_000, rw) for rw in (0.20, 0.50, 1.00, 1.50)]
print(pd.DataFrame(rows).to_string(index=False))""",
    14: r"""import pandas as pd


def regulatory_default(days_past_due, unlikely_to_pay, distressed_restructure=False):
    reasons = []
    if days_past_due >= 90:
        reasons.append("90_dpd_backstop")
    if unlikely_to_pay:
        reasons.append("unlikely_to_pay")
    if distressed_restructure:
        reasons.append("distressed_restructure")
    return bool(reasons), tuple(reasons)


cases = pd.DataFrame({"dpd": [0, 65, 92], "utp": [False, True, False], "restructure": [False, False, True]})
cases[["default", "reasons"]] = cases.apply(
    lambda r: pd.Series(regulatory_default(r.dpd, r.utp, r.restructure)), axis=1
)
print(cases.to_string(index=False))""",
    15: r"""import pandas as pd


def grade_backtest(frame: pd.DataFrame) -> pd.DataFrame:
    grouped = frame.groupby("grade", observed=True)
    result = grouped.agg(observations=("default", "size"), predicted_pd=("pd", "mean"),
                         observed_rate=("default", "mean"), defaults=("default", "sum"))
    result["observed_to_expected"] = result["observed_rate"] / result["predicted_pd"]
    return result.reset_index()


portfolio = pd.DataFrame({
    "grade": ["A"] * 5 + ["B"] * 5, "pd": [0.02] * 5 + [0.10] * 5,
    "default": [0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
})
print(grade_backtest(portfolio).round(3).to_string(index=False))""",
    16: r"""import pandas as pd


def assign_ifrs9_stage(origination_pd, current_pd, dpd, watchlist, default):
    if default or dpd >= 90:
        return 3, "credit_impaired_or_default"
    pd_ratio = current_pd / origination_pd if origination_pd > 0 else float("inf")
    if dpd >= 30 or watchlist or pd_ratio >= 2.0:
        return 2, "significant_increase_in_credit_risk"
    return 1, "performing_without_sicr"


accounts = pd.DataFrame({
    "account": ["A", "B", "C"], "orig_pd": [0.02, 0.02, 0.03],
    "current_pd": [0.025, 0.055, 0.30], "dpd": [0, 35, 95],
    "watchlist": [False, False, True], "default": [False, False, True],
})
accounts[["stage", "reason"]] = accounts.apply(
    lambda r: pd.Series(assign_ifrs9_stage(r.orig_pd, r.current_pd, r.dpd, r.watchlist, r.default)), axis=1
)
print(accounts[["account", "stage", "reason"]].to_string(index=False))""",
    17: r"""import pandas as pd


def cecl_loss_rate(exposure, historical_loss_rate, qualitative_adjustment=0.0):
    adjusted = historical_loss_rate + qualitative_adjustment
    if exposure < 0 or not 0 <= adjusted <= 1:
        raise ValueError("Invalid exposure or adjusted loss rate")
    return exposure * adjusted


pools = pd.DataFrame({
    "pool": ["prime", "near_prime", "subprime"], "exposure": [1_000_000, 600_000, 250_000],
    "historical_loss_rate": [0.008, 0.035, 0.110], "qualitative_adjustment": [0.002, 0.005, 0.010],
})
pools["lifetime_cecl"] = pools.apply(
    lambda r: cecl_loss_rate(r.exposure, r.historical_loss_rate, r.qualitative_adjustment), axis=1
)
print(pools.to_string(index=False))
print("Total CECL:", pools["lifetime_cecl"].sum())""",
    18: r"""import pandas as pd


def group_decision_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for group, part in frame.groupby("group", observed=True):
        rows.append({
            "group": group, "n": len(part), "approval_rate": part["approved"].mean(),
            "true_positive_rate": part.loc[part["creditworthy"] == 1, "approved"].mean(),
            "false_positive_rate": part.loc[part["creditworthy"] == 0, "approved"].mean(),
        })
    return pd.DataFrame(rows)


decisions = pd.DataFrame({
    "group": ["reference"] * 6 + ["comparison"] * 6,
    "creditworthy": [1, 1, 1, 0, 0, 0] * 2,
    "approved": [1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
})
metrics = group_decision_metrics(decisions)
print(metrics.round(3).to_string(index=False))
print("Approval-rate gap:", round(metrics.loc[0, "approval_rate"] - metrics.loc[1, "approval_rate"], 3))""",
    19: r'''import pandas as pd


def source_fit_table() -> pd.DataFrame:
    """Map each empirical question to data that can actually answer it."""
    return pd.DataFrame([
        ("application PD", "UCI Taiwan card", "default outcome, no dates", "benchmark only"),
        ("fair-lending decisions", "HMDA", "application outcomes", "not a PD dataset"),
        ("SME loan performance", "SBA 7(a)/504 FOIA", "loan outcomes", "definitions and vintages required"),
        ("complaint NLP", "CFPB complaints", "narratives and responses", "not underwriting evidence"),
        ("lifetime mortgage", "Fannie/Freddie", "monthly performance", "provider terms; not bundled"),
    ], columns=["question", "candidate_source", "useful_content", "boundary"])


table = source_fit_table()
print(table.to_string(index=False))''',
    20: r"""from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetLicenceRecord:
    key: str
    publisher: str
    official_url: str
    licence: str
    redistribution: str
    attribution: str


def licence_gate(record: DatasetLicenceRecord) -> tuple[bool, tuple[str, ...]]:
    issues = []
    for field in ("publisher", "official_url", "licence", "redistribution", "attribution"):
        if not getattr(record, field).strip():
            issues.append(f"missing_{field}")
    if "unknown" in record.licence.lower():
        issues.append("licence_not_resolved")
    return not issues, tuple(issues)


approved = DatasetLicenceRecord("uci_south_german", "UCI", "https://archive.ics.uci.edu/",
                                "CC BY 4.0", "download by code", "UCI dataset and DOI")
blocked = DatasetLicenceRecord("mystery_csv", "", "", "unknown", "", "")
print("Approved record:", licence_gate(approved))
print("Blocked record:", licence_gate(blocked))""",
    21: r"""import pandas as pd


def point_in_time_join(decisions: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for decision in decisions.itertuples(index=False):
        known = events.loc[
            (events.customer_id == decision.customer_id)
            & (events.effective_time <= decision.decision_time)
            & (events.processing_time <= decision.decision_time)
        ].sort_values(["effective_time", "processing_time"])
        chosen = known.tail(1)
        rows.append({
            "customer_id": decision.customer_id, "decision_time": decision.decision_time,
            "selected_value": None if chosen.empty else float(chosen.iloc[0]["value"]),
            "selected_effective_time": None if chosen.empty else chosen.iloc[0]["effective_time"],
        })
    return pd.DataFrame(rows)


decisions = pd.DataFrame({"customer_id": ["A", "B"], "decision_time": pd.to_datetime(["2025-03-15", "2025-03-15"])})
events = pd.DataFrame({
    "customer_id": ["A", "A", "B"], "effective_time": pd.to_datetime(["2025-02-01", "2025-04-01", "2025-02-20"]),
    "processing_time": pd.to_datetime(["2025-02-02", "2025-04-02", "2025-03-20"]), "value": [10, 999, 20],
})
result = point_in_time_join(decisions, events)
print(result.to_string(index=False))""",
    22: r"""import pandas as pd


def build_default_target(reference_dates, default_dates, horizon_months=12):
    reference = pd.to_datetime(reference_dates)
    default = pd.to_datetime(default_dates)
    horizon_end = reference + pd.offsets.DateOffset(months=horizon_months)
    observed = default.notna() & (default > reference) & (default <= horizon_end)
    return pd.DataFrame({"reference_date": reference, "horizon_end": horizon_end,
                         "default_date": default, "default_in_horizon": observed.astype(int)})


target = build_default_target(
    ["2024-01-31", "2024-01-31", "2024-01-31"],
    ["2024-08-15", "2025-05-01", None],
)
print(target.to_string(index=False))""",
    23: r'''import pandas as pd


def clean_performance(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return accepted rows and a row-level quarantine; do not impute or winsorise."""
    frame = raw.copy(deep=True)
    issue_rows = []
    checks = {
        "negative_dpd": frame["dpd"] < 0,
        "negative_balance": frame["balance"] < 0,
        "payment_exceeds_balance_plus_tolerance": frame["payment"] > frame["balance"] * 1.25,
        "future_snapshot": frame["snapshot_date"] > frame["as_of_date"],
    }
    bad = pd.Series(False, index=frame.index)
    for rule, mask in checks.items():
        bad |= mask
        issue_rows.extend({"row_id": int(i), "rule": rule} for i in frame.index[mask])
    return frame.loc[~bad].copy(), pd.DataFrame(issue_rows)


raw = pd.DataFrame({
    "dpd": [0, -4, 35, 0], "balance": [1000, 800, -10, 500], "payment": [100, 90, 20, 900],
    "snapshot_date": pd.to_datetime(["2025-01-31", "2025-01-31", "2025-03-31", "2025-01-31"]),
    "as_of_date": pd.to_datetime(["2025-02-01"] * 4),
})
accepted, quarantine = clean_performance(raw)
print("Accepted rows:", accepted.index.tolist())
print(quarantine.to_string(index=False))''',
    24: r"""import pandas as pd


def behavioral_features(performance, contracts, reference_date):
    ref = pd.Timestamp(reference_date)
    known_perf = performance.loc[performance["snapshot_date"] <= ref].sort_values("snapshot_date")
    window_6m = known_perf.loc[known_perf["snapshot_date"] > ref - pd.DateOffset(months=6)]
    known_contracts = contracts.loc[contracts["open_date"] <= ref]
    new_6m = known_contracts.loc[known_contracts["open_date"] > ref - pd.DateOffset(months=6)]
    return {
        "last_dpd": int(known_perf.iloc[-1]["dpd"]) if len(known_perf) else None,
        "max_dpd_6m": int(window_6m["dpd"].max()) if len(window_6m) else None,
        "count_dpd30_6m": int((window_6m["dpd"] >= 30).sum()),
        "mean_utilisation_6m": float(window_6m["balance"].div(window_6m["limit"]).mean()),
        "CountContractsLast6Months": int(len(new_6m)),
    }


performance = pd.DataFrame({
    "snapshot_date": pd.to_datetime(["2025-01-31", "2025-02-28", "2025-03-31", "2025-04-30"]),
    "dpd": [0, 12, 45, 8], "balance": [500, 650, 800, 700], "limit": [1000] * 4,
})
contracts = pd.DataFrame({"contract_id": ["C1", "C2", "C3"],
                          "open_date": pd.to_datetime(["2023-01-01", "2025-01-20", "2025-05-01"])})
print(behavioral_features(performance, contracts, "2025-04-30"))""",
}


if set(EXAMPLES) != set(range(1, 25)):
    raise RuntimeError("Standalone teaching examples must cover Chapters 1-24")

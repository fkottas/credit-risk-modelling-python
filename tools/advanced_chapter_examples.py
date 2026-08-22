"""Method-specific executable examples for Chapters 25–66.

The examples are intentionally small.  They expose the calculation being taught and produce an
output that can be checked by hand.  Larger datasets and reusable project classes are introduced
after the calculation is understood.
"""

from __future__ import annotations

EXAMPLES: dict[int, str] = {
    25: """import pandas as pd


data = pd.DataFrame({
    "utilisation": [0.10, 0.18, 0.25, 0.42, 0.55, 0.71, 0.83, 0.95],
    "default":     [0,    0,    0,    0,    1,    0,    1,    1],
})
data["bin"] = pd.cut(data["utilisation"], [0, 0.3, 0.6, 1.0], include_lowest=True)
table = data.groupby("bin", observed=False)["default"].agg(["count", "sum", "mean"])
table.columns = ["accounts", "defaults", "default_rate"]
print(table.to_string(float_format=lambda x: f"{x:.3f}"))""",
    26: """from math import inf


EDGES = [-inf, 0.30, 0.60, inf]
LABELS = ["low", "medium", "high"]


def manual_bin(value):
    if value is None:
        return "missing"
    for left, right, label in zip(EDGES[:-1], EDGES[1:], LABELS):
        if left < value <= right:
            return label
    raise ValueError("value was not assigned")


values = [None, 0.10, 0.30, 0.31, 0.60, 0.61]
print(list(zip(values, map(manual_bin, values))))""",
    27: """import numpy as np
from scipy.stats import chi2_contingency


bins = [
    {"left": 0, "right": 20, "good": 90, "bad": 10},
    {"left": 20, "right": 40, "good": 84, "bad": 16},
    {"left": 40, "right": 60, "good": 60, "bad": 40},
    {"left": 60, "right": 80, "good": 55, "bad": 45},
]


def adjacent_p_value(first, second):
    table = np.array([[first["good"], first["bad"]], [second["good"], second["bad"]]])
    return float(chi2_contingency(table, correction=False).pvalue)


p_values = [adjacent_p_value(bins[i], bins[i + 1]) for i in range(len(bins) - 1)]
merge_at = int(np.argmax(p_values))
merged = {"left": bins[merge_at]["left"], "right": bins[merge_at + 1]["right"],
          "good": bins[merge_at]["good"] + bins[merge_at + 1]["good"],
          "bad": bins[merge_at]["bad"] + bins[merge_at + 1]["bad"]}
print("adjacent p-values:", [round(value, 4) for value in p_values])
print("merge:", merge_at, "and", merge_at + 1, "->", merged)""",
    28: """import math


rows = [("low", 180, 20), ("medium", 120, 50), ("high", 40, 80)]
total_good = sum(good for _, good, _ in rows)
total_bad = sum(bad for _, _, bad in rows)
iv = 0.0
for label, good, bad in rows:
    good_share = good / total_good
    bad_share = bad / total_bad
    woe = math.log(good_share / bad_share)
    contribution = (good_share - bad_share) * woe
    iv += contribution
    print(label, "WOE=", round(woe, 4), "IV contribution=", round(contribution, 4))
print("Total IV:", round(iv, 4))""",
    29: """import numpy as np


def sigmoid(z):
    return np.where(z >= 0, 1 / (1 + np.exp(-z)), np.exp(z) / (1 + np.exp(z)))


def irls(X, y, l2=0.1, iterations=4):
    X = np.column_stack([np.ones(len(X)), np.asarray(X, dtype=float)])
    y = np.asarray(y, dtype=float)
    beta = np.zeros(X.shape[1])
    penalty = np.diag([0.0] + [l2] * (X.shape[1] - 1))
    for step in range(iterations):
        probability = sigmoid(X @ beta)
        weight = np.clip(probability * (1 - probability), 1e-9, 0.25)
        gradient = -(X.T @ (y - probability)) / len(y) + penalty @ beta
        hessian = (X.T * weight) @ X / len(y) + penalty
        delta = np.linalg.solve(hessian, gradient)
        beta -= delta
        print(step + 1, np.round(beta, 6), "max step", round(abs(delta).max(), 6))
    return beta


irls([[-1.0], [1.0]], [0, 1], iterations=1)""",
    30: """import math


pdo, base_score, base_odds = 20.0, 600.0, 50.0
factor = pdo / math.log(2.0)
offset = base_score - factor * math.log(base_odds)


def score_from_pd(pd):
    odds = (1.0 - pd) / pd
    return offset + factor * math.log(odds)


for odds in (25, 50, 100):
    pd = 1.0 / (1.0 + odds)
    print(f"odds={odds:>3}:1  PD={pd:.4%}  score={score_from_pd(pd):.1f}")""",
    31: """import pandas as pd


dates = pd.date_range("2022-01-31", periods=36, freq="ME")
sample = pd.DataFrame({"observation_date": dates})
sample["outcome_end"] = sample["observation_date"] + pd.DateOffset(months=12)
as_of = pd.Timestamp("2025-06-30")
sample["mature"] = sample["outcome_end"] <= as_of
sample["partition"] = pd.cut(
    sample["observation_date"],
    [pd.Timestamp("2021-12-31"), pd.Timestamp("2023-06-30"),
     pd.Timestamp("2024-06-30"), pd.Timestamp("2025-12-31")],
    labels=["development", "validation", "out_of_time"],
)
print(sample.groupby(["partition", "mature"], observed=False).size().unstack(fill_value=0))""",
    32: """import numpy as np


y = np.array([0, 0, 1, 0, 1, 1])
pd_hat = np.array([0.05, 0.10, 0.20, 0.30, 0.60, 0.80])
default_scores = pd_hat[y == 1]
nondefault_scores = pd_hat[y == 0]
auc = np.mean(default_scores[:, None] > nondefault_scores[None, :])
thresholds = np.unique(pd_hat)
ks = max(abs(np.mean(default_scores <= c) - np.mean(nondefault_scores <= c)) for c in thresholds)
cutoff = 0.25
approve = pd_hat < cutoff
false_approval_cost = 4500 * np.sum(approve & (y == 1))
false_decline_cost = 400 * np.sum((~approve) & (y == 0))
print({"AUC": round(float(auc), 4), "KS": round(float(ks), 4),
       "decision_cost": int(false_approval_cost + false_decline_cost)})""",
    33: """import numpy as np
import pandas as pd


pd_hat = np.array([0.01, 0.02, 0.03, 0.05, 0.08, 0.12, 0.20, 0.30])
y = np.array([0, 0, 0, 0, 1, 0, 1, 1])
grades = pd.cut(pd_hat, [0, 0.03, 0.10, 1], labels=["A", "B", "C"], include_lowest=True)
review = pd.DataFrame({"grade": grades, "pd": pd_hat, "default": y}).groupby(
    "grade", observed=False
).agg(accounts=("default", "size"), predicted_pd=("pd", "mean"), observed_rate=("default", "mean"))
print(review.to_string(float_format=lambda x: f"{x:.4f}"))""",
    34: """def gini(good, bad):
    total = good + bad
    if total == 0:
        return 0.0
    p_good, p_bad = good / total, bad / total
    return 1.0 - p_good ** 2 - p_bad ** 2


def weighted_child_gini(left, right):
    n_left, n_right = sum(left), sum(right)
    return (n_left * gini(*left) + n_right * gini(*right)) / (n_left + n_right)


parent = (6, 4)
for threshold, left, right in [(5, (5, 0), (1, 4)), (6, (6, 0), (0, 4))]:
    gain = gini(*parent) - weighted_child_gini(left, right)
    print("threshold", threshold, "weighted Gini", round(weighted_child_gini(left, right), 3),
          "gain", round(gain, 3))""",
    35: """import pandas as pd


data = pd.DataFrame({
    "group": ["A", "A", "A", "A", "B", "B", "B", "B"],
    "default": [0, 0, 1, 1, 0, 1, 1, 1],
    "approved": [1, 1, 1, 0, 1, 1, 0, 0],
})
rows = []
for group, frame in data.groupby("group"):
    rows.append({
        "group": group,
        "approval_rate": frame["approved"].mean(),
        "tpr_nondefault": frame.loc[frame.default == 0, "approved"].mean(),
        "default_rate_approved": frame.loc[frame.approved == 1, "default"].mean(),
    })
print(pd.DataFrame(rows).to_string(index=False, float_format=lambda x: f"{x:.3f}"))""",
    36: """import pandas as pd


applicants = pd.DataFrame({
    "income_band": [1, 1, 2, 2, 3, 3, 4, 4],
    "accepted":    [0, 1, 0, 1, 1, 1, 1, 1],
    "default":     [None, 1, None, 0, 0, 0, 0, 1],
})
observed = applicants.loc[applicants.accepted == 1]
print("accepted-sample default rate:", round(observed.default.mean(), 3))
print("outcomes unavailable for rejected applicants:", int(applicants.default.isna().sum()))
print("identified quantity: P(default | accepted, observed features)")""",
    37: """import pandas as pd


events = pd.DataFrame({"time": [1, 2, 2, 3, 4], "event": [1, 1, 0, 1, 0]})
survival = 1.0
rows = []
for time in sorted(events.loc[events.event == 1, "time"].unique()):
    at_risk = int((events.time >= time).sum())
    defaults = int(((events.time == time) & (events.event == 1)).sum())
    survival *= 1 - defaults / at_risk
    rows.append((time, at_risk, defaults, survival))
print(pd.DataFrame(rows, columns=["time", "at_risk", "defaults", "survival"]).to_string(index=False))""",
    38: """import numpy as np
import pandas as pd


hazard = np.array([0.02, 0.03, 0.04, 0.05])
survival_start = np.r_[1.0, np.cumprod(1.0 - hazard[:-1])]
marginal_pd = survival_start * hazard
cumulative_pd = np.cumsum(marginal_pd)
result = pd.DataFrame({"month": range(1, 5), "hazard": hazard,
                       "marginal_pd": marginal_pd, "cumulative_pd": cumulative_pd})
print(result.to_string(index=False, float_format=lambda x: f"{x:.5f}"))
print("reconciliation:", round(float(cumulative_pd[-1]), 5),
      round(float(1 - np.prod(1 - hazard)), 5))""",
    39: """from scipy.stats import beta


defaults, observations = 1, 80
prior_a, prior_b = 1.0, 19.0
posterior_a = prior_a + defaults
posterior_b = prior_b + observations - defaults
mean = posterior_a / (posterior_a + posterior_b)
lower, upper = beta.ppf([0.025, 0.975], posterior_a, posterior_b)
print({"observed_rate": defaults / observations, "posterior_mean": round(mean, 5),
       "credible_interval_95": (round(float(lower), 5), round(float(upper), 5))})""",
    40: """cashflows = [
    # months after default, recovery, direct workout cost
    (3, 1500.0, 100.0),
    (9, 800.0, 150.0),
    (15, 400.0, 200.0),
]
ead_at_default, eir = 5000.0, 0.10
pv_net_recovery = sum((recovery - cost) * (1 + eir) ** (-month / 12)
                      for month, recovery, cost in cashflows)
lgd = 1 - pv_net_recovery / ead_at_default
print("PV net recovery:", round(pv_net_recovery, 2))
print("Workout LGD:", round(lgd, 4))""",
    41: """import numpy as np


probability_positive_lgd = np.array([0.20, 0.55, 0.80])
severity_if_positive = np.array([0.25, 0.40, 0.60])
expected_lgd = probability_positive_lgd * severity_if_positive
downturn_multiplier = 1.20
downturn_lgd = np.minimum(expected_lgd * downturn_multiplier, 1.0)
for p, severity, base, downturn in zip(
    probability_positive_lgd, severity_if_positive, expected_lgd, downturn_lgd
):
    print(f"P(LGD>0)={p:.2f}  E[LGD|LGD>0]={severity:.2f}  base={base:.3f}  downturn={downturn:.3f}")""",
    42: """facilities = [
    # drawn at reference, limit at reference, exposure at default
    (4000.0, 10000.0, 7000.0),
    (8000.0, 10000.0, 9500.0),
    (10000.0, 10000.0, 10500.0),
]
for drawn, limit, ead in facilities:
    undrawn = limit - drawn
    ccf = None if undrawn == 0 else (ead - drawn) / undrawn
    print({"drawn": drawn, "undrawn": undrawn, "EAD": ead, "raw_CCF": ccf})""",
    43: """import pandas as pd


schedule = pd.DataFrame({
    "scenario": ["base", "base", "downside", "downside"],
    "weight": [0.7, 0.7, 0.3, 0.3],
    "month": [1, 2, 1, 2],
    "marginal_pd": [0.01, 0.015, 0.025, 0.035],
    "lgd": [0.40, 0.40, 0.50, 0.50],
    "ead": [10000, 9000, 10000, 9000],
    "discount_factor": [0.995, 0.990, 0.995, 0.990],
})
schedule["weighted_ecl"] = schedule.eval(
    "weight * marginal_pd * lgd * ead * discount_factor"
)
print(schedule.groupby("scenario")["weighted_ecl"].sum())
print("Total ECL:", round(schedule.weighted_ecl.sum(), 2))""",
    44: """def assign_stage(default, dpd, watchlist, pd_origination, pd_current):
    reasons = []
    if default or dpd >= 90:
        return 3, ("default_or_90_dpd",)
    if dpd >= 30:
        reasons.append("30_dpd_backstop")
    if watchlist:
        reasons.append("watchlist")
    if pd_current >= max(0.01, 2 * pd_origination):
        reasons.append("quantitative_sicr")
    return (2, tuple(reasons)) if reasons else (1, ())


cases = [(False, 0, False, 0.02, 0.025), (False, 35, False, 0.02, 0.03),
         (False, 5, True, 0.02, 0.05), (True, 95, True, 0.02, 0.40)]
print([assign_stage(*case) for case in cases])""",
    45: """import numpy as np


unemployment = np.array([4.0, 5.0, 7.0])
gdp_growth = np.array([2.0, 1.0, -1.5])
logit_pd = -4.2 + 0.22 * unemployment - 0.18 * gdp_growth
pd_path = 1 / (1 + np.exp(-logit_pd))
weights = np.array([0.20, 0.55, 0.25])
print("scenario PDs:", np.round(pd_path, 5))
print("probability-weighted PD:", round(float(weights @ pd_path), 5))""",
    46: """contractual = [1000.0, 1000.0, 1000.0]
expected = [1000.0, 700.0, 0.0]
eir = 0.12
shortfalls = []
for month, (contract, receipt) in enumerate(zip(contractual, expected), start=1):
    discount = (1 + eir) ** (-month / 12)
    shortfalls.append((contract - receipt) * discount)
    print(month, "discount", round(discount, 6), "PV shortfall", round(shortfalls[-1], 2))
print("Cash-flow ECL:", round(sum(shortfalls), 2))""",
    47: """import pandas as pd


matrix = pd.DataFrame({
    "age_band": ["current", "1-30", "31-60", "61-90"],
    "exposure": [800000, 120000, 50000, 30000],
    "historical_loss_rate": [0.005, 0.025, 0.12, 0.35],
    "forward_factor": [1.10, 1.15, 1.20, 1.25],
})
matrix["adjusted_loss_rate"] = matrix.historical_loss_rate * matrix.forward_factor
matrix["model_ecl"] = matrix.exposure * matrix.adjusted_loss_rate
overlay = 15000.0
print(matrix.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print("Model ECL:", round(matrix.model_ecl.sum(), 2), "Overlay:", overlay,
      "Reported allowance:", round(matrix.model_ecl.sum() + overlay, 2))""",
    48: """opening_allowance = 720000.0
movements = {"new_business": 85000.0, "repayments": -62000.0, "stage_change": 110000.0,
             "scenario_change": 45000.0, "write_off": -30000.0, "overlay_change": 12000.0}
closing = opening_allowance + sum(movements.values())
posted_ledger_balance = 880000.0
print("calculated closing allowance:", closing)
print("posted ledger balance:", posted_ledger_balance)
print("unreconciled difference:", posted_ledger_balance - closing)""",
    49: """import numpy as np
from scipy.stats import norm


pd, lgd, ead, maturity = 0.02, 0.45, 1_000_000.0, 2.5
correlation = 0.12 * (1 - np.exp(-50 * pd)) / (1 - np.exp(-50)) + 0.24 * (
    1 - (1 - np.exp(-50 * pd)) / (1 - np.exp(-50))
)
b = (0.11852 - 0.05478 * np.log(pd)) ** 2
maturity_adjustment = (1 + (maturity - 2.5) * b) / (1 - 1.5 * b)
conditional_pd = norm.cdf((norm.ppf(pd) + np.sqrt(correlation) * norm.ppf(0.999)) /
                          np.sqrt(1 - correlation))
capital_rate = lgd * (conditional_pd - pd) * maturity_adjustment
print({"correlation": round(float(correlation), 6), "conditional_PD": round(float(conditional_pd), 6),
       "capital_rate": round(float(capital_rate), 6), "RWA": round(12.5 * capital_rate * ead, 2)})""",
    50: """import numpy as np
from scipy.stats import norm


pd, lgd, ead = 0.02, 0.35, 250000.0


def retail_capital(correlation):
    stressed_pd = norm.cdf((norm.ppf(pd) + np.sqrt(correlation) * norm.ppf(0.999)) /
                           np.sqrt(1 - correlation))
    return lgd * (stressed_pd - pd)


for asset_class, correlation in [("residential mortgage", 0.15), ("QRRE", 0.04)]:
    capital = retail_capital(correlation)
    print(asset_class, "capital rate", round(float(capital), 6),
          "RWA", round(float(12.5 * capital * ead), 2))""",
    51: """import numpy as np


grade_weight = np.array([0.50, 0.30, 0.20])
raw_pd = np.array([0.010, 0.025, 0.070])
long_run_average = 0.035
scale = long_run_average / float(grade_weight @ raw_pd)
calibrated = np.minimum(raw_pd * scale, 1.0)
moc = np.array([0.001, 0.002, 0.004])
final_pd = np.minimum(calibrated + moc, 1.0)
print("calibrated weighted PD:", round(float(grade_weight @ calibrated), 6))
print("final grade PDs after MoC:", np.round(final_pd, 6))""",
    52: """import numpy as np


raw_lgd = np.array([0.18, 0.30, 0.55])
downturn_addon = np.array([0.05, 0.08, 0.10])
moc = np.array([0.02, 0.02, 0.03])
floor = 0.25
final_lgd = np.maximum(raw_lgd + downturn_addon + moc, floor)
raw_ccf = np.array([0.25, 0.55, 0.90])
ccf_floor = 0.50
final_ccf = np.maximum(raw_ccf, ccf_floor)
print("final LGD:", np.round(final_lgd, 3))
print("final CCF:", np.round(final_ccf, 3))""",
    53: """import numpy as np
from scipy.stats import norm


rng = np.random.default_rng(53)
n_obligors, simulations = 1000, 5000
pd, lgd, correlation = 0.02, 0.45, 0.12
systematic = rng.normal(size=simulations)
conditional_pd = norm.cdf((norm.ppf(pd) - np.sqrt(correlation) * systematic) /
                          np.sqrt(1 - correlation))
defaults = rng.binomial(n_obligors, conditional_pd)
loss_rate = defaults / n_obligors * lgd
print({"mean_loss": round(float(loss_rate.mean()), 5),
       "loss_99_9": round(float(np.quantile(loss_rate, 0.999)), 5),
       "unexpected_loss_99_9": round(float(np.quantile(loss_rate, 0.999) - loss_rate.mean()), 5)})""",
    54: """import numpy as np


months = np.array([6, 12, 18, 24])
expected_exposure = np.array([1.2, 1.0, 0.7, 0.3]) * 1_000_000
marginal_counterparty_pd = np.array([0.002, 0.003, 0.004, 0.005])
discount_factor = np.array([0.99, 0.98, 0.97, 0.96])
recovery_rate = 0.40
cva_terms = (1 - recovery_rate) * expected_exposure * marginal_counterparty_pd * discount_factor
print("CVA by period:", np.round(cva_terms, 2))
print("Approximate unilateral CVA:", round(float(cva_terms.sum()), 2))""",
    55: """criteria = {
    "conceptual_soundness": True,
    "data_reconstruction": True,
    "independent_benchmark": False,
    "implementation_reconciliation": True,
}
findings = [name for name, passed in criteria.items() if not passed]
opinion = "conditional" if findings else "satisfactory"
print({"validation_opinion": opinion, "open_findings": findings})""",
    56: """from scipy.stats import binomtest


grades = [("A", 500, 4, 0.010), ("B", 300, 12, 0.035), ("C", 120, 14, 0.090)]
for grade, n, defaults, assigned_pd in grades:
    observed = defaults / n
    test = binomtest(defaults, n, assigned_pd)
    print(grade, "observed", round(observed, 4), "assigned", assigned_pd,
          "two-sided p-value", round(test.pvalue, 4))""",
    57: """import numpy as np


actual = np.array([0.20, 0.35, 0.70, 0.50])
predicted = np.array([0.25, 0.30, 0.60, 0.55])
exposure = np.array([100, 400, 50, 200]) * 1000
error = actual - predicted
account_bias = error.mean()
exposure_weighted_bias = np.average(error, weights=exposure)
currency_error = np.sum(error * exposure)
print({"account_bias": round(float(account_bias), 4),
       "exposure_weighted_bias": round(float(exposure_weighted_bias), 4),
       "currency_error": round(float(currency_error), 2)})""",
    58: """reference = {"PD": 0.034821, "score": 612, "grade": "B", "reason": "high_utilisation"}
implementation = {"PD": 0.0348211, "score": 611, "grade": "B", "reason": "high_utilisation"}
tolerance = 1e-6
checks = {
    "PD": abs(reference["PD"] - implementation["PD"]) <= tolerance,
    "score": reference["score"] == implementation["score"],
    "grade": reference["grade"] == implementation["grade"],
    "reason": reference["reason"] == implementation["reason"],
}
print(checks)
print("UAT result:", "PASS" if all(checks.values()) else "FAIL")""",
    59: """import numpy as np


pd_hat = np.array([0.01, 0.03, 0.06, 0.10, 0.18])
ead = np.array([5000, 8000, 7000, 9000, 6000], dtype=float)
lgd, margin_rate, operating_cost = 0.45, 0.12, 120.0
for cutoff in (0.04, 0.08, 0.12):
    approve = pd_hat <= cutoff
    expected_profit = np.sum(approve * (ead * margin_rate - pd_hat * lgd * ead - operating_cost))
    print("cutoff", cutoff, "approved", int(approve.sum()), "expected profit", round(float(expected_profit), 2))""",
    60: """import numpy as np


rng = np.random.default_rng(60)
true_rewards = np.array([8.0, 11.0, 9.0])
counts = np.zeros(3, dtype=int)
estimates = np.zeros(3)
epsilon = 0.10
for _ in range(500):
    action = int(rng.integers(3)) if rng.random() < epsilon else int(np.argmax(estimates))
    reward = rng.normal(true_rewards[action], 4.0)
    counts[action] += 1
    estimates[action] += (reward - estimates[action]) / counts[action]
print("action counts:", counts.tolist())
print("estimated rewards:", np.round(estimates, 2).tolist())
print("simulation only: no customer limit is changed")""",
    61: """import hashlib
import json


record = {
    "data_sha256": "ab12",
    "code_commit": "c34d",
    "configuration": {"target": "default_12m", "seed": 61},
}
canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
run_id = hashlib.sha256(canonical.encode()).hexdigest()
print("canonical record:", canonical)
print("run identifier:", run_id[:20])""",
    62: """REQUEST_FIELDS = {"application_id", "income", "debt_to_income", "model_version"}


def validate_request(request):
    missing = REQUEST_FIELDS - request.keys()
    if missing:
        return {"status": 422, "error": "missing fields", "fields": sorted(missing)}
    if request["income"] < 0 or not 0 <= request["debt_to_income"] <= 2:
        return {"status": 422, "error": "value outside contract"}
    return {"status": 200, "application_id": request["application_id"],
            "model_version": request["model_version"]}


print(validate_request({"application_id": "A-1", "income": 42000,
                        "debt_to_income": 0.31, "model_version": "pd-2.1"}))
print(validate_request({"application_id": "A-2", "income": 42000, "model_version": "pd-2.1"}))""",
    63: """checks = {
    "unit_tests": True,
    "integration_tests": True,
    "security_scan": True,
    "validation_approval": True,
    "uat_reconciliation": False,
    "rollback_test": True,
}
failed = [name for name, passed in checks.items() if not passed]
print({"deployment_status": "BLOCKED" if failed else "ELIGIBLE",
       "failed_requirements": failed})""",
    64: """import numpy as np


expected = np.array([0.50, 0.30, 0.15, 0.05])
actual = np.array([0.40, 0.32, 0.20, 0.08])
epsilon = 1e-6
psi = np.sum((actual - expected) * np.log((actual + epsilon) / (expected + epsilon)))
monitor = {"input_PSI": round(float(psi), 4), "score_shift_available": True,
           "12m_calibration_available": False, "reason": "outcomes not yet mature"}
print(monitor)""",
    65: """incidents = [
    {"issue": "scoring service unavailable", "customer_effect": True, "financial_effect": False},
    {"issue": "wrong model version", "customer_effect": True, "financial_effect": True},
    {"issue": "late monitoring report", "customer_effect": False, "financial_effect": False},
]
for incident in incidents:
    severity = "critical" if incident["customer_effect"] and incident["financial_effect"] else (
        "high" if incident["customer_effect"] else "moderate"
    )
    response = "stop and rollback" if severity == "critical" else "investigate under incident procedure"
    print(incident["issue"], "->", severity, "->", response)""",
    66: """import hashlib
import json


changes = [
    {"version": "1.0", "change": "initial approval", "approver": "committee-A"},
    {"version": "1.1", "change": "calibration update", "approver": "committee-B"},
]
previous = "0" * 64
for change in changes:
    payload = json.dumps(change, sort_keys=True, separators=(",", ":"))
    current = hashlib.sha256((previous + payload).encode()).hexdigest()
    print(change["version"], current[:20])
    previous = current""",
}

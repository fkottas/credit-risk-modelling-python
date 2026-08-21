"""Generate original, source-free teaching figures from repository-created data."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

from creditriskbook.data import load_case_dataset, load_dataset, make_behavioral_credit_history
from creditriskbook.ifrs9 import constant_hazard_curve
from creditriskbook.irb import irb_capital

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "book" / "figures"
NAVY, BLUE, TEAL, GOLD, GREY = "#203748", "#2E74B5", "#1C8C8C", "#B28A38", "#667788"


def save(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def line_figure(x, ys, labels, title, xlabel, ylabel, name):
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    for y, label, color in zip(ys, labels, (BLUE, TEAL, GOLD, NAVY), strict=False):
        ax.plot(x, y, label=label, linewidth=2.2, color=color)
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    ax.grid(alpha=0.2)
    ax.legend(frameon=False)
    save(fig, name)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    retail = load_dataset("synthetic_retail", n_rows=6_000, seed=910).frame
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    loss = retail["default_12m"] * retail["lgd"] * retail["ead"]
    ax.hist(loss[loss > 0], bins=45, color=BLUE, alpha=0.78)
    ax.axvline(loss.mean(), color=GOLD, linewidth=2.2, label="portfolio mean loss")
    ax.set(
        title="Loss distribution: expected loss and tail", xlabel="account loss", ylabel="frequency"
    )
    ax.legend(frameon=False)
    save(fig, "part-01-loss-distribution.png")

    grouped = retail.groupby("product", observed=True)["default_12m"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    grouped.plot.bar(ax=ax, color=[TEAL, BLUE, GOLD])
    ax.set(title="Observed default rate by product", xlabel="product", ylabel="default rate")
    ax.tick_params(axis="x", rotation=0)
    save(fig, "part-02-product-risk.png")

    stages = load_case_dataset("synthetic_ifrs9_schedule", n_rows=500, seed=912).frame
    stage_counts = stages.drop_duplicates("account_id")["stage"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.bar(stage_counts.index.astype(str), stage_counts.values, color=[TEAL, GOLD, NAVY])
    ax.set(title="Synthetic IFRS 9 stage distribution", xlabel="stage", ylabel="accounts")
    save(fig, "part-03-stages.png")

    damaged = retail.copy(deep=True)
    rng = np.random.default_rng(913)
    defect_rates = {"income": 0.12, "debt_to_income": 0.08, "employment_years": 0.05}
    for column, rate in defect_rates.items():
        rows = rng.choice(damaged.index, size=int(rate * len(damaged)), replace=False)
        damaged.loc[rows, column] = np.nan
    damaged.loc[rng.choice(damaged.index, 150, replace=False), "age"] = -5
    damaged.loc[rng.choice(damaged.index, 210, replace=False), "debt_to_income"] = 1.8
    variables = ["income", "debt_to_income", "employment_years", "age"]
    missing = damaged[variables].isna().mean()
    invalid = pd.Series(
        {
            "income": damaged["income"].lt(0).mean(),
            "debt_to_income": damaged["debt_to_income"].gt(1).mean(),
            "employment_years": damaged["employment_years"].lt(0).mean(),
            "age": (~damaged["age"].between(18, 100)).mean(),
        }
    )
    y = np.arange(len(variables))
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.barh(y, missing[variables], color=BLUE, label="missing")
    ax.barh(y, invalid[variables], left=missing[variables], color=GOLD, label="rule breach")
    ax.set_yticks(y, variables)
    ax.set(
        title="Deliberately damaged teaching copy: quality profile",
        xlabel="share of records",
    )
    ax.legend(frameon=False)
    save(fig, "part-04-data-quality.png")

    bins = np.quantile(retail["debt_to_income"], np.linspace(0, 1, 7))
    idx = np.clip(np.digitize(retail["debt_to_income"], bins[1:-1]), 0, 5)
    rates = np.array([retail.loc[idx == i, "default_12m"].mean() for i in range(6)])
    line_figure(
        np.arange(1, 7),
        [rates],
        ["observed bad rate"],
        "Characteristic curve",
        "ordered bin",
        "bad rate",
        "part-05-characteristic.png",
    )

    fig, axes = plt.subplots(1, 3, figsize=(8.0, 3.7), sharey=True)
    tree_panels = [
        ("Parent", [6, 4], 0.48),
        ("Split after 5", [5, 0, 1, 4], 0.32),
        ("Split after 6", [6, 0, 0, 4], 0.48),
    ]
    for axis, (title, counts, gain) in zip(axes, tree_panels, strict=True):
        if len(counts) == 2:
            positions = [0]
            goods, bads = [counts[0]], [counts[1]]
            labels = ["node"]
        else:
            positions = [0, 1]
            goods, bads = counts[::2], counts[1::2]
            labels = ["left", "right"]
        axis.bar(positions, goods, color=TEAL, label="non-default")
        axis.bar(positions, bads, bottom=goods, color=GOLD, label="default")
        axis.set_xticks(positions, labels)
        axis.set_title(f"{title}\nGini gain = {gain:.2f}", color=NAVY, weight="bold")
        axis.set_ylim(0, 10)
        axis.grid(axis="y", alpha=0.18)
    axes[0].set_ylabel("observations")
    axes[-1].legend(frameon=False, loc="upper right", fontsize=8)
    fig.suptitle("Tree splitting compares weighted child impurity", color=NAVY, weight="bold")
    save(fig, "tree-split-gain.png")

    score = np.asarray(1.0 / (1.0 + np.exp(4.0 - 4.0 * retail["utilisation"])))
    cuts = np.quantile(score, np.linspace(0, 1, 11))
    bucket = np.clip(np.digitize(score, cuts[1:-1]), 0, 9)
    predicted = np.array([score[bucket == i].mean() for i in range(10)])
    observed = np.array([retail.loc[bucket == i, "default_12m"].mean() for i in range(10)])
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.plot([0, 1], [0, 1], linestyle="--", color=GREY)
    ax.plot(predicted, observed, marker="o", color=BLUE)
    ax.set(
        title="Calibration is distinct from discrimination",
        xlabel="mean predicted PD",
        ylabel="observed default rate",
    )
    save(fig, "part-06-calibration.png")

    months = np.arange(1, 61)
    curves = [constant_hazard_curve(p, 60).cumsum() for p in (0.01, 0.03, 0.08)]
    line_figure(
        months,
        curves,
        ["1% 12m PD", "3% 12m PD", "8% 12m PD"],
        "Lifetime cumulative PD",
        "month",
        "cumulative PD",
        "part-07-lifetime-pd.png",
    )

    scenarios = stages.assign(base=lambda x: x.marginal_pd * x.lgd * x.ead)
    totals = [scenarios.base.sum() * m for m in (0.72, 1.0, 1.48)]
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.bar(["upside", "base", "downside"], totals, color=[TEAL, BLUE, GOLD])
    ax.set(title="Scenario ECL before probability weighting", ylabel="undiscounted ECL")
    save(fig, "part-08-scenario-ecl.png")

    pd_grid = np.geomspace(0.0005, 0.20, 80)
    irb = irb_capital(
        pd_grid,
        np.full(80, 0.45),
        np.ones(80),
        maturity_years=np.full(80, 2.5),
        asset_class="corporate",
        annual_sales_eur_millions=np.full(80, 100.0),
    )
    line_figure(
        pd_grid,
        [irb.rows["risk_weighted_assets"]],
        ["corporate IRB"],
        "IRB risk-weight sensitivity",
        "PD",
        "risk weight",
        "part-09-irb-sensitivity.png",
    )

    cutoffs = np.linspace(0.01, 0.30, 60)
    profit = 900 * (score[:, None] < cutoffs).mean(axis=0) - 4_500 * (
        (score[:, None] < cutoffs) * retail["default_12m"].to_numpy()[:, None]
    ).mean(axis=0)
    line_figure(
        cutoffs,
        [profit],
        ["illustrative expected margin"],
        "Cutoff economics",
        "PD cutoff",
        "value per applicant",
        "part-10-cutoff-economics.png",
    )

    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    labels = ["data", "prediction", "calibration", "outcome", "fairness"]
    values = [0.05, 0.11, 0.08, 0.17, 0.06]
    ax.bar(labels, values, color=[TEAL, BLUE, GOLD, NAVY, GREY])
    ax.axhline(0.10, color="#B44", linestyle="--", label="illustrative alert line")
    ax.set(title="Monitoring layers must be separated", ylabel="normalized movement")
    ax.legend(frameon=False)
    save(fig, "part-11-monitoring-layers.png")

    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.axis("off")
    boxes = [
        (0.06, 0.66, "Evidence\nregistry"),
        (0.38, 0.66, "Specialist\nproposal"),
        (0.70, 0.66, "Policy\ngate"),
        (0.38, 0.22, "Human\napproval"),
    ]
    for x, y, text in boxes:
        ax.add_patch(
            plt.Rectangle((x, y), 0.22, 0.18, facecolor="#EEF3F7", edgecolor=BLUE, linewidth=1.6)
        )
        ax.text(x + 0.11, y + 0.09, text, ha="center", va="center", color=NAVY, weight="bold")
    for start, end in [
        ((0.28, 0.75), (0.38, 0.75)),
        ((0.60, 0.75), (0.70, 0.75)),
        ((0.81, 0.66), (0.55, 0.40)),
    ]:
        ax.annotate(
            "", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "color": GOLD, "lw": 2}
        )
    ax.set_title(
        "Governed agent: evidence, proposal, gate, and human authority", color=NAVY, weight="bold"
    )
    save(fig, "part-12-agent-governance.png")

    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    pipeline = [
        (0.07, 0.70, "1  Immutable source\nbytes + SHA-256", "Original evidence"),
        (0.38, 0.70, "2  Parsed text\npage + offsets", "Versioned extraction"),
        (0.69, 0.70, "3  Evidence chunks\nhash + access label", "Retrieval candidates"),
        (0.22, 0.27, "4  Ranked passages\nBM25 + as-of filter", "Inspectable support"),
        (0.56, 0.27, "5  Structured memo\nclaim + citation", "Human-review input"),
    ]
    for x, y, label, note in pipeline:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                0.24,
                0.15,
                boxstyle="round,pad=0.018",
                facecolor="#EEF3F7",
                edgecolor=BLUE,
                linewidth=1.7,
            )
        )
        ax.text(x + 0.12, y + 0.09, label, ha="center", va="center", color=NAVY, weight="bold")
        ax.text(x + 0.12, y - 0.035, note, ha="center", va="top", color=GREY, fontsize=8.5)
    for start, end in [
        ((0.31, 0.775), (0.38, 0.775)),
        ((0.62, 0.775), (0.69, 0.775)),
        ((0.81, 0.70), (0.46, 0.42)),
        ((0.46, 0.345), (0.56, 0.345)),
    ]:
        ax.annotate(
            "", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "color": GOLD, "lw": 2}
        )
    ax.text(
        0.50,
        0.08,
        "A citation is valid only when the original span supports the claim and was accessible at the decision time.",
        ha="center",
        color="#8A3B2E",
        weight="bold",
        fontsize=9.3,
    )
    ax.set_title("Document-to-evidence pipeline", color=NAVY, weight="bold", fontsize=14)
    save(fig, "nlp-document-evidence-pipeline.png")

    fig, ax = plt.subplots(figsize=(8.0, 5.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    architecture = [
        (0.06, 0.70, 0.24, 0.15, "Approved evidence\nscoped + versioned", TEAL),
        (0.38, 0.70, 0.24, 0.15, "Bounded assistant\nextract + retrieve", BLUE),
        (0.70, 0.70, 0.24, 0.15, "Action proposal\nno execution token", GOLD),
        (0.38, 0.38, 0.24, 0.15, "Deterministic gate\nrole + scope + evidence", NAVY),
        (0.38, 0.10, 0.24, 0.15, "Human authority\nreview + signed decision", TEAL),
    ]
    for x, y, width, height, label, edge in architecture:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                width,
                height,
                boxstyle="round,pad=0.02",
                facecolor="#F6F8FA",
                edgecolor=edge,
                linewidth=1.9,
            )
        )
        ax.text(
            x + width / 2,
            y + height / 2,
            label,
            ha="center",
            va="center",
            color=NAVY,
            weight="bold",
        )
    for start, end in [
        ((0.30, 0.775), (0.38, 0.775)),
        ((0.62, 0.775), (0.70, 0.775)),
        ((0.82, 0.70), (0.59, 0.53)),
        ((0.50, 0.38), (0.50, 0.25)),
    ]:
        ax.annotate(
            "", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "color": GOLD, "lw": 2}
        )
    ax.text(0.12, 0.48, "READ-ONLY\nTOOLS", ha="center", color=TEAL, weight="bold", fontsize=9)
    ax.text(
        0.85,
        0.46,
        "DENY: approve / decline\nprice / deploy / post",
        ha="center",
        color="#A33",
        weight="bold",
        fontsize=9,
    )
    ax.text(
        0.50,
        0.02,
        "The model proposes. Deterministic policy and an authorised human control action.",
        ha="center",
        color=GREY,
        fontsize=9.2,
    )
    ax.set_title("Governed document-agent architecture", color=NAVY, weight="bold", fontsize=14)
    save(fig, "nlp-governed-agent-architecture.png")

    behavioural = make_behavioral_credit_history(n_customers=300, months=18, seed=920)
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    ax.axis("off")
    boxes = [
        (0.05, 0.64, "Application\n1 row / decision"),
        (0.39, 0.64, "Contract\n1 row / facility"),
        (0.70, 0.64, "Monthly history\n1 row / facility-month"),
        (0.39, 0.18, "Bureau enquiry\n1 row / event"),
    ]
    for x, y, label in boxes:
        ax.add_patch(
            plt.Rectangle((x, y), 0.25, 0.18, facecolor="#EEF3F7", edgecolor=BLUE, linewidth=1.6)
        )
        ax.text(x + 0.125, y + 0.09, label, ha="center", va="center", color=NAVY, weight="bold")
    for start, end in [
        ((0.30, 0.73), (0.39, 0.73)),
        ((0.64, 0.73), (0.70, 0.73)),
        ((0.175, 0.64), (0.48, 0.36)),
    ]:
        ax.annotate(
            "", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "color": GOLD, "lw": 2}
        )
    ax.set_title(
        "Relational credit data: keys and units come before features", color=NAVY, weight="bold"
    )
    save(fig, "data-relational-architecture.png")

    selected = behavioural.applications.iloc[0]
    customer_id = selected["customer_id"]
    history = behavioural.monthly_performance.loc[
        behavioural.monthly_performance["customer_id"] == customer_id
    ]
    monthly = history.groupby("snapshot_date", as_index=False).agg(dpd=("dpd", "max"))
    reference = pd.Timestamp(selected["reference_date"])
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.step(monthly["snapshot_date"], monthly["dpd"], where="mid", color=BLUE, linewidth=2.2)
    ax.axvspan(
        reference - pd.DateOffset(months=6),
        reference,
        color=GOLD,
        alpha=0.16,
        label="six-month window",
    )
    ax.axvline(reference, color=NAVY, linestyle="--", label="reference date")
    ax.axhline(30, color=GREY, linestyle=":", label="30 DPD threshold")
    ax.set(
        title="DPD path becomes max, last, count and recency features",
        xlabel="snapshot date",
        ylabel="days past due",
    )
    ax.legend(frameon=False, ncol=2)
    save(fig, "behavioral-dpd-window.png")

    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.axis("off")
    steps = [
        (0.03, "Preserve\nraw row"),
        (0.27, "Apply\nrule"),
        (0.51, "Record\nissue"),
        (0.75, "Clean or\nquarantine"),
    ]
    for x, label in steps:
        ax.add_patch(
            FancyBboxPatch(
                (x, 0.42),
                0.18,
                0.22,
                boxstyle="round,pad=0.02",
                facecolor="#EEF3F7",
                edgecolor=BLUE,
                linewidth=1.6,
            )
        )
        ax.text(x + 0.09, 0.53, label, ha="center", va="center", color=NAVY, weight="bold")
    for x in (0.21, 0.45, 0.69):
        ax.annotate(
            "",
            xy=(x + 0.06, 0.53),
            xytext=(x, 0.53),
            arrowprops={"arrowstyle": "->", "color": GOLD, "lw": 2},
        )
    ax.text(
        0.50,
        0.20,
        "No silent imputation, capping or overwriting",
        ha="center",
        color="#A33",
        weight="bold",
    )
    ax.set_title(
        "Auditable cleaning is a controlled disposition process", color=NAVY, weight="bold"
    )
    save(fig, "data-cleaning-quarantine-flow.png")

    contracts = behavioural.contracts.loc[
        behavioural.contracts["customer_id"] == customer_id
    ].sort_values("open_date")
    fig, ax = plt.subplots(figsize=(8.0, 4.0))
    y = np.arange(len(contracts))
    ax.scatter(contracts["open_date"], y, s=70, color=BLUE)
    ax.axvspan(reference - pd.DateOffset(months=6), reference, color=GOLD, alpha=0.18)
    ax.axvline(reference, color=NAVY, linestyle="--")
    ax.set_yticks(y, contracts["contract_id"].str[-2:])
    ax.set(
        title="Contract openings inside the six-month lookback",
        xlabel="open date",
        ylabel="contract suffix",
    )
    save(fig, "behavioral-contract-window.png")

    print(f"Generated 16 original figures in {OUT}")


if __name__ == "__main__":
    main()

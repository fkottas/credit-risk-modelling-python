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

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10.5,
        "axes.titlesize": 13,
        "axes.titleweight": "semibold",
        "axes.labelsize": 10.5,
        "axes.edgecolor": "#8B98A5",
        "axes.linewidth": 0.8,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "legend.fontsize": 9.2,
        "grid.color": "#D9E0E6",
        "grid.linewidth": 0.7,
        "figure.facecolor": "white",
    }
)


def save(fig: plt.Figure, name: str) -> None:
    fig.tight_layout(pad=1.15)
    fig.savefig(OUT / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def line_figure(x, ys, labels, title, xlabel, ylabel, name):
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    for y, label, color in zip(ys, labels, (BLUE, TEAL, GOLD, NAVY), strict=False):
        ax.plot(x, y, label=label, linewidth=2.2, color=color)
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    ax.grid(alpha=0.65)
    if len(labels) > 1:
        ax.legend(
            frameon=False,
            ncol=min(3, len(labels)),
            loc="upper center",
            bbox_to_anchor=(0.5, -0.18),
        )
    save(fig, name)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    retail = load_dataset("synthetic_retail", n_rows=6_000, seed=910).frame
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    loss = retail["default_12m"] * retail["lgd"] * retail["ead"]
    ax.hist(loss[loss > 0], bins=45, color=BLUE, alpha=0.78)
    ax.axvline(loss.mean(), color=GOLD, linewidth=2.2, label="portfolio mean loss")
    ax.set(
        title="Distribution of realised account loss",
        xlabel="account loss (EUR)",
        ylabel="accounts",
    )
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.17))
    save(fig, "part-01-loss-distribution.png")

    grouped = retail.groupby("product", observed=True)["default_12m"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    grouped.plot.bar(ax=ax, color=[TEAL, BLUE, GOLD])
    ax.set(
        title="Default rate by product in the synthetic portfolio",
        xlabel="product",
        ylabel="observed default rate",
    )
    ax.tick_params(axis="x", rotation=0)
    save(fig, "part-02-product-risk.png")

    stages = load_case_dataset("synthetic_ifrs9_schedule", n_rows=500, seed=912).frame
    stage_counts = stages.drop_duplicates("account_id")["stage"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.bar(stage_counts.index.astype(str), stage_counts.values, color=[TEAL, GOLD, NAVY])
    ax.set(
        title="Stage distribution in the synthetic IFRS 9 case", xlabel="stage", ylabel="accounts"
    )
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
        title="Missing and invalid observations after controlled defect injection",
        xlabel="share of records",
    )
    ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.17))
    save(fig, "part-04-data-quality.png")

    bins = np.quantile(retail["debt_to_income"], np.linspace(0, 1, 7))
    idx = np.clip(np.digitize(retail["debt_to_income"], bins[1:-1]), 0, 5)
    rates = np.array([retail.loc[idx == i, "default_12m"].mean() for i in range(6)])
    line_figure(
        np.arange(1, 7),
        [rates],
        ["observed bad rate"],
        "Observed default rate by ordered scorecard bin",
        "ordered bin",
        "bad rate",
        "part-05-characteristic.png",
    )

    fig, axes = plt.subplots(1, 3, figsize=(8.0, 3.7), sharey=True)
    tree_panels = [
        ("Parent", [6, 4], "Gini impurity", 0.48),
        ("Split after 5", [5, 0, 1, 4], "Gini gain", 0.32),
        ("Split after 6", [6, 0, 0, 4], "Gini gain", 0.48),
    ]
    for axis, (title, counts, metric, value) in zip(axes, tree_panels, strict=True):
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
        axis.set_title(f"{title}\n{metric} = {value:.2f}", color=NAVY, weight="bold")
        axis.set_ylim(0, 10)
        axis.grid(axis="y", alpha=0.18)
    axes[0].set_ylabel("observations")
    handles, labels_tree = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels_tree, frameon=False, ncol=2, loc="lower center")
    fig.suptitle("Candidate tree splits and weighted Gini impurity", color=NAVY, weight="bold")
    fig.subplots_adjust(bottom=0.18)
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
        title="Calibration of predicted and observed default rates",
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
        "Lifetime cumulative probability of default",
        "month",
        "cumulative PD",
        "part-07-lifetime-pd.png",
    )

    scenarios = stages.assign(base=lambda x: x.marginal_pd * x.lgd * x.ead)
    totals = [scenarios.base.sum() * m for m in (0.72, 1.0, 1.48)]
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.bar(["upside", "base", "downside"], totals, color=[TEAL, BLUE, GOLD])
    ax.set(
        title="Expected credit loss by scenario before probability weighting",
        xlabel="scenario",
        ylabel="undiscounted ECL (EUR)",
    )
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
        "Corporate IRB risk-weight sensitivity to PD",
        "probability of default",
        "risk-weight ratio",
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
        "Expected value by approval threshold in the synthetic case",
        "approval threshold for predicted PD",
        "expected value per applicant (EUR)",
        "part-10-cutoff-economics.png",
    )

    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    labels = [
        "input data",
        "score distribution",
        "approval outcomes",
        "12-month calibration",
        "12-month group outcomes",
    ]
    availability_month = [0, 0, 0, 12, 12]
    colours = [TEAL, BLUE, GREY, GOLD, NAVY]
    y_position = np.arange(len(labels))
    ax.barh(y_position, availability_month, color=colours, height=0.58)
    ax.scatter(availability_month, y_position, color=colours, s=55, zorder=3)
    ax.set_yticks(y_position, labels)
    ax.invert_yaxis()
    ax.set_xticks([0, 3, 6, 9, 12])
    ax.set(
        title="Availability of monitoring evidence for a 12-month PD model",
        xlabel="months after a scoring date",
        ylabel="",
        xlim=(-0.5, 12.8),
    )
    ax.grid(axis="x", alpha=0.65)
    save(fig, "part-11-monitoring-layers.png")

    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.axis("off")
    boxes = [
        (0.06, 0.66, "Evidence\nregistry"),
        (0.38, 0.66, "Specialist\nproposal"),
        (0.70, 0.66, "Authority\ncheck"),
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
    ax.set_title("Restricted-authority agent workflow", color=NAVY, weight="bold")
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
        (0.38, 0.70, 0.24, 0.15, "Document assistant\nextract + retrieve", BLUE),
        (0.70, 0.70, 0.24, 0.15, "Recommendation only\nno execution access", GOLD),
        (0.38, 0.38, 0.24, 0.15, "Authorisation rules\nrole + scope + evidence", NAVY),
        (0.38, 0.10, 0.24, 0.15, "Authorised reviewer\nreview + signed decision", TEAL),
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
        "The assistant proposes; deterministic rules and an authorised reviewer control execution.",
        ha="center",
        color=GREY,
        fontsize=9.2,
    )
    ax.set_title(
        "Document-assistant architecture with separated authority",
        color=NAVY,
        weight="bold",
        fontsize=14,
    )
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
    ax.set_title("Observation units and keys in relational credit data", color=NAVY, weight="bold")
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
        title="Six-month delinquency history at the reference date",
        xlabel="snapshot date",
        ylabel="days past due",
    )
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    save(fig, "behavioral-dpd-window.png")

    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.axis("off")
    steps = [
        (0.03, "Preserve\nraw row"),
        (0.27, "Apply\nrule"),
        (0.51, "Record\nissue"),
        (0.75, "Accept or\nrecord exception"),
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
        "Retain the source value and record every correction",
        ha="center",
        color="#A33",
        weight="bold",
    )
    ax.set_title("Traceable data cleaning and exception handling", color=NAVY, weight="bold")
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
        title="Contract openings in the six-month observation window",
        xlabel="open date",
        ylabel="contract suffix",
    )
    save(fig, "behavioral-contract-window.png")

    # Chapter 1: distinguish scheduled payments, recoveries, costs and discounted loss.
    months_cf = np.array([1, 2, 3])
    contractual = np.array([350.0, 350.0, 350.0])
    payments = np.array([350.0, 200.0, 0.0])
    recoveries = np.array([0.0, 0.0, 120.0])
    costs = np.array([0.0, 5.0, 15.0])
    shortfall = contractual - payments - recoveries + costs
    discounted = shortfall * (1.12 ** (-months_cf / 12.0))
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    width = 0.17
    ax.bar(months_cf - 1.5 * width, contractual, width, color=BLUE, label="contractual")
    ax.bar(months_cf - 0.5 * width, payments, width, color=TEAL, label="payment")
    ax.bar(months_cf + 0.5 * width, recoveries, width, color=GOLD, label="recovery")
    ax.bar(months_cf + 1.5 * width, discounted, width, color=NAVY, label="discounted loss")
    for month, value in zip(months_cf, discounted, strict=True):
        ax.text(month + 1.5 * width, value + 9, f"{value:.2f}", ha="center", fontsize=8)
    ax.set(
        title=f"Cash-flow loss components (present value = EUR {discounted.sum():.2f})",
        xlabel="month",
        ylabel="EUR",
        xticks=months_cf,
    )
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.14))
    save(fig, "cash-flow-loss-decomposition.png")

    # Chapter 17: the horizon distinction is architectural, not a naming change.
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    ax.set_xlim(0, 36)
    ax.set_ylim(0, 4)
    ax.set_yticks([3.2, 2.2, 1.2], ["IFRS 9 Stage 1", "IFRS 9 Stage 2", "CECL"])
    ax.axvspan(0, 12, ymin=0.69, ymax=0.88, color=BLUE, alpha=0.82)
    ax.axvspan(0, 36, ymin=0.44, ymax=0.63, color=GOLD, alpha=0.75)
    ax.axvspan(0, 36, ymin=0.19, ymax=0.38, color=TEAL, alpha=0.78)
    ax.axvline(12, color=GREY, linestyle="--", linewidth=1.3)
    ax.text(
        6,
        3.2,
        "12-month default-event\nhorizon",
        ha="center",
        va="center",
        color="white",
        weight="bold",
        fontsize=8.5,
    )
    ax.text(18, 2.2, "lifetime ECL after SICR", ha="center", va="center", color=NAVY, weight="bold")
    ax.text(
        18,
        1.2,
        "expected lifetime loss from initial recognition",
        ha="center",
        va="center",
        color="white",
        weight="bold",
        fontsize=9,
    )
    ax.set(
        title="Loss-recognition horizons under IFRS 9 and CECL",
        xlabel="months from reporting / recognition date",
    )
    ax.grid(axis="x", alpha=0.18)
    save(fig, "ifrs9-cecl-horizon.png")

    # Chapter 20: licensing and analytical suitability for candidate data sources.
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    licence_boxes = [
        (0.05, 0.72, "Original publisher\nand exact file"),
        (0.38, 0.72, "Explicit current\nterms and attribution"),
        (0.71, 0.72, "Purpose, privacy\nand target fit"),
        (0.08, 0.25, "Bundle\nwith notice"),
        (0.40, 0.25, "Download locally\nby code"),
        (0.72, 0.25, "Exclude or seek\nwritten permission"),
    ]
    for x, y_box, label in licence_boxes:
        ax.add_patch(
            FancyBboxPatch(
                (x, y_box),
                0.22,
                0.15,
                boxstyle="round,pad=0.018",
                facecolor="#EEF3F7" if y_box > 0.5 else "white",
                edgecolor=BLUE if y_box > 0.5 else GOLD,
                linewidth=1.7,
            )
        )
        ax.text(
            x + 0.11,
            y_box + 0.075,
            label,
            ha="center",
            va="center",
            color=NAVY,
            weight="bold",
            fontsize=9,
        )
    for start, end in [
        ((0.27, 0.795), (0.38, 0.795)),
        ((0.60, 0.795), (0.71, 0.795)),
        ((0.82, 0.72), (0.19, 0.40)),
        ((0.82, 0.72), (0.51, 0.40)),
        ((0.82, 0.72), (0.83, 0.40)),
    ]:
        ax.annotate(
            "", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "color": GOLD, "lw": 1.8}
        )
    ax.text(
        0.50,
        0.08,
        "The permitted treatment follows the source terms and the intended use.",
        ha="center",
        color="#A33",
        weight="bold",
    )
    ax.set_title("Dataset licensing and analytical suitability", color=NAVY, weight="bold")
    save(fig, "dataset-licence-decision-gate.png")

    # Chapter 22: show the information cut-off and outcome horizon.
    fig, ax = plt.subplots(figsize=(8.0, 3.8))
    ax.set_xlim(-1, 19)
    ax.set_ylim(0, 1)
    ax.axvspan(0, 6, color=BLUE, alpha=0.20)
    ax.axvspan(6, 18, color=GOLD, alpha=0.20)
    ax.axvline(6, color=NAVY, linewidth=2.1)
    ax.annotate(
        "observation window\nfeatures available",
        xy=(3, 0.64),
        ha="center",
        va="center",
        color=NAVY,
        weight="bold",
    )
    ax.annotate(
        "performance window\ndefault is observed",
        xy=(12, 0.64),
        ha="center",
        va="center",
        color=NAVY,
        weight="bold",
    )
    ax.annotate(
        "reference / decision date",
        xy=(6, 0.30),
        xytext=(9.2, 0.18),
        arrowprops={"arrowstyle": "->", "color": NAVY},
        color=NAVY,
        weight="bold",
    )
    ax.scatter([14], [0.48], s=80, color="#A33", zorder=4)
    ax.text(14, 0.36, "default", ha="center", color="#A33", weight="bold")
    ax.set_xticks([0, 3, 6, 9, 12, 15, 18], ["-6", "-3", "0", "+3", "+6", "+9", "+12"])
    ax.set_yticks([])
    ax.set(
        title="Observation and performance windows for a 12-month target",
        xlabel="months relative to the reference date",
    )
    for spine in ("left", "right", "top"):
        ax.spines[spine].set_visible(False)
    save(fig, "observation-performance-windows.png")

    # Chapter 28: WOE is a distribution log-ratio; bad rate is a different quantity.
    goods = np.array([180.0, 130.0, 70.0, 30.0])
    bads = np.array([20.0, 40.0, 60.0, 70.0])
    woe = np.log((goods / goods.sum()) / (bads / bads.sum()))
    bad_rate = bads / (goods + bads)
    bins_woe = np.arange(1, 5)
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    colors = [TEAL if value >= 0 else GOLD for value in woe]
    ax.bar(bins_woe, woe, color=colors, alpha=0.88, label="WOE")
    ax.axhline(0, color=GREY, linewidth=1)
    ax.set(
        xlabel="ordered characteristic bin",
        ylabel="WOE = log(good share / bad share)",
        title="Weight of evidence and observed default rate by bin",
        xticks=bins_woe,
    )
    ax2 = ax.twinx()
    ax2.plot(bins_woe, bad_rate, color=NAVY, marker="o", linewidth=2.1, label="bad rate")
    ax2.set_ylabel("observed bad rate")
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(
        lines + lines2,
        labels + labels2,
        frameon=False,
        ncol=2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
    )
    save(fig, "woe-logodds-characteristic.png")

    # Chapter 29: show the objective actually used by the from-scratch IRLS estimator.
    x_irls = np.array([-2.0, -1.0, 0.5, 1.0, 2.0])
    y_irls = np.array([0.0, 0.0, 0.0, 1.0, 1.0])
    design = np.column_stack([np.ones(len(x_irls)), x_irls])
    beta = np.zeros(2)
    l2 = 0.02
    penalty = np.diag([0.0, l2])
    objectives = []
    for _ in range(9):
        eta = design @ beta
        p_hat = np.where(eta >= 0, 1.0 / (1.0 + np.exp(-eta)), np.exp(eta) / (1.0 + np.exp(eta)))
        p_safe = np.clip(p_hat, 1e-12, 1 - 1e-12)
        objectives.append(
            float(
                -np.mean(y_irls * np.log(p_safe) + (1 - y_irls) * np.log(1 - p_safe))
                + 0.5 * beta @ penalty @ beta
            )
        )
        weights = np.clip(p_hat * (1 - p_hat), 1e-9, 0.25)
        gradient = -(design.T @ (y_irls - p_hat)) / len(y_irls) + penalty @ beta
        hessian = (design.T * weights) @ design / len(y_irls) + penalty
        beta = beta - np.linalg.solve(hessian, gradient)
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.plot(range(len(objectives)), objectives, marker="o", color=BLUE, linewidth=2.2)
    ax.set(
        title="Convergence of penalised logistic regression by IRLS",
        xlabel="Newton iteration",
        ylabel="average penalised negative log-likelihood",
    )
    ax.grid(alpha=0.2)
    ax.text(
        0.98, 0.04, "The intercept is not penalised", transform=ax.transAxes, ha="right", color=NAVY
    )
    save(fig, "irls-objective-convergence.png")

    # Chapter 30: points-to-double-the-odds has a precise log-odds geometry.
    pd_grid_score = np.geomspace(0.005, 0.30, 180)
    odds = (1 - pd_grid_score) / pd_grid_score
    factor = 20.0 / np.log(2.0)
    scaled_score = 600.0 + factor * np.log(odds / 50.0)
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.semilogx(pd_grid_score, scaled_score, color=BLUE, linewidth=2.3)
    p_50, p_100 = 1 / 51, 1 / 101
    ax.scatter([p_50, p_100], [600, 620], color=[GOLD, TEAL], s=70, zorder=4)
    ax.annotate(
        "50:1 odds\nscore 600",
        (p_50, 600),
        xytext=(0.035, 575),
        arrowprops={"arrowstyle": "->", "color": GOLD},
        color=NAVY,
    )
    ax.annotate(
        "100:1 odds\nscore 620",
        (p_100, 620),
        xytext=(0.006, 642),
        arrowprops={"arrowstyle": "->", "color": TEAL},
        color=NAVY,
    )
    ax.set(
        title="Score scaling with 20 points to double the odds",
        xlabel="probability of default (log scale)",
        ylabel="score",
        ylim=(505, 660),
    )
    ax.grid(alpha=0.2)
    save(fig, "pdo-score-scale.png")

    # Chapter 38: hazard, marginal PD and cumulative PD must reconcile by construction.
    month_h = np.arange(1, 25)
    hazard = 0.006 + 0.0012 * month_h + 0.008 * np.exp(-(((month_h - 9) / 4.0) ** 2))
    survival_start = np.concatenate([[1.0], np.cumprod(1.0 - hazard[:-1])])
    marginal_pd = survival_start * hazard
    cumulative_pd = np.cumsum(marginal_pd)
    fig, ax = plt.subplots(figsize=(8.0, 4.3))
    ax.plot(month_h, hazard, color=GOLD, linewidth=2.1, label="conditional hazard")
    ax.plot(month_h, marginal_pd, color=TEAL, linewidth=2.1, label="marginal PD")
    ax.plot(month_h, cumulative_pd, color=BLUE, linewidth=2.4, label="cumulative PD")
    ax.set(
        title="Relationship between hazard, marginal PD, and cumulative PD",
        xlabel="month",
        ylabel="probability",
        ylim=(0, max(cumulative_pd) * 1.12),
    )
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    save(fig, "hazard-marginal-cumulative-pd.png")

    print(f"Generated 24 original figures in {OUT}")


if __name__ == "__main__":
    main()

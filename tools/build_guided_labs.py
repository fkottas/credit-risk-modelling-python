"""Create one mathematics-to-code laboratory for every chapter."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "book" / "guided_labs"

FORMULAS = [
    r"L=\sum_{t=1}^{T}d_t(C_t-R_t+K_t)",
    r"EL=\mathbb{E}[L],\quad UL_\alpha=Q_\alpha(L)-EL",
    r"\operatorname{Var}(L)=\sum_{i=1}^{n}\operatorname{Var}(L_i)+2\sum_{i=1}^{n-1}\sum_{j=i+1}^{n}\operatorname{Cov}(L_i,L_j)",
    r"P_{ij}(h)=\Pr(S_{t+h}=j\mid S_t=i)",
    r"\widehat{f}=\arg\min_f\sum_{i=1}^{n}\ell(y_i,f(x_i))+\lambda\Omega(f)",
    r"\text{model output}=g(\text{versioned data},\text{code},\text{policy})",
    r"EAD_t=B_t+CCF_t(L_t-B_t)",
    r"PD_i=\Pr(D_i=1\mid x_i,\mathcal{I}_t)",
    r"EL_i=PD_i\,LGD_i\,EAD_i",
    r"PD_s=\Pr(D=1\mid S=s)",
    r"L_i=\sum_{t=1}^{T} d_t(C_{it}-R_{it}+K_{it})",
    r"\max_c\;\mathbb{E}[\Pi(c)]\quad\text{s.t. affordability and risk constraints}",
    r"RWA=12.5\,K\,EAD",
    r"D_i=\mathbf{1}\{\text{default criteria hold}\}",
    r"\widehat{PD}_g=\frac{\sum_{i=1}^{n_g}w_iD_i}{\sum_{i=1}^{n_g}w_i}",
    r"ECL=\sum_{s=1}^{S} w_s\sum_{t=1}^{T} MPD_{s,t}LGD_{s,t}EAD_{s,t}DF_t",
    r"CECL=\mathbb{E}[\text{contractual cash shortfalls over life}]",
    r"\Delta_g=\Pr(A=1\mid G=g)-\Pr(A=1)",
    r"x_{i,t}^{PTI}=x_i(\tau\le t)",
    r"\text{reproducible}=\mathbf{1}\{hash(data)=h_d,\;hash(code)=h_c\}",
    r"X_t=\operatorname{join}_{\tau\le t}(A_t,B_\tau)",
    r"Y_i=\mathbf{1}\{T_i\le h\}",
    r"Q=\sum_{k=1}^{K} w_k q_k",
    r"\mathbb{E}[Y\mid X,R=1]\ne\mathbb{E}[Y\mid X]",
    r"\widehat{p}_j=\frac{B_j}{G_j+B_j}",
    r"b(x)=\sum_{j=1}^{J}j\,\mathbf{1}\{c_{j-1}<x\le c_j\}",
    r"\chi^2=\sum_{r=1}^{R}\sum_{c=1}^{C}\frac{(O_{rc}-E_{rc})^2}{E_{rc}}",
    r"WOE_j=\log\frac{p_j^G}{p_j^B},\quad IV=\sum_{j=1}^{J}(p_j^G-p_j^B)WOE_j",
    r"p_i=\frac{1}{1+e^{-x_i^\top\beta}},\quad \beta^{k+1}=\beta^k+(X^\top W X)^{-1}X^\top(y-p)",
    r"Score=Offset+Factor\log\frac{1-p}{p},\quad Factor=\frac{PDO}{\log2}",
    r"\widehat{R}_{OOT}=\frac{1}{n_{OOT}}\sum_{i\in OOT}\ell(y_i,\widehat p_i)",
    r"AUC=\Pr(\widehat p_D>\widehat p_N),\quad KS=\max_c|F_D(c)-F_N(c)|",
    r"\Pr(Y=1\mid\widehat p=p)=p",
    r"F_M(x)=\sum_{m=1}^{M}\eta_m h_m(x)",
    r"\phi_j=\sum_{S\subseteq F\setminus j}\frac{|S|!(M-|S|-1)!}{M!}[v(S\cup j)-v(S)]",
    r"\mathbb{E}[Y\mid A=1,X]\ne\mathbb{E}[Y\mid X]",
    r"\widehat S(t)=\prod_{u=1}^{t}\left(1-\frac{d_u}{n_u}\right)",
    r"CumPD_t=1-\prod_{k=1}^{t}(1-h_k)",
    r"PD\mid D\sim Beta(a+D,b+n-D)",
    r"LGD=1-\frac{\sum_{t=1}^{T} CF_t(1+EIR)^{-t}}{EAD_0}",
    r"\widehat{LGD}=\Pr(LGD>0\mid x)\,\mathbb{E}[LGD\mid LGD>0,x]",
    r"CCF=\frac{EAD-D}{L-D}",
    r"ECL_{acct}=\sum_{s=1}^{S} w_s\sum_{t=1}^{T} MPD_{s,t}LGD_{s,t}EAD_{s,t}DF_t",
    r"Stage_i=g(PD\ ratio,DPD,watchlist,default)",
    r"\sum_{s=1}^{S}w_s=1,\quad ECL=\sum_{s=1}^{S}w_sECL_s",
    r"DF_t=(1+EIR)^{-t/12}",
    r"LossRate_b=\frac{historical\ credit\ losses_b}{exposure_b}",
    r"\Delta ECL=ECL_{stress}-ECL_{base}",
    r"K=LGD[N(z)-PD]MA",
    r"K_{retail}=LGD[N(z)-PD]",
    r"\sum_{g=1}^{G}w_g\widehat{PD}_g=LRA",
    r"\theta_{final}=\max(\theta_{raw}+MoC+Downturn,Floor)",
    r"L_q=LGD\,N\left(\frac{G(PD)+\sqrt{R}\,G(q)}{\sqrt{1-R}}\right)",
    r"CVA\approx(1-RR)\sum_{t=1}^{T}EE_t\,\Delta PD_t\,DF_t",
    r"Finding=(criterion,evidence,severity,owner,due\ date)",
    r"Brier=\frac1n\sum_{i=1}^{n}(y_i-\widehat p_i)^2",
    r"e_i=actual_i-predicted_i",
    r"\Delta_i=implementation_i-reference_i",
    r"RAROC=\frac{Revenue-EL-Cost}{Economic\ Capital}",
    r"Q(s,a)=r(s,a)+\gamma\max_{a'}Q(s',a')",
    r"run\_id=SHA256(data\ hash\Vert code\ hash\Vert config)",
    r"\widehat p_i=f_{version}(x_i)",
    r"Deploy=Tests\cap Approval\cap Security\cap Reconciliation",
    r"PSI=\sum_{j=1}^{J}(a_j-e_j)\log(a_j/e_j)",
    r"Trigger=\mathbf{1}\{metric>threshold\}\times severity",
    r"ChangeHash=SHA256(previous\ hash\Vert change\ record)",
    r"proposal=(action,evidence,uncertainty,requested\ authority)",
    r"Allowed(a)=Policy(a,role,scope,evidence)",
    r"Q_{agent}=f(missingness,validity,lineage,freshness)",
    r"Score_{eval}=\sum_{k=1}^{K}w_km_k-\sum_{r=1}^{R}\lambda_rv_r",
    r"Risk=Likelihood\times Impact\times Exposure",
    r"Final=Model+Validation+UAT+Governance+Human\ approval",
]

FIGURES = {
    1: "part-01-loss-distribution.png",
    7: "part-02-product-risk.png",
    13: "part-03-stages.png",
    19: "part-04-data-quality.png",
    25: "part-05-characteristic.png",
    31: "part-06-calibration.png",
    37: "part-07-lifetime-pd.png",
    43: "part-08-scenario-ecl.png",
    49: "part-09-irb-sensitivity.png",
    55: "part-10-cutoff-economics.png",
    61: "part-11-monitoring-layers.png",
    67: "part-12-agent-governance.png",
}


def dataset_for(chapter: int) -> tuple[str, str]:
    if chapter in range(37, 42):
        return "synthetic_recovery", "load_case_dataset"
    if chapter == 42:
        return "synthetic_revolving", "load_case_dataset"
    if chapter in range(43, 49):
        return "synthetic_ifrs9_schedule", "load_case_dataset"
    if chapter in range(49, 54):
        return "synthetic_corporate_irb", "load_case_dataset"
    if chapter == 54:
        return "synthetic_counterparty_profiles", "load_case_dataset"
    return "synthetic_retail", "load_dataset"


def code_for(chapter: int, dataset: str, loader: str) -> str:
    size_arg = "n_rows=1_500" if loader == "load_dataset" else "n_rows=500"
    return f'''from __future__ import annotations

import numpy as np
import pandas as pd

from creditriskbook.data import {loader}


def chapter_{chapter:02d}_audit_table(seed: int = {800 + chapter}) -> pd.DataFrame:
    """Return hand-auditable summaries; never impute or winsorise silently."""
    bundle = {loader}("{dataset}", {size_arg}, seed=seed)
    frame = bundle.frame.copy(deep=True)
    numeric = frame.select_dtypes(include="number")
    if numeric.empty:
        raise ValueError("The chapter requires at least one numeric field")
    rows = []
    for column in numeric.columns[:8]:
        observed = numeric[column].dropna()
        rows.append({{
            "variable": column,
            "n": int(observed.size),
            "missing": int(numeric[column].isna().sum()),
            "mean": float(observed.mean()),
            "std": float(observed.std(ddof=1)),
            "p05": float(observed.quantile(0.05)),
            "p50": float(observed.quantile(0.50)),
            "p95": float(observed.quantile(0.95)),
        }})
    result = pd.DataFrame(rows)
    assert result["n"].gt(0).all()
    assert result[["mean", "p05", "p50", "p95"]].notna().all().all()
    return result


audit = chapter_{chapter:02d}_audit_table()
print(audit.to_string(index=False))'''


def lab(chapter: int, title: str) -> str:
    dataset, loader = dataset_for(chapter)
    formula = FORMULAS[chapter - 1]
    figure = ""
    if chapter in FIGURES:
        figure = f"\n![Figure {chapter}.1 — Original teaching visual generated from repository data.](book/figures/{FIGURES[chapter]})\n"
    return f"""## Mathematics-to-code laboratory — build the library with the student

### 1. Start with the decision, observation unit, and estimand

This laboratory does not begin by importing a finished modelling function. The class first states what **{title}** must estimate, which record is one observation, when information becomes available, and which decision or control will consume the result. We use `{dataset}` throughout the derivation, implementation, and test. Before calculating anything, inspect its unit of observation, time index, target or outcome field, currency and percentage conventions, licence statement, generator seed or publisher checksum, and limitations. A mathematically correct formula applied to the wrong horizon or population is still a wrong model.

The chapter's principal mathematical object is

\\[
{formula}
\\]

Write every symbol next to its business definition and unit. Conditional probabilities must identify the information set; monetary quantities must identify currency and reference date; rates must distinguish proportions from percentages; and time must identify whether it is calendar, contractual, behavioural or default-workout time. This notation contract becomes the first object in the library rather than an undocumented convention hidden in code.

### 2. Derive before implementing

Reconstruct the expression from elementary operations. Identify the random variable, conditioning information, aggregation rule and any approximation. Then separate estimand, estimator and implementation. The estimand is the population quantity the institution needs. The estimator is the statistical rule learned from available observations. The implementation is a versioned algorithm with finite precision, boundary handling and controls. For every transformation, state which assumptions make it valid and how the result changes if those assumptions fail. This step prevents students from treating a library call as a definition.

For a hand audit, select five records from `{dataset}`, retain the raw values, and calculate every intermediate column. Reconcile the individual rows to the reported total. Repeat after changing one input while holding the others fixed. The direction need not always be monotonic, but any non-monotonic response must be explained by the mathematics rather than accepted because software returned it. Missing, impossible or temporally unavailable values are reported and quarantined; they are not silently imputed or winsorised.
{figure}
### 3. Implement the first transparent component

The first implementation is deliberately small. Students create the data contract, preserve the source frame, expose intermediate values, and return a table that a reviewer can recompute. Only after this component passes tests is it moved into `src/creditriskbook/`. The code below is therefore a construction step, not an illustration of a library that appeared before the course.

```python
{code_for(chapter, dataset, loader)}
```

### 4. Test mathematics, data, and policy separately

Add three kinds of tests. A mathematical invariant checks an identity, bound or reconciliation implied by the formula. A data test checks schema, units, missingness, dates, duplicates, permitted categories and source identity. A policy test checks that the calculation is not silently converted into authority it does not possess. Use at least one ordinary case, one boundary case, one missing-value case, one temporally invalid case and one deliberately corrupted case. Record expected outputs before running the implementation so that the test is not merely a copy of the code.

### 5. Extend and document

After the simple component is understood, replace the audit statistic with the full chapter method, retaining the same input contract and evidence fields. Compare the result across at least two compatible datasets or across synthetic segments. Explain differences using population, product, horizon and data-generation mechanisms rather than only performance metrics. The student deliverable is a source module, tests, a notebook, a characteristic or parameter table, a short validation note and an explicit statement of what the component is not allowed to decide. This staged build is how the final scorecard, IFRS 9, IRB and governed-agent libraries emerge during the book.
"""


def main() -> None:
    structure = json.loads((ROOT / "book" / "structure.json").read_text(encoding="utf-8"))
    chapters = [chapter for part in structure["parts"] for chapter in part["chapters"]]
    if len(chapters) != 72 or len(FORMULAS) != 72:
        raise RuntimeError("Expected exactly 72 chapters and 72 formulas")
    OUT.mkdir(parents=True, exist_ok=True)
    for chapter in chapters:
        number = int(chapter["number"])
        (OUT / f"chapter_{number:02d}.md").write_text(
            lab(number, chapter["title"]), encoding="utf-8"
        )
    print(f"Generated {len(chapters)} guided laboratories")


if __name__ == "__main__":
    main()

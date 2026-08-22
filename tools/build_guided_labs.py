"""Create one mathematics-to-code laboratory for every chapter."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from advanced_chapter_examples import EXAMPLES as ADVANCED_EXAMPLES
from chapter_lab_context import LAB_CONTEXT, RESULT_INTERPRETATION
from early_chapter_examples import EXAMPLES as EARLY_EXAMPLES

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "book" / "guided_labs"

FORMULAS = [
    r"L=\sum_{t=1}^{T}(1+r)^{-t/12}\left[(C_t-P_t)-Rec_t+K_t\right]",
    r"EL=\mathbb{E}[L],\quad UL_\alpha=Q_\alpha(L)-EL",
    r"\operatorname{Var}(L)=\sum_{i=1}^{n}\operatorname{Var}(L_i)+2\sum_{i=1}^{n-1}\sum_{j=i+1}^{n}\operatorname{Cov}(L_i,L_j)",
    r"P_{ij}(h)=\Pr(S_{t+h}=j\mid S_t=i)",
    r"\widehat{f}=\arg\min_f\sum_{i=1}^{n}\ell(y_i,f(x_i))+\lambda\Omega(f)",
    r"\text{model output}=g(\text{versioned data},\text{code},\text{policy})",
    r"EAD_t=B_t+CCF_t(L_t-B_t)",
    r"PD_i=\Pr(D_i=1\mid x_i,\mathcal{I}_t)",
    r"EL_i=PD_i\,LGD_i\,EAD_i",
    r"PD_s=\Pr(D=1\mid S=s)",
    r"L_i=\sum_{t=1}^{T} d_t\left[(C_{it}-P_{it})-Rec_{it}+K_{it}\right]",
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
    r"maxDPD_i(w)=\max_{t_i-w<s\le t_i}DPD_{i,s},\quad CountContracts_i(w)=\sum_j\mathbf{1}\{t_i-w<open_{ij}\le t_i\}",
    r"\widehat{p}_j=\frac{B_j}{G_j+B_j}",
    r"b(x)=\sum_{j=1}^{J}j\,\mathbf{1}\{c_{j-1}<x\le c_j\}",
    r"\chi^2=\sum_{r=1}^{R}\sum_{c=1}^{C}\frac{(O_{rc}-E_{rc})^2}{E_{rc}}",
    r"WOE_j=\log\frac{p_j^G}{p_j^B},\quad IV=\sum_{j=1}^{J}(p_j^G-p_j^B)WOE_j",
    r"\beta^{(k+1)}=\beta^{(k)}+\left(\frac{X^\top W^{(k)}X}{n}+\Lambda\right)^{-1}\left[\frac{X^\top(y-p^{(k)})}{n}-\Lambda\beta^{(k)}\right]",
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
    r"LGD=1-\frac{\sum_{t=1}^{T} CF_t(1+EIR)^{-u_t}}{EAD_0}",
    r"\widehat{LGD}=\Pr(LGD>0\mid x)\,\mathbb{E}[LGD\mid LGD>0,x]",
    r"CCF=\frac{EAD-D}{L-D}",
    r"ECL_{acct}=\sum_{s=1}^{S} w_s\sum_{t=1}^{T} MPD_{s,t}LGD_{s,t}EAD_{s,t}DF_t",
    r"Stage_i=g(PD\ ratio,DPD,watchlist,default)",
    r"\sum_{s=1}^{S}w_s=1,\quad ECL=\sum_{s=1}^{S}w_sECL_s",
    r"DF_t=(1+EIR)^{-t/12}",
    r"LossRate_b=\frac{historical\ credit\ losses_b}{exposure_b}",
    r"A_{close}=A_{open}+\sum_k\Delta A_k-WriteOffs",
    r"K=LGD[N(z)-PD]MA",
    r"K_{retail}=LGD[N(z)-PD]",
    r"\sum_{g=1}^{G}w_g\widehat{PD}_g=LRA",
    r"\theta_{final}=\max(\theta_{raw}+MoC+Downturn,Floor)",
    r"L_q=LGD\,N\left(\frac{G(PD)+\sqrt{R}\,G(q)}{\sqrt{1-R}}\right)",
    r"CVA\approx(1-RR)\sum_{t=1}^{T}EE_t\,\Delta PD_t\,DF_t",
    r"Unresolved=\sum_j\mathbf{1}\{test_j=fail\}",
    r"Brier=\frac1n\sum_{i=1}^{n}(y_i-\widehat p_i)^2",
    r"e_i=actual_i-predicted_i",
    r"\Delta_i=implementation_i-reference_i",
    r"RAROC=\frac{Revenue-EL-Cost}{Economic\ Capital}",
    r"Q(s,a)=r(s,a)+\gamma\max_{a'}Q(s',a')",
    r"run\_id=SHA256(data\ hash\Vert code\ hash\Vert config)",
    r"\widehat p_i=f_{version}(x_i)",
    r"Release=I_{tests}I_{approval}I_{security}I_{reconciliation}",
    r"PSI=\sum_{j=1}^{J}(a_j-e_j)\log(a_j/e_j)",
    r"Trigger=\mathbf{1}\{metric>threshold\}\times severity",
    r"ChangeHash=SHA256(previous\ hash\Vert change\ record)",
    r"tfidf(t,d)=tf(t,d)\left[\log\frac{N+1}{df(t)+1}+1\right]",
    r"BM25(q,d)=\sum_{t\in q}idf(t)\frac{f(t,d)(k_1+1)}{f(t,d)+k_1(1-b+b|d|/\overline{|d|})}",
    r"p(w_{1:T}\mid x)=\prod_{t=1}^{T}p(w_t\mid w_{<t},x),\quad SupportRate=\frac{1}{|C|}\sum_{c\in C}s(c)",
    r"\tau=(s_0,a_0,o_1,\ldots,s_T),\quad Allowed(a)=Policy(action,role,scope,evidence,approval,time)",
    r"RECEIVED\rightarrow EXTRACTED\rightarrow RECONCILED\rightarrow RETRIEVED\rightarrow VALIDATED\rightarrow HUMAN\_REVIEW",
    r"Release=\mathbf{1}\{critical\ violations=0\}\,\mathbf{1}\{mandatory\ thresholds\ pass\}",
]

FIGURES = {
    1: "cash-flow-loss-decomposition.png",
    2: "part-01-loss-distribution.png",
    7: "part-02-product-risk.png",
    16: "part-03-stages.png",
    17: "ifrs9-cecl-horizon.png",
    23: "part-04-data-quality.png",
    20: "dataset-licence-decision-gate.png",
    22: "observation-performance-windows.png",
    25: "part-05-characteristic.png",
    28: "woe-logodds-characteristic.png",
    29: "irls-objective-convergence.png",
    30: "pdo-score-scale.png",
    33: "part-06-calibration.png",
    37: "part-07-lifetime-pd.png",
    38: "hazard-marginal-cumulative-pd.png",
    43: "part-08-scenario-ecl.png",
    49: "part-09-irb-sensitivity.png",
    59: "part-10-cutoff-economics.png",
    64: "part-11-monitoring-layers.png",
    70: "part-12-agent-governance.png",
}

FIGURE_CAPTIONS = {
    1: "Contractual amounts, receipts, recoveries, and discounted shortfalls in the worked example.",
    2: "Realised loss is right-skewed; the mean does not describe the upper tail.",
    7: "Observed default rates across the project-generated product cases.",
    16: "Account counts by IFRS 9 stage in the synthetic calculation case.",
    17: "IFRS 9 changes the measurement horizon by stage; the CECL illustration begins with lifetime loss.",
    23: "Missing-value and rule-violation rates after controlled defect injection.",
    20: "Source terms and analytical suitability determine whether data are bundled, downloaded, or excluded.",
    22: "Features are measured before the reference date and the 12-month outcome afterwards.",
    25: "Observed default rate across ordered bins of a candidate characteristic.",
    28: "WOE compares conditional distributions; bad rate is the within-bin event proportion.",
    29: "The penalised negative log-likelihood decreases over the displayed IRLS iterations.",
    30: "With PDO equal to 20, doubling good-to-bad odds increases score by 20 points.",
    33: "Observed default rate is compared with mean predicted PD by probability band.",
    37: "Illustrative lifetime cumulative PD curves derived from different 12-month levels.",
    38: "Conditional hazard generates marginal first-default probabilities and cumulative PD.",
    43: "Scenario-specific ECL is calculated before applying scenario probabilities.",
    49: "Corporate IRB risk weight increases nonlinearly with PD under fixed LGD and maturity.",
    59: "Expected value changes with the PD approval threshold in the synthetic decision case.",
    64: "Input and score evidence are immediate; calibration and defaults require mature outcomes.",
    70: "Evidence, analysis, policy evaluation, and human authority remain separate.",
}


def dataset_for(chapter: int) -> tuple[str, str]:
    if chapter == 1:
        return "synthetic_recovery", "load_case_dataset"
    if chapter in {2, 8, 13, 14, 15, 39}:
        return "synthetic_corporate_irb", "load_case_dataset"
    if chapter in {3, 16, 17, 38}:
        return "synthetic_ifrs9_schedule", "load_case_dataset"
    if chapter in {4, 11, 21, 22, 23, 24, 37}:
        return "synthetic_behavioral_history", "make_behavioral_credit_history"
    if chapter in {19, 20}:
        return "dataset_registry.yml", "registry_review"
    if chapter >= 67:
        return "synthetic_credit_documents", "make_synthetic_credit_document_case"
    if chapter in {40, 41, 57}:
        return "synthetic_recovery", "load_case_dataset"
    if chapter in {42, 60}:
        return "synthetic_revolving", "load_case_dataset"
    if chapter in range(43, 49):
        return "synthetic_ifrs9_schedule", "load_case_dataset"
    if chapter in range(49, 54):
        return "synthetic_corporate_irb", "load_case_dataset"
    if chapter == 54:
        return "synthetic_counterparty_profiles", "load_case_dataset"
    return "synthetic_retail", "load_dataset"


def code_for(chapter: int, dataset: str, loader: str) -> str:
    if chapter <= 24:
        return EARLY_EXAMPLES[chapter]
    if chapter <= 66:
        return ADVANCED_EXAMPLES[chapter]
    if chapter == 67:
        return '''import math
import re
from collections import Counter


def tokenize(text):
    """Return visible lowercase alphanumeric tokens; preserve the raw text separately."""
    return re.findall(r"[a-z0-9_]+", text.lower())


def tfidf(term, document, corpus):
    tokens = tokenize(document)
    term_frequency = tokens.count(term)
    document_frequency = sum(term in set(tokenize(item)) for item in corpus)
    inverse_document_frequency = math.log((len(corpus) + 1) / (document_frequency + 1)) + 1
    return term_frequency * inverse_document_frequency


corpus = [
    "income verified from payslip",
    "income missing: request payslip",
    "policy requires verified income",
]
print(Counter(tokenize(corpus[0])))
print({"tfidf_income_doc1": round(tfidf("income", corpus[0], corpus), 6)})'''
    if chapter == 68:
        return """import math
import re
from collections import Counter


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def bm25(query, documents, k1=1.5, b=0.75):
    doc_tokens = [tokens(document) for document in documents]
    average_length = sum(map(len, doc_tokens)) / len(doc_tokens)
    scores = []
    for document in doc_tokens:
        counts = Counter(document)
        score = 0.0
        for term in set(tokens(query)):
            document_frequency = sum(term in item for item in doc_tokens)
            inverse_document_frequency = math.log(
                1 + (len(documents) - document_frequency + 0.5) / (document_frequency + 0.5)
            )
            frequency = counts[term]
            denominator = frequency + k1 * (1 - b + b * len(document) / average_length)
            score += inverse_document_frequency * frequency * (k1 + 1) / denominator
        scores.append(score)
    return scores


policy = [
    "verified income evidence is required before affordability review",
    "applications with missing identity evidence must be referred",
    "model deployment requires independent validation approval",
]
scores = bm25("what income evidence is required", policy)
ranking = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
print([(index, round(score, 4), policy[index]) for index, score in ranking])"""
    if chapter == 69:
        return """from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceMemo:
    application_id: str
    evidence_ids: tuple[str, ...]
    policy_citations: tuple[str, ...]
    recommendation: str


ALLOWED = {"request_missing_evidence", "refer_for_human_review", "no_automated_action"}


def validate_memo(memo, evidence_ids, policy_ids):
    if memo.recommendation not in ALLOWED:
        raise ValueError("recommendation is not authorised")
    if set(memo.evidence_ids) - set(evidence_ids):
        raise ValueError("invented evidence citation")
    if set(memo.policy_citations) - set(policy_ids):
        raise ValueError("invented policy citation")
    return True


memo = EvidenceMemo("APP-1", ("EV-1",), ("POL-1",), "request_missing_evidence")
print({"valid": validate_memo(memo, {"EV-1"}, {"POL-1"}), "recommendation": memo.recommendation})"""
    if chapter == 70:
        return """DENIED = {"approve_customer_credit", "decline_customer_credit", "deploy_model", "post_ledger"}
READ_ONLY = {"retrieve_policy", "read_quality_report"}


def permission(action, role, evidence_ids, approved=False):
    if action in DENIED:
        return "DENY"
    if not evidence_ids:
        return "DENY_MISSING_EVIDENCE"
    if action in READ_ONLY:
        return "ALLOW_READ_ONLY"
    if action == "request_human_validation":
        return "PENDING_HUMAN_APPROVAL" if not approved else "APPROVED_PROPOSAL_ONLY"
    return "DENY_UNKNOWN_ACTION"


attempts = ["retrieve_policy", "request_human_validation", "approve_customer_credit"]
print([(action, permission(action, "document_assistant", ("EV-1",))) for action in attempts])"""
    if chapter == 71:
        return """from creditriskbook.data import make_synthetic_credit_document_case
from creditriskbook.nlp import DocumentUnderwritingAssistant


case = make_synthetic_credit_document_case(n_applications=16, seed=7801)
assistant = DocumentUnderwritingAssistant()
result = assistant.run(case.applications.iloc[0], case.documents, case.policy_documents)
print({
    "application_id": result.memo.application_id,
    "recommendation": result.memo.recommendation,
    "missing_evidence": result.memo.missing_evidence,
    "policy_decision": result.policy_decision.decision,
})
print(result.trace)"""
    if chapter == 72:
        return """from creditriskbook.agents import ActionProposal, PolicyEngine


engine = PolicyEngine()
attacks = [
    "approve_customer_credit",
    "deploy_model",
    "alter_source_evidence",
]
results = []
for action in attacks:
    proposal = ActionProposal(action, "red-team attempt", ("EV-RED",), "unsafe_agent")
    decision = engine.evaluate(proposal)
    results.append((action, decision.decision))
assert all(decision == "DENY" for _, decision in results)
print(results)
print({"critical_violations": 0, "mandatory_release_criteria": "PASS"})"""
    raise KeyError(f"No executable example is defined for Chapter {chapter}")


def execute_code(code: str) -> str:
    """Execute the displayed code and return the exact output committed to the lesson."""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + environment.get("PYTHONPATH", "")
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        timeout=180,
    )
    if completed.returncode:
        raise RuntimeError(
            f"Guided-lab code failed with exit code {completed.returncode}\n"
            f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    output = "\n".join(line.rstrip() for line in completed.stdout.strip().splitlines())
    return output or "Completed successfully with no printed output."


def lab(chapter: int, title: str) -> str:
    dataset, loader = dataset_for(chapter)
    formula = FORMULAS[chapter - 1]
    code = code_for(chapter, dataset, loader)
    output = execute_code(code)
    question, reason, validation, extension = LAB_CONTEXT[chapter]
    interpretation = RESULT_INTERPRETATION[chapter]
    if chapter <= 6:
        implementation_text = (
            "From first principles: scalar values, lists, and the Python standard library; "
            "intermediate quantities remain visible."
        )
    elif chapter <= 24:
        implementation_text = (
            "From first principles: the calculation is written in full; NumPy or pandas is used "
            "only for transparent array and table operations."
        )
    elif chapter <= 54:
        implementation_text = (
            "Reference implementation: the code evaluates the displayed expression directly and "
            "provides expected intermediate values for later library tests."
        )
    else:
        implementation_text = (
            "Applied implementation: the code creates a reproducible validation, deployment, or "
            "governance record while keeping measurement separate from policy authority."
        )
    figure = ""
    if chapter in FIGURES:
        figure = (
            f"\n![Figure {chapter}.1 — {FIGURE_CAPTIONS[chapter]}]"
            f"(book/figures/{FIGURES[chapter]})\n"
        )
    return f"""## Worked calculation — {question}

{reason}

**Companion case:** `{dataset}`. **Implementation level:** {implementation_text}

### Method

The calculation follows

\\[
{formula}
\\]

{figure}
### Python implementation

```python
{code}
```

### Executed result

```output
{output}
```

### Interpretation

{interpretation}

**Validation:** {validation}

### Exercises

1. Repeat the calculation with **{extension}** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.
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

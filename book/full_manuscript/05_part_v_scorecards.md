# Chapter 25 — Exploratory and Characteristic Analysis

## Explore the process, not only distributions

Scorecard development begins after the population, target and split are frozen. Exploration should describe volumes, dates, products, channels, missingness, event rates and feature behaviour across time. A variable with a strong full-sample relationship may reverse by vintage or represent a policy rule already applied to accepted cases.

Characteristic analysis evaluates one predictor across interpretable groups. For each bin report count, population share, goods, bads, bad rate, WOE, IV component and eventual points. Add time and segment views. A summary slide should not hide zero-event bins, sparse bins or missing values.

The first characteristic table is written without the project package. Its tiny fixture makes every denominator visible.

```python
import pandas as pd


def characteristic_table(frame, feature, target):
    result = (
        frame.groupby(feature, dropna=False, observed=True)[target]
        .agg(observations="size", bads="sum", bad_rate="mean")
        .reset_index()
    )
    result["goods"] = result["observations"] - result["bads"]
    result["share"] = result["observations"] / len(frame)
    return result[[feature, "observations", "goods", "bads", "bad_rate", "share"]]


fixture = pd.DataFrame(
    {
        "utilisation_band": ["low", "low", "medium", "medium", "high", "high", "high"],
        "default_12m": [0, 0, 0, 1, 0, 1, 1],
    }
)
print(characteristic_table(fixture, "utilisation_band", "default_12m").to_string(index=False))
```

```output
utilisation_band  observations  goods  bads  bad_rate    share
            high             3      1     2  0.666667 0.428571
             low             2      2     0  0.000000 0.285714
          medium             2      1     1  0.500000 0.285714
```

The presentation generator creates a title, characteristic summary and one slide per feature with bad rates and a bin table. It is deliberately not a one-click approval pack. Sample dates, population, cut-point rationale, stability, exclusions, judgement and sign-off must be added.

## Univariate traps

Information value is descriptive within a chosen sample and binning. High IV may indicate useful separation, leakage, selection or overfitting. Correlated variables can each look strong but become unstable together. An apparent U-shape may be real or a sparse-tail artefact. Missing-bin performance may change when the application form changes.

Review plots by development, validation and out-of-time sample using the development cuts. Never re-bin the validation set to make its relationship attractive.

**Lab.** Produce a characteristic pack for eight variables. For each, write keep, merge, transform, investigate or exclude, with business and statistical reasons.

# Chapter 26 — Manual Numeric and Categorical Binning

## Why manual binning remains important

Manual bins encode product knowledge, operational thresholds and stable interpretation. Examples include DPD backstops, utilisation bands, term options and documented income ranges. Manual does not mean arbitrary: each cut requires evidence, minimum counts, event support, monotonicity review and validation.

Numeric bins should cover $(-\infty,+\infty)$, with missing and special values explicit. Special values such as -999 must not be treated as economic numbers. Categorical grouping combines levels with similar risk and meaning; rare categories may be grouped, but protected or materially different categories should not be hidden merely to smooth bad rates. Unseen production levels require a defined `OTHER` policy.

```python
import math

import pandas as pd


def manual_numeric_bin(value, edges, special_values=(-999.0,)):
    """Apply frozen right-closed cuts; never learn an edge while scoring."""
    if pd.isna(value):
        return "MISSING"
    if value in special_values:
        return f"SPECIAL:{value:g}"
    boundaries = [-math.inf, *sorted(edges), math.inf]
    for index, (left, right) in enumerate(zip(boundaries[:-1], boundaries[1:]), start=1):
        if left < value <= right:
            return f"BIN_{index}:({left:g},{right:g}]"
    raise AssertionError("unreachable")


def manual_categorical_bin(value, groups):
    if pd.isna(value):
        return "MISSING"
    for label, members in groups.items():
        if value in members:
            return label
    return "OTHER"


values = [-999.0, None, 0.0, 1.0, 2.5, 8.0]
print([manual_numeric_bin(value, [0, 1, 3, 6]) for value in values])
groups = {"instalment": {"personal_loan"}, "revolving": {"credit_card"}}
print([manual_categorical_bin(value, groups) for value in ["personal_loan", "credit_card", "new_product", None]])
```

```output
['SPECIAL:-999', 'MISSING', 'BIN_1:(-inf,0]', 'BIN_2:(0,1]', 'BIN_3:(1,3]', 'BIN_5:(6,inf]']
['instalment', 'revolving', 'OTHER', 'MISSING']
```

Intervals use right-closed semantics and labels are stored with the bin specification. Training and scoring call the same `transform`; cut points are never recomputed at scoring time.

## Manual-bin policy

The binning memo should include variable definition, available time, raw distribution, cut alternatives, final edges, special handling, missing treatment, event counts, WOE, stability, business rationale and approver. If a policy threshold changes, decide whether it is a policy update or model change; do not quietly edit a cut in production.

**Lab.** Manually bin utilisation using business bands and compare with equal-frequency bins. Apply both to an out-of-time sample. Choose based on stability and meaning, not maximum development IV.

# Chapter 27 — Automated Quantile, Equal-Width, ChiMerge, and Monotonic Binning

## Candidate algorithms

Quantile binning targets similar counts and is robust to skew, but repeated values can collapse edges. Equal-width binning preserves the measurement scale but can create sparse tails. ChiMerge begins with fine ordered intervals and repeatedly merges the adjacent pair with the smallest Pearson chi-square difference in good/bad composition. A monotonic variant continues merging violations until bad rates move in one direction.

We implement these algorithms without a scorecard package. The complete library version first creates pre-bins, applies minimum population and event/non-event constraints, merges by chi-square to `max_bins`, and optionally enforces a trend. Missing and special values stay outside the ordered merge.

For adjacent bins with observed table $O_{rc}$, Pearson’s statistic is

\[
\chi^2=\sum_{r=1}^{R}\sum_{c=1}^{C}\frac{(O_{rc}-E_{rc})^2}{E_{rc}}.
\]

A small value means the two adjacent bins have similar class composition and are candidates for merging. This is a heuristic, not proof that the final grouping is optimal or stable.

```python
import numpy as np


def pair_chi_square(left, right):
    observed = np.array(
        [[left["goods"], left["bads"]], [right["goods"], right["bads"]]], dtype=float
    )
    expected = observed.sum(axis=1, keepdims=True) @ observed.sum(axis=0, keepdims=True)
    expected /= observed.sum()
    contributions = np.divide(
        (observed - expected) ** 2,
        expected,
        out=np.zeros_like(expected),
        where=expected > 0,
    )
    return float(contributions.sum())


def chimerge(prebins, max_bins):
    bins = [dict(item) for item in prebins]
    while len(bins) > max_bins:
        scores = [pair_chi_square(bins[i], bins[i + 1]) for i in range(len(bins) - 1)]
        i = int(np.argmin(scores))
        left, right = bins[i], bins[i + 1]
        merged = {
            "lower": left["lower"],
            "upper": right["upper"],
            "goods": left["goods"] + right["goods"],
            "bads": left["bads"] + right["bads"],
        }
        bins[i : i + 2] = [merged]
    return bins


prebins = [
    {"lower": 0, "upper": 1, "goods": 40, "bads": 4},
    {"lower": 1, "upper": 2, "goods": 35, "bads": 5},
    {"lower": 2, "upper": 3, "goods": 20, "bads": 10},
    {"lower": 3, "upper": 4, "goods": 10, "bads": 12},
]
print(chimerge(prebins, max_bins=3))
```

```output
[{'lower': 0, 'upper': 2, 'goods': 75, 'bads': 9}, {'lower': 2, 'upper': 3, 'goods': 20, 'bads': 10}, {'lower': 3, 'upper': 4, 'goods': 10, 'bads': 12}]
```

The first two pre-bins merge because their good/bad compositions are most similar. The production implementation adds deterministic tie-breaking, quantile and equal-width pre-bins, minimum shares, minimum goods and bads, missing/special isolation, monotonic-violation merging and serialisable interval specifications. Students add each control one at a time and write its boundary test before the function is promoted.

Automatic trend choice can be unstable when the true relationship is flat or U-shaped. Compare increasing and decreasing alternatives, bootstrap edges, and challenge business plausibility. A monotonic variable is not necessarily causal.

## Freeze and validate

Fit bins only on training data. Persist the complete specification. Test boundary values, infinities, missing, special and unseen categories. Calculate population stability using fixed development bins. Monitor share in `OTHER`; a spike may indicate a source change.

**Lab.** Fit quantile, uniform, ChiMerge and monotonic bins to the same six variables. Compare bin counts, IV, out-of-time PSI, minimum events and interpretation. Select a specification under a written policy.

# Chapter 28 — Weight of Evidence and Information Value from First Principles

## Definition and convention

For bin $j$, let $G_j$ and $B_j$ be goods and bads. With smoothing $a>0$ and $k$ bins,

\[
p^G_j=\frac{G_j+a}{\sum_{m=1}^{k}G_m+ak},\qquad
p^B_j=\frac{B_j+a}{\sum_{m=1}^{k}B_m+ak}.
\]

This book defines $WOE_j=\log(p^G_j/p^B_j)$. Positive WOE therefore indicates relatively more goods. Some software uses the opposite sign. Mixing conventions reverses coefficients and points; record the convention in every artifact.

Information value is

\[
IV=\sum_{j=1}^{k}(p^G_j-p^B_j)WOE_j.
\]

Smoothing prevents infinite WOE for zero-event bins but does not make them reliable. The smoothing value affects small bins and belongs in configuration.

```python
import numpy as np
import pandas as pd


def woe_iv(bin_counts, smoothing=0.5):
    table = bin_counts.copy()
    k = len(table)
    total_goods = table["goods"].sum() + smoothing * k
    total_bads = table["bads"].sum() + smoothing * k
    table["p_good"] = (table["goods"] + smoothing) / total_goods
    table["p_bad"] = (table["bads"] + smoothing) / total_bads
    table["woe"] = np.log(table["p_good"] / table["p_bad"])
    table["iv_component"] = (table["p_good"] - table["p_bad"]) * table["woe"]
    return table, float(table["iv_component"].sum())


counts = pd.DataFrame(
    {"bin": ["low", "medium", "high"], "goods": [80, 45, 15], "bads": [10, 20, 30]}
)
table, information_value = woe_iv(counts)
print(table.round(4).to_string(index=False))
print("IV =", round(information_value, 6))
```

```output
   bin  goods  bads  p_good  p_bad     woe  iv_component
   low     80    10  0.5689 0.1707  1.2036        0.4792
medium     45    20  0.3216 0.3333 -0.0360        0.0004
  high     15    30  0.1095 0.4959 -1.5101        0.5835
IV = 1.063185
```

WOE turns a nonlinear univariate relationship into a piecewise constant representation. A logistic coefficient then scales that characteristic after controlling for others. WOE does not solve multicollinearity, selection bias or temporal instability.

## Review standards

Investigate high IV, zero goods/bads, small bins, non-business ordering and missing-bin shifts. Compare WOE across time. Calculate bin-level PSI using fixed categories. If an unseen scoring category maps to neutral WOE, count and escalate it; neutrality is a fallback, not evidence of equal risk.

**Lab.** Calculate WOE by hand for three bins with and without smoothing. Reverse the event convention and verify how WOE changes. Explain why the final predicted PD can remain equivalent if coefficient signs change consistently.

# Chapter 29 — Logistic Regression by Maximum Likelihood and IRLS

## Model and likelihood

For WOE vector $x_i$, logistic regression assumes

\[
p_i=\frac{1}{1+\exp[-(\beta_0+x_i'\beta)]}.
\]

The unpenalised Bernoulli log-likelihood is

\[
\ell(\beta)=\sum_{i=1}^{n}\left[y_i\log p_i+(1-y_i)\log(1-p_i)\right].
\]

To make the regularisation parameter comparable when the training sample is duplicated or enlarged, this book minimises the **average** negative log-likelihood plus an L2 penalty:

\[
\mathcal{J}(\beta)=
-\frac{1}{n}\sum_{i=1}^{n}
\left[y_i\log p_i+(1-y_i)\log(1-p_i)\right]
+\frac{1}{2}\beta^{\top}\Lambda\beta,
\]

\[
\Lambda=\operatorname{diag}(0,\lambda,\ldots,\lambda).
\]

The zero in $\Lambda_{00}$ is deliberate: the intercept is not regularised. Let $Z$ be the design matrix after adding the intercept column, let $p$ be the vector of current probabilities and define

\[
W^{(k)}=\operatorname{diag}\left(p_i^{(k)}[1-p_i^{(k)}]\right).
\]

Differentiating the objective gives

\[
g(\beta)=\nabla\mathcal{J}(\beta)
=-\frac{1}{n}Z^{\top}(y-p)+\Lambda\beta,
\]

\[
H(\beta)=\nabla^2\mathcal{J}(\beta)
=\frac{1}{n}Z^{\top}WZ+\Lambda.
\]

Newton's method uses $\beta^{(k+1)}=\beta^{(k)}-H^{-1}g$. Substitution produces the penalised IRLS update

\[
\beta^{(k+1)}=\beta^{(k)}+
\left(\frac{1}{n}Z^{\top}W^{(k)}Z+\Lambda\right)^{-1}
\left[\frac{1}{n}Z^{\top}(y-p^{(k)})-\Lambda\beta^{(k)}\right].
\]

The inverse is mathematical notation, not an implementation instruction. Code solves the linear system. With observation weights $a_i$, replace $n$ by $\sum_i a_i$ and insert those weights in the score and information calculations.

| Symbol | Meaning | Shape or domain |
|---|---|---|
| $n,p$ | observations and non-intercept features | positive integers |
| $Z$ | design matrix, including a leading column of ones | $\mathbb{R}^{n\times(p+1)}$ |
| $y$ | default indicator, where one is the event | $\{0,1\}^n$ |
| $\beta$ | intercept and slope coefficients | $\mathbb{R}^{p+1}$ |
| $p_i$ | modelled event probability | mathematically in $(0,1)$ |
| $W$ | diagonal Bernoulli variance matrix | $W_{ii}=p_i(1-p_i)\in(0,0.25]$ |
| $\lambda$ | L2 penalty strength on slopes | $\lambda\ge0$ |
| $\Lambda$ | penalty matrix with unpenalised intercept | positive semidefinite |

For a hand-worked first iteration, take feature values $[-1,1]$, outcomes $[0,1]$ and $\lambda=0.1$. At $\beta^{(0)}=(0,0)^{\top}$, both probabilities equal $0.5$. Then

\[
Z=\begin{bmatrix}1&-1\\1&1\end{bmatrix},\qquad
g(\beta^{(0)})=\begin{bmatrix}0\\-0.5\end{bmatrix},\qquad
H(\beta^{(0)})=\begin{bmatrix}0.25&0\\0&0.35\end{bmatrix}.
\]

Thus $-H^{-1}g=(0,1.428571)^{\top}$ and

\[
\beta^{(1)}=(0,1.428571)^{\top}.
\]

The following standalone implementation exposes that exact update before the estimator is promoted into the course library [R63].

```python
import numpy as np


def stable_sigmoid(logit):
    logit = np.asarray(logit, dtype=float)
    probability = np.empty_like(logit)
    positive = logit >= 0
    probability[positive] = 1.0 / (1.0 + np.exp(-logit[positive]))
    exp_value = np.exp(logit[~positive])
    probability[~positive] = exp_value / (1.0 + exp_value)
    epsilon = np.finfo(float).eps
    return np.clip(probability, epsilon, 1.0 - epsilon)


def irls_step(design, y, beta, l2):
    n = len(design)
    probability = stable_sigmoid(design @ beta)
    variance = np.maximum(probability * (1.0 - probability), 1e-12)
    penalty = np.diag([0.0] + [l2] * (design.shape[1] - 1))
    score = design.T @ (y - probability) / n - penalty @ beta
    information = (design.T * variance) @ design / n + penalty
    return beta + np.linalg.solve(information, score)


def fit_logistic_irls(X, y, l2=1e-3, max_iter=100, tolerance=1e-9):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    if X.ndim != 2 or y.shape != (len(X),):
        raise ValueError("X must be two-dimensional and y must match its rows")
    if l2 < 0 or not np.isin(y, [0.0, 1.0]).all() or np.unique(y).size != 2:
        raise ValueError("Require l2 >= 0 and a binary target containing both classes")
    design = np.column_stack([np.ones(len(X)), X])
    beta = np.zeros(design.shape[1])
    for iteration in range(1, max_iter + 1):
        beta_next = irls_step(design, y, beta, l2)
        if np.max(np.abs(beta_next - beta)) < tolerance:
            return beta_next, iteration
        beta = beta_next
    raise RuntimeError("IRLS did not converge")


X_demo = np.array([[-1.0], [1.0]])
y_demo = np.array([0.0, 1.0])
Z_demo = np.column_stack([np.ones(len(X_demo)), X_demo])
beta_one = irls_step(Z_demo, y_demo, np.zeros(2), l2=0.1)
print("Beta after one update:", beta_one)

X_fit = np.array([[-1.5], [-1.0], [-0.5], [0.0], [0.5], [1.0], [1.5]])
y_fit = np.array([0, 0, 0, 0, 1, 1, 1])
beta, iterations = fit_logistic_irls(X_fit, y_fit, l2=0.02)
print({"beta": np.round(beta, 6).tolist(), "iterations": iterations})
```

```output
Beta after one update: [0.         1.42857143]
{'beta': [-0.725133, 2.861941], 'iterations': 7}
```

Changing from a summed likelihood to an average likelihood changes the numerical meaning of $\lambda$ unless the penalty is rescaled. State the convention in every model artefact. L2 regularisation reduces unstable magnitudes and produces finite estimates under many separation cases, but it changes inference. Full column rank is needed for the ordinary unpenalised inverse; a strictly positive ridge term can stabilise penalised slope directions, although an unidentified intercept or malformed design can still fail. Approximate standard errors rely on model assumptions and do not account for bin search, repeated observations or temporal dependence. Use bootstrap or clustered methods where appropriate.

Implementation invariants include an unpenalised intercept, probabilities within numerical bounds, a non-increasing objective under an accepted Newton step and nearly zero final score. A convergence flag proves only numerical optimisation. It does not prove correct labels, linear log odds, stable coefficients, calibration or fitness for use.

## Variable selection

Selection should combine business meaning, availability, univariate evidence, correlation, VIF, sign, stability and incremental performance. Stepwise p-values alone overfit. LASSO may select among correlated features arbitrarily. Keep a simple benchmark and document exclusions.

Filter, wrapper and embedded methods answer different questions. A Fisher score for variable $x_j$ compares between-class separation with within-class variation,

\[
F_j=\frac{(\bar{x}_{j,1}-\bar{x}_{j,0})^2}{s^2_{j,1}+s^2_{j,0}},
\]

while Cramér's $V$ describes association between two categorical variables from a contingency-table statistic,

\[
V=\sqrt{\frac{\chi^2/n}{\min(r-1,c-1)}}.
\]

Neither measure knows whether the field is available at the decision time, stable, explainable or lawful. A wrapper repeatedly fits models to candidate subsets and evaluates a predeclared out-of-time objective. This can discover combinations, but it multiplies selection noise; nested validation is needed if the reported performance is to include the search.

Embedded regularisation estimates coefficients and selects or shrinks them in one objective. For negative log-likelihood $-\ell(\beta)$,

\[
\widehat\beta_{ridge}=\arg\min_\beta\{-\ell(\beta)+\lambda\sum_{j=1}^{p}\beta_j^2\},
\]

\[
\widehat\beta_{lasso}=\arg\min_\beta\{-\ell(\beta)+\lambda\sum_{j=1}^{p}|\beta_j|\}.
\]

Ridge stabilises correlated coefficients but normally keeps them all. LASSO can set coefficients exactly to zero, yet may choose one of several correlated variables unpredictably. Elastic net combines both penalties. The intercept is normally unpenalised, and $\lambda$ must be selected inside the training process rather than against the final test period.

Principal-component analysis diagonalises the training covariance matrix $S$: $Sv_k=\lambda_kv_k$, with component $z_k=Xv_k$. It can compress correlated numeric variables, but components may be difficult to explain and can drift when the covariance structure changes. Fit loadings on training data only, freeze centring and scaling, retain the original feature lineage and compare the loss of business meaning with any performance benefit. Bayesian additive regression trees are a flexible nonlinear selection-and-interaction challenger: a prior regularises an ensemble of shallow trees, and posterior inclusion summaries express model uncertainty. They are not a replacement for point-in-time controls, independent validation or reason governance.

```python
import numpy as np


def fisher_score(values, target):
    good = np.asarray(values)[np.asarray(target) == 0]
    bad = np.asarray(values)[np.asarray(target) == 1]
    numerator = (bad.mean() - good.mean()) ** 2
    denominator = bad.var(ddof=1) + good.var(ddof=1)
    return numerator / denominator


x = np.array([0.10, 0.20, 0.25, 0.55, 0.70, 0.85])
y = np.array([0, 0, 0, 1, 1, 1])
print(round(fisher_score(x, y), 6))
```

```output
14.7
```

The score is deliberately hand-checkable: the two class means are $0.1833$ and $0.7000$, and the sample variances are $0.005833$ and $0.022500$. The ratio of squared mean difference to their sum is $14.7$. A large value signals separation in this fixture, not automatic admission to a model.

The expected coefficient sign depends on the WOE convention. With good-to-bad WOE and target 1=bad, a stable risk characteristic commonly receives a negative coefficient: higher WOE implies lower bad log odds.

**Lab.** Fit IRLS with L2 values from zero to 0.1. Compare convergence, coefficients, calibration and out-of-time performance. Identify unstable variables rather than choosing the smallest training loss.

# Chapter 30 — PDO Scaling, Bin Points, Ratings, and Reason Codes

## From log odds to a score

Let good-to-bad odds be $O=(1-p)/p$. A conventional linear score is

\[
Score=Offset+Factor\log O,
\]

where $Factor=PDO/\log 2$ and $Offset=BaseScore-Factor\log(BaseOdds)$. If base score is 600 at good-to-bad odds 20 and PDO is 50, doubling good odds increases score by 50.

Because the logistic model uses bad log odds $z=\log[p/(1-p)]$, score equals `offset - factor*z`. The intercept contributes base points and each characteristic contributes `-factor*beta*WOE`. The repository reconciles row components to total score before rounding and clipping.

This is the promotion checkpoint. The reader has already written characteristic summaries, frozen manual bins, an adjacent-bin ChiMerge loop, WOE/IV and IRLS. Those functions are moved into modules, given dataclasses and serialisable specifications, and surrounded by unit tests for event sign, boundaries, missing, special and unseen values, convergence and reconciliation. Only now do we call the assembled `LogisticScorecard`; the import is a reviewed version of the code just constructed, not a hidden scorecard dependency.

```python
from creditriskbook.scorecard import LogisticScorecard, ScoreScale

scorecard = LogisticScorecard(
    scale=ScoreScale(base_score=600, pdo=50, base_odds_good_to_bad=20),
    l2=1e-3,
).fit(train[features], train[bundle.target])

components = scorecard.score_components(test[features].head())
points = scorecard.points_table()
reasons = scorecard.reason_codes(test[features].head(), top_n=4)
print(components[["raw_total", "score", "pd", "rating"]])
print(reasons)
```

Ratings map score ranges to ordered grades. Grade boundaries should target risk differentiation, minimum population, monotonic PD, stability and business use. Calibrate grade PD separately; a label such as R1 has no universal PD.

Scorecard reason codes compare each selected bin’s points with the best observed bin for that characteristic and report the largest penalties. They are faithful to the additive scorecard. For XGBoost, the library uses sensitivity-based counterfactual reasons and labels them as such; it does not invent bin points.

## Implementation controls

Test probability-to-score round trips, PDO doubling, every bin boundary, missing/special/unseen values, row-level points reconciliation, rating boundaries and reason order. Store unrounded and final score. A policy decline reason may differ from a model reason, so preserve both.

**Lab.** Build a manual-plus-automatic scorecard, export CSV, HTML and PowerPoint characteristic packs, map scores to eight grades, and produce four reasons for twenty cases. Reconcile each score by hand for one account.

> Part V provides a complete scorecard implementation from raw variables to review presentation. Every transformation is inspectable, persisted and tested without a specialist scorecard library.

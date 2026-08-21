# Chapter 3 — Basel IRB, IFRS 9, CECL and Responsible Lending

## Same symbols, different objectives

IRB, IFRS 9, CECL, pricing and origination may all use PD, LGD and EAD, but the parameters are not interchangeable. Regulatory capital asks whether a bank can absorb unexpected loss under a prescribed prudential framework. IFRS 9 estimates probability-weighted discounted cash shortfalls for financial reporting. CECL estimates expected credit losses over the contractual term for assets in its scope under US GAAP. A decision model ranks or estimates risk at a customer action point. The objective determines horizon, calibration, conservatism, scenario treatment and governance.

The consolidated Basel Framework separates IRB overview, risk-weight functions, risk components and minimum requirements. CRE31 sets out risk-weight calculations; CRE32 sets out PD, LGD, EAD and maturity components [R1–R2]. European institutions must additionally interpret applicable CRR/CRD requirements, EBA guidelines and supervisory decisions. The EBA guidelines address PD and LGD estimation and defaulted exposures [R3]. This book's capital code illustrates a corporate risk-weight function; it does not determine IRB eligibility or calculate every jurisdictional adjustment.

## IRB calculation intuition

For corporate exposures, the framework maps PD into an asset correlation, combines the borrower's default threshold with a severe systematic factor, applies LGD, subtracts expected loss and adjusts for maturity. The code returns capital rate, capital amount and `RWA = 12.5 × capital`.

```python
from creditriskbook.capital import corporate_irb_capital

result = corporate_irb_capital(
    pd_values=[0.005, 0.02],
    lgd_values=[0.45, 0.45],
    ead_values=[1_000_000, 1_000_000],
    maturity_years=[2.5, 2.5],
)
```

The function applies an explicit teaching PD floor. A real implementation must source the applicable floor, exposure class, maturity treatment, CCF rules, downturn and conservatism requirements, output-floor implications and transitional rules. Those are legal and supervisory determinations, not parameters to guess in code.

## IFRS 9 impairment

The IFRS Foundation's project summary describes three impairment stages: Stage 1 generally recognises 12-month ECL; Stage 2 recognises lifetime ECL after a significant increase in credit risk; Stage 3 recognises lifetime ECL for credit-impaired assets and changes the interest-revenue basis [R4]. Twelve-month ECL is not the next twelve months of cash shortfalls. It is the portion of lifetime cash shortfalls arising from defaults possible in the next twelve months [R5].

An implementation needs contractual cash flows, expected cash flows, default and recovery timing, effective-interest discounting, scenarios and staging. The simplified engine in the repository uses constant hazard and average timing. It is useful for reconciliation exercises but is explicitly not a full accounting engine.

SICR is a change in credit risk since initial recognition, not merely a high current PD. Practical indicators can include relative or absolute lifetime PD change, delinquency, forbearance, watchlist status and qualitative information. Thresholds require rebuttal, validation and consistent treatment. Stage migration must be monitored by origination cohort and reason.

Scenario weighting should not be a hidden multiplier. Define coherent upside, base and downside paths; connect macro drivers to risk components; validate the satellite model; record scenario probabilities and governance; and calculate the nonlinear ECL under each scenario before weighting. Applying one average scenario to a nonlinear loss function can understate tail effects.

## CECL

FASB introduced CECL in Topic 326, replacing the incurred-loss approach for relevant US GAAP assets. FDIC resources describe its scope across financial assets measured at amortised cost, net investments in leases and off-balance-sheet credit exposures [R6]. CECL does not use IFRS 9's three-stage transfer logic. Institutions can use loss-rate, vintage, roll-rate, probability-of-default/LGD, discounted-cash-flow and other methods consistent with the portfolio and evidence. Forecast horizons and reversion to historical information must be documented.

## Responsible lending and protected characteristics

A variable can be predictive and still be inappropriate. Protected attributes should be retained in a separately controlled fairness dataset where lawful, while excluded from modelling unless a clear legal basis and purpose exist. Removing a protected field does not remove proxy effects. Geography, device, language, employment, education and transaction patterns may encode the same structure.

Fairness analysis includes data coverage, measurement error, approval and take-up selection, outcome definitions, group calibration, error rates, approval rates, pricing, reason codes and intersectional groups. A ratio or significance test is a diagnostic, not a legal conclusion. Applicable equality, consumer-protection, privacy and adverse-action rules require local counsel and compliance.

The EU AI Act classifies many systems used to evaluate natural persons' creditworthiness or credit score as high-risk, subject to its scope and exceptions. The official text distinguishes fraud detection and prudential capital purposes in specified circumstances [R7]. Do not collapse an origination score, an IFRS 9 model and an IRB model into one legal category. Determine the system's intended purpose, provider/deployer roles, technique, jurisdiction and deployment date.

## Model risk governance in 2026

The US federal banking agencies revised model-risk-management guidance in April 2026. Federal Reserve SR 26-2 retains core principles while emphasising a risk-based approach tailored to model profile, institution size and complexity [R9]. A project should record which guidance version applies rather than citing SR 11-7 from habit.

A robust model inventory contains purpose, owner, users, tier, data, methodology, limitations, validation, approvals, dependencies, implementation, monitoring, issues, changes and retirement. Agentic components are included even if they call third-party foundation models.

## Chapter deliverable

Create a parameter-purpose matrix with rows for application PD, pricing PD, IFRS 9 12-month PD, IFRS 9 lifetime PD, IRB PD, CECL loss estimate, LGD, downturn LGD, EAD and CCF. Columns should define outcome, horizon, point-in-time or through-the-cycle intent, scenario treatment, calibration population, discounting, conservatism, owner and downstream use. Any unexplained sharing of a value is an issue.


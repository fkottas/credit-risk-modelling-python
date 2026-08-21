# Chapter 13 — IRB Capital, Portfolio and Counterparty Risk

## Corporate IRB function

The corporate one-factor function links borrower PD to systematic asset correlation, evaluates conditional default under a severe systematic factor, applies LGD, subtracts expected loss and adjusts for maturity [R1–R2]. `corporate_irb_capital` exposes each component for audit.

```python
result = corporate_irb_capital(pd, lgd, ead, maturity_years=maturity)
assert np.allclose(result["risk_weighted_assets"], 12.5 * result["capital"])
```

The calculation is an educational implementation. A regulatory engine must determine exposure class, IRB permission, PD/LGD/CCF floors, maturity, specialised lending, defaulted treatment, supporting factors, output floor, provisions and jurisdictional transition. Never infer these from dataset columns.

## Vasicek intuition

The asymptotic single-risk-factor model represents an obligor's asset return as a systematic factor plus idiosyncratic noise. Conditional on a severe systematic state, default probability rises. With infinitely granular exposures, idiosyncratic risk diversifies and portfolio loss converges to conditional expected loss.

`vasicek_portfolio_loss_quantile` computes the conditional loss rate for a common PD, LGD, correlation and confidence. It is intuition, not a full portfolio model. Real portfolios are heterogeneous and concentrated.

## Concentration and Monte Carlo

Name, sector, geography, product and collateral concentration create deviations from the asymptotic assumption. A credit Monte Carlo simulation samples systematic factors, correlated obligor latent variables, default, exposure and recovery. Aggregate losses produce expected loss, quantiles and expected shortfall.

Validation checks marginals, correlations, convergence, tail stability and sensitivity. Correlations inferred from short default histories are uncertain. Stress scenarios and concentration limits often provide more robust insight than a single precise Credit VaR.

Capital allocation can use marginal or Euler contributions when the risk measure is sufficiently smooth. Allocation supports pricing and limits but should not create false precision. Show sensitivity to correlation and recovery assumptions.

## Counterparty exposure

Counterparty credit risk concerns replacement cost and future market exposure before settlement. Exposure depends on market factors, netting set, collateral, margin period of risk and close-out. Expected exposure is an average profile; potential future exposure is a high quantile. Wrong-way risk occurs when exposure rises as counterparty credit worsens.

Netting is enforceable only with valid legal agreements in relevant jurisdictions. Collateral reduces exposure subject to thresholds, minimum transfer amounts, haircuts, timing and disputes. Operational inability to call or liquidate collateral matters as much as formula.

## CVA, DVA and SA-CCR

CVA is the adjustment for counterparty default risk in derivative value; DVA reflects own credit in accounting valuation under applicable standards. A simple unilateral CVA integrates discounted expected positive exposure, marginal counterparty default and loss given default. Production valuation requires market-consistent curves, netting, collateral, wrong-way risk and accounting scope.

SA-CCR is a prescribed standardised counterparty exposure framework. It combines replacement cost and potential future exposure add-ons across asset classes, with supervisory factors and netting rules. This book provides system boundaries and reconciliations, not a legal implementation. Use current Basel and jurisdictional text, including CRE52, for requirements [R23].

## Shared data, separate models

IRB credit risk and counterparty risk share legal entities, ratings, collateral and limits, but exposure construction differs. Create canonical identifiers and ownership while preserving model-specific snapshots. A derivative netting-set exposure should not be forced into a retail EAD schema.

## Chapter deliverable

Use notebook 06 to compare IFRS 9 ECL, IRB expected loss and IRB capital for the same five synthetic exposures. Change PD and maturity one at a time and explain nonlinear effects. Then simulate a 1,000-obligor portfolio with one systematic factor and compare loss quantiles with the Vasicek approximation.


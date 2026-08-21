# Chapter 14 — Stress Testing and Decision Optimisation

## Scenarios are coherent stories with numbers

A stress scenario specifies macro and financial paths, horizon, severity, narrative and transmission. Variables should be mutually coherent: unemployment, GDP, rates, inflation, house prices and exchange rates cannot be shocked independently without considering their relationship. Use historical, hypothetical, regulatory and reverse scenarios for different purposes.

A satellite model links scenario variables to portfolio risk. It can model default rates, rating transitions, hazard, LGD, CCF, utilisation, prepayment or revenue. Estimate on representative cycles where possible, include lags, and test economic signs. A small historical sample makes tail extrapolation highly uncertain; overlay sensitivity and expert challenge are required.

## IFRS 9 scenario weighting versus stress testing

IFRS 9 probability-weights unbiased scenarios for accounting ECL. Stress testing asks what happens under severe states and may not probability-weight them. Capital planning, risk appetite and reverse stress have still different objectives. Maintain one scenario service with purpose-specific approvals rather than one undifferentiated “downside multiplier.”

Reverse stress begins with failure—capital breach, liquidity pressure, loss limit or business-model unviability—and searches for plausible conditions that cause it. It is useful for exposing nonlinear thresholds and concentration.

## Sensitivity framework

Before a complex scenario, vary one driver at a time. Record elasticity of PD, LGD, EAD, ECL, capital, approval and profit. Then combine coherent shocks. Sensitivity should include model coefficients, calibration, scenario weights, recovery lag, utilisation and correlation. Separate model uncertainty from scenario severity.

## Risk-based pricing

Price should cover expected loss, funding, operations, capital, liquidity, taxes and target return, subject to affordability, competition and law. A stylised risk-adjusted return on capital is

`RAROC = (revenue − expected loss − operating cost) / economic capital`.

Inputs must share horizon and cash-flow timing. A riskier customer may require a higher price mathematically, but higher price can increase adverse selection, affordability stress and default. Pricing is an intervention that changes behaviour.

## Portfolio and limit optimisation

Decision optimisation selects approvals, amounts, prices or limits to maximise expected value subject to constraints. A portfolio problem can include approval volume, expected loss, capital, concentration, fairness, affordability and operational capacity. The objective uses calibrated probabilities and uncertainty buffers.

Do not optimise on point estimates alone. Robust optimisation evaluates adverse parameter sets. Shadow prices reveal which constraint binds. Test policy discontinuities around cut-offs and limits. A small score change should not cause a disproportionate customer outcome without rationale.

## Bandits and reinforcement learning

A contextual bandit chooses a treatment and observes reward, useful when action has limited state effect. Reinforcement learning uses state, action, transition and delayed reward. Credit limits and collections have long delays, censoring, safety constraints and policy selection, making naive online exploration unacceptable.

An RL design needs:

- a state containing only information available at decision time;
- a restricted action set approved by policy;
- reward including profit, loss, customer and compliance costs;
- hard affordability, fairness, concentration and legal constraints;
- an audited behaviour policy and propensity estimates;
- offline policy evaluation with uncertainty;
- simulation and shadow mode before controlled deployment;
- kill switch and human authority.

Q-learning estimates action value recursively. Deep RL replaces the table with a function approximator, increasing extrapolation risk. Off-policy methods can be biased when candidate actions lack support under historical policy. If an action was almost never taken for a group, the data cannot reliably estimate its consequence.

## Safe dynamic limits

A dynamic limit policy may reduce undrawn exposure for deteriorating accounts or increase limits for reliable borrowers. Outcomes include utilisation, revenue, default, complaints, attrition and customer hardship. Historical limit changes were not random. Use causal or experimental design where lawful, and prohibit actions outside explicit bounds.

An agent may prepare evidence for a limit committee. It must not directly alter customer limits. The same boundary applies to RL: a learned policy is a model subject to validation, approval, monitoring and rollback.

## Chapter deliverable

Take the expected-application-value function from `decisioning.py`. Build a constrained grid of PD cut-off and loan amount. Add an expected-loss limit and minimum approval rate. Stress PD by 30% and LGD by 15%. Recommend a robust region, not one optimum. Describe how selection and price response could invalidate it.


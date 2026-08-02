# Chapter 17 — Governed Agentic AI in Credit Risk

## What an agent is

An agent observes context, selects tools or actions, maintains state and pursues a goal over multiple steps. A chatbot answering one question is not necessarily agentic. In credit risk, the meaningful question is not whether an interface is called an agent, but what it can read, infer, write, approve and trigger.

Useful bounded agents can assemble a data-quality report, trace lineage, propose tests, compare model documents, summarise monitoring evidence or draft an incident ticket. High-risk functions include changing targets, selecting customers, modifying policy, retraining, deploying, changing prices or limits and communicating decisions. Those require deterministic controls, appropriate validation and explicit authority.

## Reference architecture

The book's architecture has five layers:

- evidence store with immutable data, metrics, artefacts and source hashes;
- deterministic tools for approved calculations and retrieval;
- policy and permission layer defining allowed reads and proposed writes;
- reasoning layer that plans, calls tools and produces a recommendation;
- human workflow that reviews evidence and authorises material action.

The agent never becomes the system of record. Tools enforce permissions; prompts do not. A statement such as “never deploy” is insufficient if the agent's credentials can deploy.

## Deterministic bounded example

`GovernedMonitoringAgent` receives a typed quality report and monitoring metrics. It applies pre-approved thresholds. Critical data failure returns `HALT`; material PSI or weak mature AUC returns `ESCALATE`; smaller PSI returns `REVIEW`; otherwise it recommends continued monitoring. Every result requires human approval and contains a hash of evidence.

```python
recommendation = GovernedMonitoringAgent().review(
    quality_report,
    {"pd_psi": 0.31, "roc_auc": 0.72},
)
assert recommendation.status == "ESCALATE"
assert recommendation.human_approval_required
```

The prohibited actions are part of the output contract: approve or decline credit, alter price or limit, retrain or deploy without approval, and alter evidence. This component is agent-like triage without an LLM. A language model can draft the narrative, but deterministic rules remain authoritative.

## Evidence provenance

Every agent claim should cite a tool result, source or calculation. Store prompt/template version, model/provider version, tool calls, input hashes, output, decision, reviewer and timestamp. Sensitive prompts and outputs follow data-classification and retention rules.

Retrieval must respect document version and authority. A current policy supersedes a draft. Regulatory text should come from official sources. A secondary guide can explain but not replace the rule. The attached agentic-credit paper is treated only as a conceptual source because its reported experimental evidence lacks enough reproducible dataset and method detail; the book does not reuse its performance claims [R24].

## Threats

Prompt injection can enter through a document, dataset value or web page and instruct the agent to ignore policy or exfiltrate data. Treat retrieved content as data, not instructions. Tool parameters are validated independently. Deny broad file, network, email and deployment access.

Hallucination creates unsupported facts, citations or numbers. Require source-grounded output and fail closed when evidence is missing. Instability means the same evidence can produce different narratives; deterministic calculation and approval thresholds must not depend on sampling.

Data leakage can expose customer, model or commercial information to a provider. Perform privacy, security, residency and contractual assessment. Minimise fields, redact where possible and separate customer-level workflows from general knowledge tasks.

Automation bias occurs when reviewers accept polished recommendations. The interface should show evidence, uncertainty, conflicts and alternative action—not only a confident summary. Track reviewer disagreement and overturned recommendations.

## Segregation of duties

Separate agents by role and credentials. A documentation agent can read approved artefacts and write a draft. A monitoring agent can open a ticket. A validation agent can run challenge tests in a sandbox. None can approve its own output. A deployment service accepts only a signed approval produced by the governed human workflow.

Multi-agent designs increase interaction risk. Agents can amplify each other's unsupported assumptions. Use a small number of bounded roles, typed messages, shared evidence identifiers and maximum iteration. Do not create agents merely to imitate an organisation chart.

## Evaluation

An agent test set includes normal, edge, adversarial and absent-evidence cases. Measure factual grounding, citation correctness, calculation agreement, policy compliance, sensitive-data handling, tool selection, refusal, latency and cost. Test prompt injection, poisoned documents, conflicting policies, stale versions and unavailable tools.

For action recommendations, evaluate false reassurance and unnecessary escalation separately. A safe agent should halt when critical evidence is unavailable. Red-team attempts to cross customer-decision, deployment and data boundaries. Verify the kill switch technically.

NIST AI RMF organises risk-management outcomes under Govern, Map, Measure and Manage, and its generative-AI profile adds risks and actions relevant to foundation-model systems [R8]. Use it as a cross-sectoral framework alongside applicable financial, privacy, consumer and AI requirements.

## EU high-risk context

The EU AI Act's official text identifies creditworthiness and credit-score uses for natural persons as high-risk in scope, with specified distinctions including fraud and prudential uses [R7]. An agent that merely drafts model documentation differs from one that influences an individual decision. Classify the whole intended system, including tools and downstream action, not only the language model.

## Chapter deliverable

Run notebook 07 and add three adversarial tests: a metric field containing an instruction, missing AUC and conflicting PSI values from two sources. Define which source is authoritative and make the agent halt on unresolved conflict. Produce a permission matrix of read, propose, write, approve and execute for data, model, validation, monitoring and deployment roles.


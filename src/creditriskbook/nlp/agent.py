"""Offline reference assistant for credit-document evidence workflows."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from creditriskbook.agents import ActionProposal, EvidenceItem, PolicyDecision, PolicyEngine

from .documents import (
    DocumentChunk,
    chunk_document,
    detect_instruction_like_text,
    extract_tagged_facts,
)
from .retrieval import bm25_retrieve
from .structured import UnderwritingEvidenceMemo, validate_memo


@dataclass(frozen=True)
class DocumentAgentResult:
    memo: UnderwritingEvidenceMemo
    proposal: ActionProposal
    policy_decision: PolicyDecision
    trace: tuple[str, ...]


class DocumentUnderwritingAssistant:
    """Extract and recommend; never approve, decline, price, or change a limit."""

    name = "document_underwriting_assistant"

    def __init__(self, policy_engine: PolicyEngine | None = None) -> None:
        self.policy_engine = policy_engine or PolicyEngine()

    def run(
        self,
        application: pd.Series,
        documents: pd.DataFrame,
        policy_documents: pd.DataFrame,
    ) -> DocumentAgentResult:
        application_id = str(application["application_id"])
        packet = documents.loc[documents["application_id"].eq(application_id)].copy()
        trace = ["packet_selected"]
        facts = []
        safety_flags: list[str] = []
        for row in packet.itertuples(index=False):
            facts.extend(extract_tagged_facts(row.document_id, row.text))
            if detect_instruction_like_text(row.text):
                safety_flags.append(f"untrusted_instruction_text:{row.document_id}")
        trace.append("facts_extracted")
        fact_map = {fact.field: fact for fact in facts}
        document_types = set(packet["document_type"])
        required = {"application_form", "payslip", "bank_statement_summary"}
        missing = tuple(sorted(required - document_types))

        inconsistencies: list[str] = []
        declared = fact_map.get("declared_monthly_income_eur")
        verified = fact_map.get("verified_monthly_income_eur")
        if declared and verified:
            relative_gap = abs(float(declared.value) - float(verified.value)) / max(
                float(declared.value), 1.0
            )
            if relative_gap > 0.20:
                inconsistencies.append(f"income_gap_above_20pct:{relative_gap:.3f}")
        trace.append("facts_reconciled")

        policy_chunks: list[DocumentChunk] = []
        for row in policy_documents.itertuples(index=False):
            policy_chunks.extend(
                chunk_document(row.document_id, row.text, chunk_words=55, overlap_words=8)
            )
        retrieved = bm25_retrieve(
            "human approval missing evidence prohibited customer decision",
            tuple(policy_chunks),
            top_k=2,
        )
        policy_ids = tuple(item.document_id for item in retrieved)
        trace.append("approved_policy_retrieved")

        evidence_ids = tuple(sorted({fact.evidence_id for fact in facts}))
        verified_facts = tuple(
            f"{fact.field}={fact.value}"
            for fact in facts
            if fact.field not in {"application_id", "customer_id"}
        )
        recommendation = "request_missing_evidence" if missing else "refer_for_human_review"
        memo = UnderwritingEvidenceMemo(
            application_id=application_id,
            verified_facts=verified_facts,
            missing_evidence=missing,
            inconsistencies=tuple(inconsistencies),
            safety_flags=tuple(safety_flags),
            policy_citations=policy_ids,
            evidence_ids=evidence_ids,
            recommendation=recommendation,
            uncertainty=(
                "Synthetic deterministic extraction; no inference beyond tagged evidence. "
                "A qualified reviewer must inspect original documents and policy."
            ),
        )
        validate_memo(
            memo,
            available_evidence_ids=set(evidence_ids),
            available_policy_ids=set(policy_documents["document_id"]),
        )
        trace.append("structured_output_validated")
        evidence = EvidenceItem.from_payload(
            f"synthetic-document-packet/{application_id}",
            {
                "evidence_ids": evidence_ids,
                "missing": missing,
                "inconsistencies": inconsistencies,
                "safety_flags": safety_flags,
            },
        )
        proposal = ActionProposal(
            action="request_human_validation",
            rationale=f"Document evidence review for {application_id}: {recommendation}.",
            evidence_ids=(evidence.evidence_id,),
            requested_by=self.name,
            parameters={"application_id": application_id, "memo_recommendation": recommendation},
        )
        decision = self.policy_engine.evaluate(proposal)
        trace.append("permission_policy_evaluated")
        return DocumentAgentResult(memo, proposal, decision, tuple(trace))

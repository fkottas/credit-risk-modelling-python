from __future__ import annotations

import unittest

from creditriskbook.data import make_synthetic_credit_document_case
from creditriskbook.nlp import (
    DocumentUnderwritingAssistant,
    UnderwritingEvidenceMemo,
    bm25_retrieve,
    chunk_document,
    detect_instruction_like_text,
    extract_tagged_facts,
    validate_memo,
)


class SyntheticDocumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.case = make_synthetic_credit_document_case(n_applications=16, seed=7801)

    def test_generator_is_reproducible_and_contains_no_real_records(self) -> None:
        second = make_synthetic_credit_document_case(n_applications=16, seed=7801)
        self.assertEqual(self.case.source_sha256, second.source_sha256)
        self.assertEqual(len(self.case.source_sha256), 64)
        self.assertTrue(self.case.documents["synthetic"].all())
        self.assertEqual(self.case.applications["application_id"].nunique(), 16)
        self.assertTrue(
            self.case.documents["application_id"]
            .isin(self.case.applications["application_id"])
            .all()
        )

    def test_extraction_keeps_source_evidence(self) -> None:
        document = self.case.documents.iloc[0]
        facts = extract_tagged_facts(document["document_id"], document["text"])
        fields = {fact.field for fact in facts}
        self.assertIn("application_id", fields)
        self.assertIn("requested_amount_eur", fields)
        self.assertTrue(all(fact.evidence_id.startswith("doc-ev-") for fact in facts))
        self.assertTrue(all(fact.source_text for fact in facts))

    def test_prompt_injection_text_is_flagged_not_executed(self) -> None:
        adversarial = self.case.documents.loc[
            self.case.documents["text"].str.contains("Ignore previous", case=False)
        ].iloc[0]
        self.assertTrue(detect_instruction_like_text(adversarial["text"]))

    def test_bm25_returns_cited_policy_chunks(self) -> None:
        chunks = tuple(
            chunk
            for row in self.case.policy_documents.itertuples(index=False)
            for chunk in chunk_document(row.document_id, row.text, chunk_words=45, overlap_words=5)
        )
        result = bm25_retrieve("human approval missing evidence", chunks, top_k=2)
        self.assertGreaterEqual(len(result), 1)
        self.assertTrue(all(item.score > 0 for item in result))
        self.assertTrue(
            {item.document_id for item in result}.issubset(
                set(self.case.policy_documents["document_id"])
            )
        )


class DocumentAssistantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = make_synthetic_credit_document_case(n_applications=16, seed=7801)
        self.assistant = DocumentUnderwritingAssistant()

    def _run(self, index: int):
        return self.assistant.run(
            self.case.applications.iloc[index], self.case.documents, self.case.policy_documents
        )

    def test_missing_payslip_requests_evidence_and_human_review(self) -> None:
        result = self._run(0)
        self.assertEqual(result.memo.recommendation, "request_missing_evidence")
        self.assertIn("payslip", result.memo.missing_evidence)
        self.assertEqual(result.proposal.action, "request_human_validation")
        self.assertEqual(result.policy_decision.decision, "PENDING_HUMAN_APPROVAL")
        self.assertNotIn("approve", result.memo.recommendation)

    def test_adversarial_document_cannot_change_authority(self) -> None:
        result = self._run(1)
        self.assertTrue(result.memo.safety_flags)
        self.assertEqual(result.proposal.action, "request_human_validation")
        self.assertEqual(result.policy_decision.decision, "PENDING_HUMAN_APPROVAL")
        self.assertEqual(result.trace[-1], "permission_policy_evaluated")

    def test_unsupported_or_decision_output_fails_closed(self) -> None:
        invalid = UnderwritingEvidenceMemo(
            application_id="DOCAPP-00001",
            verified_facts=(),
            missing_evidence=(),
            inconsistencies=(),
            safety_flags=(),
            policy_citations=("POLICY-NOT-AVAILABLE",),
            evidence_ids=("ev-unknown",),
            recommendation="approve",
            uncertainty="none",
        )
        with self.assertRaises(ValueError):
            validate_memo(
                invalid,
                available_evidence_ids={"ev-known"},
                available_policy_ids={"POLICY-AUTHORITY-001"},
            )


if __name__ == "__main__":
    unittest.main()

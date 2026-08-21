"""Run the offline, evidence-bound credit-document assistant."""

from __future__ import annotations

from dataclasses import asdict

from creditriskbook.data import make_synthetic_credit_document_case
from creditriskbook.nlp import DocumentUnderwritingAssistant


def main() -> None:
    case = make_synthetic_credit_document_case(n_applications=16, seed=7801)
    assistant = DocumentUnderwritingAssistant()
    for index in (0, 1, 6):
        result = assistant.run(case.applications.iloc[index], case.documents, case.policy_documents)
        print(
            {
                "application_id": result.memo.application_id,
                "recommendation": result.memo.recommendation,
                "missing": result.memo.missing_evidence,
                "safety_flags": result.memo.safety_flags,
                "policy_decision": result.policy_decision.decision,
                "trace": result.trace,
            }
        )
    print("Synthetic source SHA-256:", case.source_sha256)
    print("Example memo fields:", sorted(asdict(result.memo)))


if __name__ == "__main__":
    main()

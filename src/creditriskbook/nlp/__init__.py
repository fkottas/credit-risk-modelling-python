"""NLP, retrieval, structured-output, and document-agent teaching components."""

from .agent import DocumentAgentResult, DocumentUnderwritingAssistant
from .documents import (
    DocumentChunk,
    ExtractedFact,
    chunk_document,
    detect_instruction_like_text,
    extract_tagged_facts,
    normalize_document_text,
)
from .retrieval import RetrievedChunk, bm25_retrieve, tokenize
from .structured import (
    StructuredTextModel,
    UnderwritingEvidenceMemo,
    validate_memo,
)

__all__ = [
    "DocumentAgentResult",
    "DocumentChunk",
    "DocumentUnderwritingAssistant",
    "ExtractedFact",
    "RetrievedChunk",
    "StructuredTextModel",
    "UnderwritingEvidenceMemo",
    "bm25_retrieve",
    "chunk_document",
    "detect_instruction_like_text",
    "extract_tagged_facts",
    "normalize_document_text",
    "tokenize",
    "validate_memo",
]

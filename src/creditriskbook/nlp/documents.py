"""Transparent document normalisation, chunking, extraction, and safety checks."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    document_id: str
    start_word: int
    end_word: int
    text: str


@dataclass(frozen=True)
class ExtractedFact:
    field: str
    value: Any
    document_id: str
    evidence_id: str
    source_text: str


FIELD_TYPES: dict[str, type] = {
    "APPLICATION_ID": str,
    "CUSTOMER_ID": str,
    "REQUESTED_AMOUNT_EUR": float,
    "DECLARED_MONTHLY_INCOME_EUR": float,
    "VERIFIED_MONTHLY_INCOME_EUR": float,
    "AVERAGE_MONTHLY_CREDITS_EUR": float,
    "AVERAGE_MONTHLY_DEBITS_EUR": float,
    "MAX_DPD_REPORTED": int,
    "DECLARED_EMPLOYER_CODE": str,
    "EMPLOYER_CODE": str,
}

INSTRUCTION_PATTERNS = (
    re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"approve\s+(?:the\s+)?loan", re.IGNORECASE),
    re.compile(r"reveal\s+(?:the\s+)?system\s+prompt", re.IGNORECASE),
    re.compile(r"change\s+(?:the\s+)?credit\s+(?:decision|limit|price)", re.IGNORECASE),
)


def normalize_document_text(text: str) -> str:
    """Normalise line endings and spaces without changing semantic content."""
    if not isinstance(text, str):
        raise TypeError("Document text must be a string")
    lines = [
        re.sub(r"[ \t]+", " ", line).strip() for line in text.replace("\r\n", "\n").split("\n")
    ]
    return "\n".join(line for line in lines if line)


def chunk_document(
    document_id: str,
    text: str,
    *,
    chunk_words: int = 80,
    overlap_words: int = 15,
) -> tuple[DocumentChunk, ...]:
    """Create deterministic word windows with explicit offsets and overlap."""
    if chunk_words <= 0 or overlap_words < 0 or overlap_words >= chunk_words:
        raise ValueError("Require chunk_words > overlap_words >= 0")
    words = normalize_document_text(text).split()
    if not words:
        return ()
    chunks: list[DocumentChunk] = []
    step = chunk_words - overlap_words
    for start in range(0, len(words), step):
        end = min(start + chunk_words, len(words))
        chunk_text = " ".join(words[start:end])
        digest = hashlib.sha256(f"{document_id}|{start}|{end}|{chunk_text}".encode()).hexdigest()[
            :16
        ]
        chunks.append(DocumentChunk(f"chunk-{digest}", document_id, start, end, chunk_text))
        if end == len(words):
            break
    return tuple(chunks)


def extract_tagged_facts(document_id: str, text: str) -> tuple[ExtractedFact, ...]:
    """Extract the synthetic KEY: VALUE contract with source evidence for every fact."""
    facts: list[ExtractedFact] = []
    for line in normalize_document_text(text).splitlines():
        if ":" not in line:
            continue
        key, raw = (part.strip() for part in line.split(":", 1))
        converter = FIELD_TYPES.get(key)
        if converter is None:
            continue
        try:
            value = converter(raw)
        except ValueError as exc:
            raise ValueError(f"Invalid {key} in {document_id}: {raw!r}") from exc
        evidence_digest = hashlib.sha256(f"{document_id}|{line}".encode()).hexdigest()[:16]
        facts.append(
            ExtractedFact(
                field=key.lower(),
                value=value,
                document_id=document_id,
                evidence_id=f"doc-ev-{evidence_digest}",
                source_text=line,
            )
        )
    return tuple(facts)


def detect_instruction_like_text(text: str) -> tuple[str, ...]:
    """Flag untrusted instructions embedded in evidence; never execute them."""
    normalized = normalize_document_text(text)
    return tuple(pattern.pattern for pattern in INSTRUCTION_PATTERNS if pattern.search(normalized))

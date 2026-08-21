"""Small BM25-style retriever whose mathematics is visible to students."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from .documents import DocumentChunk

TOKEN = re.compile(r"[a-z0-9_]+")


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    document_id: str
    score: float
    text: str


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(TOKEN.findall(text.lower()))


def bm25_retrieve(
    query: str,
    chunks: tuple[DocumentChunk, ...],
    *,
    top_k: int = 3,
    k1: float = 1.5,
    b: float = 0.75,
) -> tuple[RetrievedChunk, ...]:
    """Rank chunks with the standard BM25 term-frequency saturation form."""
    if top_k <= 0 or k1 <= 0 or not 0 <= b <= 1:
        raise ValueError("Require top_k > 0, k1 > 0, and b in [0, 1]")
    if not chunks:
        return ()
    query_terms = set(tokenize(query))
    documents = [tokenize(chunk.text) for chunk in chunks]
    average_length = sum(map(len, documents)) / len(documents)
    document_frequency = Counter(
        term for terms in documents for term in set(terms) if term in query_terms
    )
    scored: list[RetrievedChunk] = []
    n_documents = len(documents)
    for chunk, terms in zip(chunks, documents, strict=True):
        counts = Counter(terms)
        score = 0.0
        for term in query_terms:
            if not counts[term]:
                continue
            df = document_frequency[term]
            idf = math.log(1.0 + (n_documents - df + 0.5) / (df + 0.5))
            normalizer = counts[term] + k1 * (1 - b + b * len(terms) / average_length)
            score += idf * counts[term] * (k1 + 1) / normalizer
        scored.append(RetrievedChunk(chunk.chunk_id, chunk.document_id, score, chunk.text))
    ranked = sorted(scored, key=lambda item: (-item.score, item.document_id, item.chunk_id))
    return tuple(item for item in ranked[:top_k] if item.score > 0)

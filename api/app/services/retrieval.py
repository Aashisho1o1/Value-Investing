from __future__ import annotations

import math
import re
from collections import Counter

from app.models import EvidenceChunk


THEME_QUERIES = {
    "summary": {
        "sections": {"Business", "MD&A"},
        "keywords": {"business", "customer", "product", "market", "strategy", "segment"},
    },
    "business_quality": {
        "sections": {"Business", "MD&A"},
        "keywords": {"competitive", "advantage", "brand", "recurring", "customer", "demand"},
    },
    "financial_strength": {
        "sections": {"MD&A", "Financial Statements"},
        "keywords": {"cash", "liquidity", "margin", "profitability", "operations", "debt"},
    },
    "risk_review": {
        "sections": {"Risk Factors", "MD&A"},
        "keywords": {"risk", "volatility", "customer", "regulatory", "supply", "litigation"},
    },
    "capital_allocation": {
        "sections": {"MD&A", "Financial Statements"},
        "keywords": {"capital", "investment", "acquisition", "repurchase", "dividend", "share"},
    },
    "valuation_context": {
        "sections": {"MD&A", "Financial Statements"},
        "keywords": {"cash", "earnings", "margin", "capital", "investment", "cyclical"},
    },
    "open_questions": {
        "sections": {"Risk Factors", "Business", "MD&A"},
        "keywords": {"uncertain", "depend", "competition", "macro", "demand", "unknown"},
    },
}


def _tokenize(value: str) -> list[str]:
    return re.findall(r"[a-z]{3,}", value.lower())


def _idf_weights(chunks: list[EvidenceChunk]) -> dict[str, float]:
    doc_count = len(chunks) or 1
    frequencies = Counter()
    for chunk in chunks:
        frequencies.update(set(_tokenize(chunk.snippet)))
    return {
        token: math.log((doc_count + 1) / (count + 1)) + 1
        for token, count in frequencies.items()
    }


def score_chunk(chunk: EvidenceChunk, theme: str, idf_weights: dict[str, float]) -> float:
    config = THEME_QUERIES[theme]
    keywords = config["keywords"]
    chunk_tokens = set(_tokenize(chunk.snippet))
    overlap_score = sum(idf_weights.get(token, 1.0) for token in chunk_tokens & keywords)
    section_bonus = 3.5 if chunk.section in config["sections"] else 0.5
    density_bonus = min(len(chunk_tokens & keywords), 4) * 0.4
    return overlap_score + section_bonus + density_bonus


def retrieve_theme_chunks(
    chunks: list[EvidenceChunk],
    per_theme_limit: int = 4,
) -> tuple[dict[str, list[EvidenceChunk]], list[EvidenceChunk]]:
    idf_weights = _idf_weights(chunks)
    themed: dict[str, list[EvidenceChunk]] = {}
    aggregate_scores: dict[str, float] = {}
    chunk_lookup = {chunk.chunk_id: chunk for chunk in chunks}

    for theme in THEME_QUERIES:
        ranked = sorted(
            (
                chunk.model_copy(update={"rank": score_chunk(chunk, theme, idf_weights)})
                for chunk in chunks
            ),
            key=lambda chunk: chunk.rank,
            reverse=True,
        )
        themed[theme] = [chunk for chunk in ranked[:per_theme_limit] if chunk.rank > 0]
        for chunk in themed[theme]:
            aggregate_scores[chunk.chunk_id] = max(aggregate_scores.get(chunk.chunk_id, 0), chunk.rank)

    evidence_chunks = [
        chunk_lookup[chunk_id].model_copy(update={"rank": rank})
        for chunk_id, rank in sorted(aggregate_scores.items(), key=lambda item: item[1], reverse=True)
    ]
    return themed, evidence_chunks[:18]


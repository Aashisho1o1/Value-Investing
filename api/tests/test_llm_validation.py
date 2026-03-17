import pytest

from app.services.filing_parser import parse_filing_html
from app.services.llm import LLMValidationError, validate_model_payload
from app.services.metrics import extract_metric_series
from app.services.retrieval import retrieve_theme_chunks


def _valid_payload(themed):
    return {
        "sections": {
            key: [
                {
                    "text": f"Evidence-backed view for {key.replace('_', ' ')} remains conservative.",
                    "citation_chunk_ids": [themed[key][0].chunk_id],
                }
            ]
            for key in themed
        },
        "scorecard": [
            {
                "key": "business_quality",
                "score": 4,
                "rationale": "The business appears understandable from the filing.",
                "citation_chunk_ids": [themed["business_quality"][0].chunk_id],
            },
            {
                "key": "financial_strength",
                "score": 4,
                "rationale": "Liquidity and earnings are discussed in the filing.",
                "citation_chunk_ids": [themed["financial_strength"][0].chunk_id],
            },
            {
                "key": "balance_sheet",
                "score": 3,
                "rationale": "The filing shows a mixed leverage profile.",
                "citation_chunk_ids": [themed["financial_strength"][0].chunk_id],
            },
            {
                "key": "capital_allocation",
                "score": 3,
                "rationale": "Management highlights reinvestment and capital returns.",
                "citation_chunk_ids": [themed["capital_allocation"][0].chunk_id],
            },
            {
                "key": "risk_burden",
                "score": 2,
                "rationale": "The filing emphasizes operating and market risks.",
                "citation_chunk_ids": [themed["risk_review"][0].chunk_id],
            },
        ],
    }


def test_validate_model_payload_accepts_cited_sections(load_fixture):
    html = load_fixture("filing_aapl.html")
    _, chunks = parse_filing_html(html, "https://example.com/aapl")
    themed, evidence = retrieve_theme_chunks(chunks)
    metrics = extract_metric_series(load_fixture("companyfacts_aapl.json"))
    payload = _valid_payload(themed)

    memo_sections, scorecard, citations = validate_model_payload(
        payload=payload,
        evidence_lookup={chunk.chunk_id: chunk for chunk in evidence},
        metrics=metrics,
        filing_date="2024-11-01",
    )

    assert memo_sections["summary"].paragraphs
    assert len(scorecard) == 5
    assert citations


def test_validate_model_payload_rejects_uncited_text(load_fixture):
    html = load_fixture("filing_aapl.html")
    _, chunks = parse_filing_html(html, "https://example.com/aapl")
    themed, evidence = retrieve_theme_chunks(chunks)
    metrics = extract_metric_series(load_fixture("companyfacts_aapl.json"))
    payload = _valid_payload(themed)
    payload["sections"]["summary"][0]["citation_chunk_ids"] = []

    with pytest.raises(LLMValidationError):
        validate_model_payload(
            payload=payload,
            evidence_lookup={chunk.chunk_id: chunk for chunk in evidence},
            metrics=metrics,
            filing_date="2024-11-01",
        )


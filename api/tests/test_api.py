from fastapi.testclient import TestClient

import app.main as main
from app.models import AnalyzeResponse
from app.services.llm import empty_memo_sections


class StubAnalyzer:
    def analyze(self, ticker: str, force_refresh: bool = False):
        return AnalyzeResponse.model_validate(
            {
                "company": {
                    "name": "Apple Inc.",
                    "ticker": ticker.upper(),
                    "cik": "0000320193",
                    "exchange": None,
                    "sic": None,
                    "sic_description": None,
                    "fiscal_year_end": "0928",
                },
                "filing": {
                    "accession_number": "0000320193-24-000123",
                    "filing_date": "2024-11-01",
                    "filing_index_url": "https://example.com/index.html",
                    "filing_html_url": "https://example.com/filing.html",
                    "form": "10-K",
                },
                "metrics": [],
                "charts": [],
                "scorecard": [],
                "memo_sections": {key: section.model_dump() for key, section in empty_memo_sections().items()},
                "citations": {},
                "evidence_chunks": [],
                "warnings": [],
                "memo_status": "unavailable",
            }
        )


def test_analyze_endpoint_returns_payload(monkeypatch):
    monkeypatch.setattr(main, "analyzer", StubAnalyzer())
    client = TestClient(main.app)

    response = client.post("/v1/analyze", json={"ticker": "aapl"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["company"]["ticker"] == "AAPL"
    assert payload["memo_status"] == "unavailable"


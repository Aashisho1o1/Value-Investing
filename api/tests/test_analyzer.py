from app.services.analyzer import Analyzer
from app.services.cache import FileCache
from app.services.sec_client import select_latest_10k


class FixtureSECClient:
    def __init__(self, submissions, companyfacts, filing_html):
        self.submissions = submissions
        self.companyfacts = companyfacts
        self.filing_html = filing_html

    def get_latest_filing_bundle(self, ticker: str):
        return select_latest_10k(self.submissions, ticker, "0000320193")

    def get_companyfacts(self, cik: str):
        return self.companyfacts

    def get_filing_html(self, filing):
        return self.filing_html


class StubLLMClient:
    def generate_report(self, company, filing, metrics_summary, warnings, themed_chunks):
        return {
            "sections": {
                key: [
                    {
                        "text": f"{company['name']} has a conservative first-pass view for {key.replace('_', ' ')}.",
                        "citation_chunk_ids": [themed_chunks[key][0].chunk_id],
                    }
                ]
                for key in themed_chunks
            },
            "scorecard": [
                {
                    "key": "business_quality",
                    "score": 4,
                    "rationale": "The filing provides a readable business description.",
                    "citation_chunk_ids": [themed_chunks["business_quality"][0].chunk_id],
                },
                {
                    "key": "financial_strength",
                    "score": 4,
                    "rationale": "Cash generation and profitability appear solid in the filing.",
                    "citation_chunk_ids": [themed_chunks["financial_strength"][0].chunk_id],
                },
                {
                    "key": "balance_sheet",
                    "score": 3,
                    "rationale": "Liquidity and debt suggest a mixed balance sheet picture.",
                    "citation_chunk_ids": [themed_chunks["financial_strength"][0].chunk_id],
                },
                {
                    "key": "capital_allocation",
                    "score": 3,
                    "rationale": "Management describes reinvestment and shareholder returns.",
                    "citation_chunk_ids": [themed_chunks["capital_allocation"][0].chunk_id],
                },
                {
                    "key": "risk_burden",
                    "score": 2,
                    "rationale": "Risk disclosures remain meaningful.",
                    "citation_chunk_ids": [themed_chunks["risk_review"][0].chunk_id],
                },
            ],
        }


class NullLLMClient:
    def generate_report(self, company, filing, metrics_summary, warnings, themed_chunks):
        return None


def test_analyzer_runs_end_to_end_for_multiple_fixtures(load_fixture, tmp_path):
    cases = [
        ("AAPL", "companyfacts_aapl.json"),
        ("COST", "companyfacts_cost.json"),
        ("DAL", "companyfacts_dal.json"),
    ]
    submissions = load_fixture("submissions_aapl.json")
    filing_html = load_fixture("filing_aapl.html")

    for ticker, fixture_name in cases:
        analyzer = Analyzer(
            sec_client=FixtureSECClient(submissions, load_fixture(fixture_name), filing_html),
            llm_client=StubLLMClient(),
            cache=FileCache(tmp_path / ticker.lower()),
        )
        response = analyzer.analyze(ticker)

        assert response.company.ticker == ticker
        assert response.charts
        assert response.memo_status == "available"
        assert response.citations


def test_analyzer_falls_back_when_llm_is_unavailable(load_fixture, tmp_path):
    analyzer = Analyzer(
        sec_client=FixtureSECClient(
            load_fixture("submissions_aapl.json"),
            load_fixture("companyfacts_aapl.json"),
            load_fixture("filing_aapl.html"),
        ),
        llm_client=NullLLMClient(),
        cache=FileCache(tmp_path / "no-llm"),
    )

    response = analyzer.analyze("AAPL")

    assert response.memo_status == "unavailable"
    assert response.scorecard == []
    assert any("memo is unavailable" in warning.lower() for warning in response.warnings)

from app.services.filing_parser import parse_filing_html
from app.services.retrieval import retrieve_theme_chunks


def test_retrieve_theme_chunks_ranks_relevant_sections(load_fixture):
    html = load_fixture("filing_aapl.html")
    _, chunks = parse_filing_html(html, "https://example.com/aapl")
    themed, evidence = retrieve_theme_chunks(chunks)

    assert themed["risk_review"][0].section == "Risk Factors"
    assert themed["capital_allocation"][0].section in {"MD&A", "Financial Statements"}
    assert evidence[0].rank >= evidence[-1].rank


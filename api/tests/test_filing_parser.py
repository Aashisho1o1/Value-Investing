from app.services.filing_parser import parse_filing_html


def test_parse_filing_html_extracts_sections_and_chunks(load_fixture):
    html = load_fixture("filing_aapl.html")
    sections, chunks = parse_filing_html(html, "https://example.com/aapl")

    assert set(sections) == {"Business", "Risk Factors", "MD&A", "Financial Statements"}
    assert any(chunk.section == "MD&A" for chunk in chunks)
    assert chunks[0].chunk_id.startswith("business-")
    assert all(len(chunk.snippet) >= 80 for chunk in chunks)


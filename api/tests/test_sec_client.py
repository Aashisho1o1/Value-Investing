from app.services.sec_client import select_latest_10k


def test_select_latest_10k(load_fixture):
    submissions = load_fixture("submissions_aapl.json")
    bundle = select_latest_10k(submissions, "AAPL", "0000320193")

    assert bundle.company.name == "Apple Inc."
    assert bundle.company.cik == "0000320193"
    assert bundle.filing.form == "10-K"
    assert bundle.filing.filing_date == "2024-11-01"
    assert bundle.filing.filing_html_url.endswith("/a10-k20240928.htm")


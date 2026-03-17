from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.models import CompanyInfo, FilingInfo
from app.services.cache import FileCache


SEC_DATA_BASE = "https://data.sec.gov"
SEC_WWW_BASE = "https://www.sec.gov"


@dataclass
class FilingBundle:
    company: CompanyInfo
    filing: FilingInfo
    primary_document: str


def _zero_pad_cik(value: str | int) -> str:
    return str(value).zfill(10)


def _strip_accession(accession_number: str) -> str:
    return accession_number.replace("-", "")


def select_latest_10k(submissions: dict[str, Any], ticker: str, cik: str) -> FilingBundle:
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accession_numbers = recent.get("accessionNumber", [])
    filing_dates = recent.get("filingDate", [])
    primary_documents = recent.get("primaryDocument", [])

    for index, form in enumerate(forms):
        if form != "10-K":
            continue

        accession_number = accession_numbers[index]
        accession_compact = _strip_accession(accession_number)
        primary_document = primary_documents[index]
        filing_date = filing_dates[index]
        filing_index_url = (
            f"{SEC_WWW_BASE}/Archives/edgar/data/{int(cik)}/{accession_compact}/index.html"
        )
        filing_html_url = (
            f"{SEC_WWW_BASE}/Archives/edgar/data/{int(cik)}/{accession_compact}/{primary_document}"
        )

        company = CompanyInfo(
            name=submissions.get("name") or ticker,
            ticker=ticker,
            cik=_zero_pad_cik(cik),
            exchange=None,
            sic=submissions.get("sic"),
            sic_description=submissions.get("sicDescription"),
            fiscal_year_end=submissions.get("fiscalYearEnd"),
        )
        filing = FilingInfo(
            accession_number=accession_number,
            filing_date=filing_date,
            filing_index_url=filing_index_url,
            filing_html_url=filing_html_url,
            form=form,
        )
        return FilingBundle(company=company, filing=filing, primary_document=primary_document)

    raise ValueError(f"No 10-K filing found for {ticker}")


class SECClient:
    def __init__(self, user_agent: str, cache: FileCache) -> None:
        self.cache = cache
        self.client = httpx.Client(
            headers={
                "User-Agent": user_agent,
                "Accept-Encoding": "gzip, deflate",
                "Host": "data.sec.gov",
            },
            timeout=30.0,
            follow_redirects=True,
        )

    def _get_json(self, cache_key: str, url: str, ttl_seconds: int | None = None) -> dict[str, Any]:
        cached = self.cache.load_json(cache_key, ttl_seconds=ttl_seconds)
        if cached is not None:
            return cached

        response = self.client.get(url)
        response.raise_for_status()
        payload = response.json()
        self.cache.save_json(cache_key, payload)
        return payload

    def _get_text(self, cache_key: str, url: str, ttl_seconds: int | None = None) -> str:
        cached = self.cache.load_text(cache_key, ttl_seconds=ttl_seconds)
        if cached is not None:
            return cached

        response = self.client.get(
            url,
            headers={
                "User-Agent": self.client.headers["User-Agent"],
                "Accept": "text/html,application/xhtml+xml",
                "Host": "www.sec.gov",
            },
        )
        response.raise_for_status()
        payload = response.text
        self.cache.save_text(cache_key, payload)
        return payload

    def resolve_ticker(self, ticker: str) -> dict[str, Any]:
        payload = self._get_json(
            "company_tickers",
            f"{SEC_WWW_BASE}/files/company_tickers.json",
            ttl_seconds=60 * 60 * 24,
        )
        normalized = ticker.upper()
        for company in payload.values():
            if company["ticker"].upper() == normalized:
                return company
        raise ValueError(f"Ticker '{ticker}' was not found in the SEC company list")

    def get_latest_filing_bundle(self, ticker: str) -> FilingBundle:
        company = self.resolve_ticker(ticker)
        cik = _zero_pad_cik(company["cik_str"])
        submissions = self._get_json(
            f"submissions_{cik}",
            f"{SEC_DATA_BASE}/submissions/CIK{cik}.json",
            ttl_seconds=60 * 60 * 12,
        )
        return select_latest_10k(submissions, ticker.upper(), cik)

    def get_companyfacts(self, cik: str) -> dict[str, Any]:
        return self._get_json(
            f"companyfacts_{cik}",
            f"{SEC_DATA_BASE}/api/xbrl/companyfacts/CIK{cik}.json",
            ttl_seconds=60 * 60 * 12,
        )

    def get_filing_html(self, filing: FilingInfo) -> str:
        accession_compact = _strip_accession(filing.accession_number)
        return self._get_text(
            f"filing_html_{filing.form}_{accession_compact}",
            filing.filing_html_url,
        )


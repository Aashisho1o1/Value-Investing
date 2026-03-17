from __future__ import annotations

from typing import Any

from app.models import AnalyzeResponse
from app.services.cache import FileCache
from app.services.filing_parser import parse_filing_html
from app.services.llm import DeepSeekClient, LLMValidationError, empty_memo_sections, validate_model_payload
from app.services.metrics import build_chart_definitions, extract_metric_series, summarize_metrics_for_prompt
from app.services.retrieval import retrieve_theme_chunks
from app.services.sec_client import SECClient


class Analyzer:
    def __init__(self, sec_client: SECClient, llm_client: DeepSeekClient, cache: FileCache) -> None:
        self.sec_client = sec_client
        self.llm_client = llm_client
        self.cache = cache

    def analyze(self, ticker: str, force_refresh: bool = False) -> AnalyzeResponse:
        bundle = self.sec_client.get_latest_filing_bundle(ticker)
        analysis_cache_key = (
            f"analysis_{bundle.company.ticker}_{bundle.filing.accession_number.replace('-', '')}"
        )
        if not force_refresh:
            cached = self.cache.load_json(analysis_cache_key)
            if cached is not None:
                return AnalyzeResponse.model_validate(cached)

        companyfacts = self.sec_client.get_companyfacts(bundle.company.cik)
        html = self.sec_client.get_filing_html(bundle.filing)
        metrics = extract_metric_series(companyfacts)
        charts, chart_warnings = build_chart_definitions(metrics)
        _, chunks = parse_filing_html(html, bundle.filing.filing_html_url)
        themed_chunks, evidence_chunks = retrieve_theme_chunks(chunks)

        warnings = list(chart_warnings)
        if not chunks:
            warnings.append("The filing text could not be segmented into major sections.")

        memo_sections = empty_memo_sections()
        citations = {}
        scorecard = []
        memo_status = "unavailable"

        try:
            llm_payload = self.llm_client.generate_report(
                company=bundle.company.model_dump(),
                filing=bundle.filing.model_dump(),
                metrics_summary=summarize_metrics_for_prompt(metrics),
                warnings=warnings,
                themed_chunks=themed_chunks,
            )
            if llm_payload is not None:
                evidence_lookup = {
                    chunk.chunk_id: chunk
                    for chunk_list in themed_chunks.values()
                    for chunk in chunk_list
                }
                memo_sections, scorecard, citations = validate_model_payload(
                    payload=llm_payload,
                    evidence_lookup=evidence_lookup,
                    metrics=metrics,
                    filing_date=bundle.filing.filing_date,
                )
                memo_status = "available"
            else:
                warnings.append("DeepSeek is not configured, so the cited memo is unavailable.")
        except (LLMValidationError, ValueError, KeyError) as exc:
            warnings.append(f"Memo generation was unavailable: {exc}")

        response = AnalyzeResponse(
            company=bundle.company,
            filing=bundle.filing,
            metrics=metrics,
            charts=charts,
            scorecard=scorecard,
            memo_sections=memo_sections,
            citations=citations,
            evidence_chunks=evidence_chunks,
            warnings=warnings,
            memo_status=memo_status,  # type: ignore[arg-type]
        )
        if memo_status == "available":
            self.cache.save_json(analysis_cache_key, response.model_dump())
        return response

from typing import Literal

from pydantic import BaseModel, Field


MEMO_SECTION_TITLES = {
    "summary": "Business in Plain English",
    "business_quality": "Business Quality",
    "financial_strength": "Financial Strength",
    "risk_review": "Risks and Red Flags",
    "capital_allocation": "Capital Allocation",
    "valuation_context": "Valuation Context",
    "open_questions": "What Requires Human Judgment",
}

SCORECARD_LABELS = {
    "business_quality": "Business Quality",
    "financial_strength": "Financial Strength",
    "balance_sheet": "Balance Sheet",
    "capital_allocation": "Capital Allocation",
    "risk_burden": "Risk Burden",
}


class AnalyzeRequest(BaseModel):
    ticker: str = Field(..., min_length=1)
    force_refresh: bool = False


class CompanyInfo(BaseModel):
    name: str
    ticker: str
    cik: str
    exchange: str | None = None
    sic: str | None = None
    sic_description: str | None = None
    fiscal_year_end: str | None = None


class FilingInfo(BaseModel):
    accession_number: str
    filing_date: str
    filing_index_url: str
    filing_html_url: str
    form: str


class MetricPoint(BaseModel):
    fiscal_year: str
    value: float | None
    unit: str
    form: str
    filed: str
    frame: str | None = None
    source_concept: str | None = None


class MetricSeries(BaseModel):
    key: str
    label: str
    formatter: Literal["currency", "number", "percent"]
    points: list[MetricPoint]
    latest_value: float | None
    latest_fiscal_year: str | None = None


class ChartSeriesPoint(BaseModel):
    fiscal_year: str
    primary: float | None
    secondary: float | None = None


class ChartDefinition(BaseModel):
    key: str
    title: str
    subtitle: str
    kind: Literal["line", "bar", "paired_bar"]
    formatter: Literal["currency", "number", "percent"]
    primary_label: str
    secondary_label: str | None = None
    series: list[ChartSeriesPoint]


class EvidenceChunk(BaseModel):
    chunk_id: str
    section: str
    snippet: str
    source_url: str
    rank: float
    topics: list[str]


class Citation(BaseModel):
    id: str
    chunk_id: str
    section: str
    snippet: str
    source_url: str


class ScorecardItem(BaseModel):
    key: Literal[
        "business_quality",
        "financial_strength",
        "balance_sheet",
        "capital_allocation",
        "risk_burden",
    ]
    label: str
    score: Literal[1, 2, 3, 4, 5]
    rationale: str
    citation_ids: list[str]


class MemoParagraph(BaseModel):
    id: str
    text: str
    citation_ids: list[str]


class MemoSection(BaseModel):
    key: Literal[
        "summary",
        "business_quality",
        "financial_strength",
        "risk_review",
        "capital_allocation",
        "valuation_context",
        "open_questions",
    ]
    title: str
    paragraphs: list[MemoParagraph]


class AnalyzeResponse(BaseModel):
    company: CompanyInfo
    filing: FilingInfo
    metrics: list[MetricSeries]
    charts: list[ChartDefinition]
    scorecard: list[ScorecardItem]
    memo_sections: dict[str, MemoSection]
    citations: dict[str, Citation]
    evidence_chunks: list[EvidenceChunk]
    warnings: list[str]
    memo_status: Literal["available", "unavailable"]


export const memoSectionKeys = [
  "summary",
  "business_quality",
  "financial_strength",
  "risk_review",
  "capital_allocation",
  "valuation_context",
  "open_questions",
] as const;

export const scorecardKeys = [
  "business_quality",
  "financial_strength",
  "balance_sheet",
  "capital_allocation",
  "risk_burden",
] as const;

export type MemoSectionKey = (typeof memoSectionKeys)[number];
export type ScorecardKey = (typeof scorecardKeys)[number];
export type MemoStatus = "available" | "unavailable";
export type FormatterKind = "currency" | "number" | "percent";
export type ChartKind = "line" | "bar" | "paired_bar";

export interface AnalyzeRequest {
  ticker: string;
  force_refresh?: boolean;
}

export interface CompanyInfo {
  name: string;
  ticker: string;
  cik: string;
  exchange?: string | null;
  sic?: string | null;
  sic_description?: string | null;
  fiscal_year_end?: string | null;
}

export interface FilingInfo {
  accession_number: string;
  filing_date: string;
  filing_index_url: string;
  filing_html_url: string;
  form: string;
}

export interface MetricPoint {
  fiscal_year: string;
  value: number | null;
  unit: string;
  form: string;
  filed: string;
  frame?: string | null;
  source_concept?: string | null;
}

export interface MetricSeries {
  key: string;
  label: string;
  formatter: FormatterKind;
  points: MetricPoint[];
  latest_value: number | null;
  latest_fiscal_year?: string | null;
}

export interface ChartSeriesPoint {
  fiscal_year: string;
  primary: number | null;
  secondary?: number | null;
}

export interface ChartDefinition {
  key: string;
  title: string;
  subtitle: string;
  kind: ChartKind;
  formatter: FormatterKind;
  primary_label: string;
  secondary_label?: string | null;
  series: ChartSeriesPoint[];
}

export interface EvidenceChunk {
  chunk_id: string;
  section: string;
  snippet: string;
  source_url: string;
  rank: number;
  topics: string[];
}

export interface Citation {
  id: string;
  chunk_id: string;
  section: string;
  snippet: string;
  source_url: string;
}

export interface ScorecardItem {
  key: ScorecardKey;
  label: string;
  score: 1 | 2 | 3 | 4 | 5;
  rationale: string;
  citation_ids: string[];
}

export interface MemoParagraph {
  id: string;
  text: string;
  citation_ids: string[];
}

export interface MemoSection {
  key: MemoSectionKey;
  title: string;
  paragraphs: MemoParagraph[];
}

export interface AnalyzeResponse {
  company: CompanyInfo;
  filing: FilingInfo;
  metrics: MetricSeries[];
  charts: ChartDefinition[];
  scorecard: ScorecardItem[];
  memo_sections: Record<MemoSectionKey, MemoSection>;
  citations: Record<string, Citation>;
  evidence_chunks: EvidenceChunk[];
  warnings: string[];
  memo_status: MemoStatus;
}

export function formatValue(value: number | null, kind: FormatterKind): string {
  if (value === null || Number.isNaN(value)) {
    return "n/a";
  }

  if (kind === "currency") {
    const absolute = Math.abs(value);
    if (absolute >= 1_000_000_000) {
      return `$${(value / 1_000_000_000).toFixed(1)}B`;
    }
    if (absolute >= 1_000_000) {
      return `$${(value / 1_000_000).toFixed(1)}M`;
    }
    if (absolute >= 1_000) {
      return `$${(value / 1_000).toFixed(1)}K`;
    }
    return `$${value.toFixed(0)}`;
  }

  if (kind === "percent") {
    return `${value.toFixed(1)}%`;
  }

  if (Math.abs(value) >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(1)}B`;
  }
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(1)}K`;
  }
  return value.toFixed(1);
}


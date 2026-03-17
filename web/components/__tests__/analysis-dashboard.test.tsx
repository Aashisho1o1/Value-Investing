import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { AnalysisDashboard } from "@/components/analysis-dashboard";
import type { AnalyzeResponse } from "@shared/analysis";

const response: AnalyzeResponse = {
  company: {
    name: "Apple Inc.",
    ticker: "AAPL",
    cik: "0000320193",
    exchange: null,
    sic: null,
    sic_description: null,
    fiscal_year_end: "0928",
  },
  filing: {
    accession_number: "0000320193-24-000123",
    filing_date: "2024-11-01",
    filing_index_url: "https://example.com/index.html",
    filing_html_url: "https://example.com/filing.html",
    form: "10-K",
  },
  metrics: [
    {
      key: "revenue",
      label: "Revenue",
      formatter: "currency",
      latest_value: 391000000000,
      latest_fiscal_year: "2024",
      points: [
        { fiscal_year: "2022", value: 394000000000, unit: "USD", form: "10-K", filed: "2022-10-28", frame: null, source_concept: "RevenueFromContractWithCustomerExcludingAssessedTax" },
        { fiscal_year: "2023", value: 383000000000, unit: "USD", form: "10-K", filed: "2023-11-03", frame: null, source_concept: "RevenueFromContractWithCustomerExcludingAssessedTax" },
        { fiscal_year: "2024", value: 391000000000, unit: "USD", form: "10-K", filed: "2024-11-01", frame: null, source_concept: "RevenueFromContractWithCustomerExcludingAssessedTax" }
      ],
    },
    {
      key: "operating_income",
      label: "Operating Income",
      formatter: "currency",
      latest_value: 123000000000,
      latest_fiscal_year: "2024",
      points: [
        { fiscal_year: "2022", value: 119000000000, unit: "USD", form: "10-K", filed: "2022-10-28", frame: null, source_concept: "OperatingIncomeLoss" },
        { fiscal_year: "2023", value: 114000000000, unit: "USD", form: "10-K", filed: "2023-11-03", frame: null, source_concept: "OperatingIncomeLoss" },
        { fiscal_year: "2024", value: 123000000000, unit: "USD", form: "10-K", filed: "2024-11-01", frame: null, source_concept: "OperatingIncomeLoss" }
      ],
    },
    {
      key: "cash_from_operations",
      label: "Cash From Operations",
      formatter: "currency",
      latest_value: 118000000000,
      latest_fiscal_year: "2024",
      points: [
        { fiscal_year: "2022", value: 122000000000, unit: "USD", form: "10-K", filed: "2022-10-28", frame: null, source_concept: "NetCashProvidedByUsedInOperatingActivities" },
        { fiscal_year: "2023", value: 111000000000, unit: "USD", form: "10-K", filed: "2023-11-03", frame: null, source_concept: "NetCashProvidedByUsedInOperatingActivities" },
        { fiscal_year: "2024", value: 118000000000, unit: "USD", form: "10-K", filed: "2024-11-01", frame: null, source_concept: "NetCashProvidedByUsedInOperatingActivities" }
      ],
    },
    {
      key: "cash_and_equivalents",
      label: "Cash and Equivalents",
      formatter: "currency",
      latest_value: 32100000000,
      latest_fiscal_year: "2024",
      points: [
        { fiscal_year: "2022", value: 23600000000, unit: "USD", form: "10-K", filed: "2022-10-28", frame: null, source_concept: "CashAndCashEquivalentsAtCarryingValue" },
        { fiscal_year: "2023", value: 29900000000, unit: "USD", form: "10-K", filed: "2023-11-03", frame: null, source_concept: "CashAndCashEquivalentsAtCarryingValue" },
        { fiscal_year: "2024", value: 32100000000, unit: "USD", form: "10-K", filed: "2024-11-01", frame: null, source_concept: "CashAndCashEquivalentsAtCarryingValue" }
      ],
    },
    {
      key: "total_debt",
      label: "Total Debt",
      formatter: "currency",
      latest_value: 104000000000,
      latest_fiscal_year: "2024",
      points: [
        { fiscal_year: "2022", value: 111000000000, unit: "USD", form: "10-K", filed: "2022-10-28", frame: null, source_concept: "LongTermDebtAndCapitalLeaseObligations" },
        { fiscal_year: "2023", value: 108000000000, unit: "USD", form: "10-K", filed: "2023-11-03", frame: null, source_concept: "LongTermDebtAndCapitalLeaseObligations" },
        { fiscal_year: "2024", value: 104000000000, unit: "USD", form: "10-K", filed: "2024-11-01", frame: null, source_concept: "LongTermDebtAndCapitalLeaseObligations" }
      ],
    }
  ],
  charts: [
    {
      key: "revenue_trend",
      title: "Revenue Trend",
      subtitle: "Annual revenue from SEC company facts.",
      kind: "line",
      formatter: "currency",
      primary_label: "Revenue",
      secondary_label: null,
      series: [
        { fiscal_year: "2022", primary: 394000000000, secondary: null },
        { fiscal_year: "2023", primary: 383000000000, secondary: null },
        { fiscal_year: "2024", primary: 391000000000, secondary: null }
      ],
    }
  ],
  scorecard: [
    {
      key: "business_quality",
      label: "Business Quality",
      score: 4,
      rationale: "The filing presents a coherent business overview.",
      citation_ids: ["c1"],
    }
  ],
  memo_sections: {
    summary: {
      key: "summary",
      title: "Business in Plain English",
      paragraphs: [{ id: "p1", text: "Apple sells devices and services across a broad installed base.", citation_ids: ["c1"] }],
    },
    business_quality: {
      key: "business_quality",
      title: "Business Quality",
      paragraphs: [{ id: "p2", text: "The filing emphasizes ecosystem depth and repeat engagement.", citation_ids: ["c1"] }],
    },
    financial_strength: {
      key: "financial_strength",
      title: "Financial Strength",
      paragraphs: [{ id: "p3", text: "Cash generation remains a central strength in the filing.", citation_ids: ["c1"] }],
    },
    risk_review: {
      key: "risk_review",
      title: "Risks and Red Flags",
      paragraphs: [{ id: "p4", text: "Competition and supply chain risk remain visible.", citation_ids: ["c1"] }],
    },
    capital_allocation: {
      key: "capital_allocation",
      title: "Capital Allocation",
      paragraphs: [{ id: "p5", text: "Management discusses capital returns and reinvestment.", citation_ids: ["c1"] }],
    },
    valuation_context: {
      key: "valuation_context",
      title: "Valuation Context",
      paragraphs: [{ id: "p6", text: "The filing suggests strong earning power but valuation still needs market data.", citation_ids: ["c1"] }],
    },
    open_questions: {
      key: "open_questions",
      title: "What Requires Human Judgment",
      paragraphs: [{ id: "p7", text: "Industry durability and competition still require judgment.", citation_ids: ["c1"] }],
    },
  },
  citations: {
    c1: {
      id: "c1",
      chunk_id: "business-001",
      section: "Business",
      snippet: "Apple designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories.",
      source_url: "https://example.com/filing.html",
    }
  },
  evidence_chunks: [
    {
      chunk_id: "business-001",
      section: "Business",
      snippet: "Apple designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories.",
      source_url: "https://example.com/filing.html",
      rank: 8.5,
      topics: ["business"],
    }
  ],
  warnings: [],
  memo_status: "available",
};

describe("AnalysisDashboard", () => {
  it("opens the evidence drawer when a citation is clicked", async () => {
    const user = userEvent.setup();
    render(<AnalysisDashboard response={response} />);

    await user.click(screen.getAllByRole("button", { name: "C1" })[0]);

    expect(screen.getByText("Citation c1")).toBeInTheDocument();
    expect(
      screen.getAllByText(/Apple designs, manufactures, and markets smartphones/i)
        .length,
    ).toBeGreaterThan(0);
  });

  it("shows an unavailable memo notice when the memo layer fails", () => {
    render(
      <AnalysisDashboard
        response={{ ...response, memo_status: "unavailable", scorecard: [] }}
      />,
    );

    expect(
      screen.getByText(/The cited memo is unavailable right now/i),
    ).toBeInTheDocument();
  });
});

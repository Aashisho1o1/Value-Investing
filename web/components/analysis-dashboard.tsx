"use client";

import React from "react";
import {
  AnalyzeResponse,
  Citation,
  MemoSectionKey,
  formatValue,
  memoSectionKeys,
} from "@shared/analysis";
import { useMemo, useState } from "react";

import { ChartCard } from "@/components/chart-card";
import { EvidenceDrawer } from "@/components/evidence-drawer";

const scoreClasses = {
  1: "bg-ember/10 text-ember border-ember/20",
  2: "bg-ember/10 text-ember border-ember/20",
  3: "bg-sand text-ink border-ink/10",
  4: "bg-moss/10 text-moss border-moss/20",
  5: "bg-moss/10 text-moss border-moss/20",
};

function metricValue(response: AnalyzeResponse, key: string) {
  return response.metrics.find((metric) => metric.key === key) ?? null;
}

function latestMetricLabel(
  response: AnalyzeResponse,
  key: string,
  fallback: string,
): string {
  const metric = metricValue(response, key);
  if (!metric) {
    return "n/a";
  }
  return formatValue(metric.latest_value, metric.formatter) || fallback;
}

export function AnalysisDashboard({ response }: { response: AnalyzeResponse }) {
  const [activeCitationId, setActiveCitationId] = useState<string | null>(null);
  const [activeChunkId, setActiveChunkId] = useState<string | null>(null);

  const activeCitation: Citation | null = activeCitationId
    ? response.citations[activeCitationId] ?? null
    : null;
  const activeChunk = useMemo(
    () =>
      activeChunkId
        ? response.evidence_chunks.find((chunk) => chunk.chunk_id === activeChunkId) ?? null
        : null,
    [activeChunkId, response.evidence_chunks],
  );

  return (
    <div className="pb-16">
      <header className="sticky top-0 z-30 border-b border-ink/10 bg-parchment/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-5 sm:px-8 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="eyebrow">Latest 10-K</p>
            <h1 className="mt-2 font-display text-4xl text-ink sm:text-5xl">
              {response.company.name}
            </h1>
            <p className="mt-3 text-sm leading-6 text-ink/65">
              {response.company.ticker} • Filed {response.filing.filing_date} •
              {" "}
              <a href={response.filing.filing_html_url} target="_blank" rel="noreferrer">
                SEC source
              </a>
            </p>
          </div>
          <div className="max-w-md rounded-[1.5rem] border border-ink/10 bg-white/70 px-5 py-4 text-sm leading-6 text-ink/65">
            Research aid only. This memo is evidence-backed but incomplete and
            should not be treated as investment advice or a precise valuation.
          </div>
        </div>
      </header>

      <main className="mx-auto mt-8 grid max-w-7xl gap-6 px-5 sm:px-8">
        <section className="grid gap-6 lg:grid-cols-[1.2fr,0.8fr]">
          <article className="panel p-6">
            <p className="eyebrow">Snapshot</p>
            <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {[
                ["Revenue", latestMetricLabel(response, "revenue", "n/a")],
                ["Operating Income", latestMetricLabel(response, "operating_income", "n/a")],
                ["Cash From Ops", latestMetricLabel(response, "cash_from_operations", "n/a")],
                ["Cash vs Debt", `${latestMetricLabel(response, "cash_and_equivalents", "n/a")} / ${latestMetricLabel(response, "total_debt", "n/a")}`],
              ].map(([label, value]) => (
                <div key={label} className="rounded-[1.4rem] bg-sand/60 p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ink/55">
                    {label}
                  </p>
                  <p className="mt-3 font-display text-3xl text-ink">{value}</p>
                </div>
              ))}
            </div>
            {response.warnings.length ? (
              <div className="mt-5 rounded-[1.4rem] border border-ember/15 bg-ember/10 p-4 text-sm leading-6 text-ink/75">
                {response.warnings.map((warning) => (
                  <p key={warning}>{warning}</p>
                ))}
              </div>
            ) : null}
          </article>

          <article className="panel p-6">
            <p className="eyebrow">Scorecard</p>
            <div className="mt-4 grid gap-4">
              {response.scorecard.length ? (
                response.scorecard.map((item) => (
                  <div
                    key={item.key}
                    className="rounded-[1.4rem] border border-ink/10 bg-white/70 p-4"
                  >
                    <div className="flex items-center justify-between gap-4">
                      <h3 className="text-lg font-semibold text-ink">{item.label}</h3>
                      <span
                        className={`rounded-full border px-3 py-1 text-sm font-semibold ${scoreClasses[item.score]}`}
                      >
                        {item.score}/5
                      </span>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-ink/75">
                      {item.rationale}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {item.citation_ids.map((citationId) => (
                        <button
                          key={citationId}
                          type="button"
                          className="citation-chip"
                          onClick={() => {
                            setActiveChunkId(null);
                            setActiveCitationId(citationId);
                          }}
                        >
                          {citationId.toUpperCase()}
                        </button>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <p className="rounded-[1.4rem] bg-sand/60 p-4 text-sm leading-6 text-ink/70">
                  Scorecard is unavailable until the memo layer returns a fully
                  cited result.
                </p>
              )}
            </div>
          </article>
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          {response.charts.map((chart) => (
            <ChartCard key={chart.key} chart={chart} />
          ))}
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.2fr,0.8fr]">
          <article className="panel p-6">
            <p className="eyebrow">Memo</p>
            {response.memo_status === "unavailable" ? (
              <div className="mt-4 rounded-[1.5rem] border border-ember/15 bg-ember/10 p-5 text-sm leading-7 text-ink/75">
                The cited memo is unavailable right now. You can still review the
                normalized financials and the highest-ranked filing excerpts.
              </div>
            ) : null}
            <div className="mt-6 space-y-8">
              {memoSectionKeys.map((key) => {
                const section = response.memo_sections[key as MemoSectionKey];
                return (
                  <section key={key}>
                    <h2 className="font-display text-3xl text-ink">
                      {section.title}
                    </h2>
                    <div className="mt-4 space-y-4">
                      {section.paragraphs.length ? (
                        section.paragraphs.map((paragraph) => (
                          <div key={paragraph.id} className="rounded-[1.4rem] bg-white/70 p-5">
                            <p className="text-[15px] leading-7 text-ink/80">
                              {paragraph.text}
                            </p>
                            <div className="mt-3 flex flex-wrap gap-2">
                              {paragraph.citation_ids.map((citationId) => (
                                <button
                                  key={citationId}
                                  type="button"
                                  className="citation-chip"
                                  onClick={() => {
                                    setActiveChunkId(null);
                                    setActiveCitationId(citationId);
                                  }}
                                >
                                  {citationId.toUpperCase()}
                                </button>
                              ))}
                            </div>
                          </div>
                        ))
                      ) : (
                        <p className="text-sm leading-7 text-ink/50">
                          No cited narrative available for this section.
                        </p>
                      )}
                    </div>
                  </section>
                );
              })}
            </div>
          </article>

          <article className="panel p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="eyebrow">Evidence</p>
                <h2 className="mt-2 font-display text-3xl text-ink">
                  Highest-ranked excerpts
                </h2>
              </div>
            </div>
            <div className="mt-5 space-y-4">
              {response.evidence_chunks.slice(0, 8).map((chunk) => (
                <button
                  key={chunk.chunk_id}
                  type="button"
                  onClick={() => {
                    setActiveCitationId(null);
                    setActiveChunkId(chunk.chunk_id);
                  }}
                  className="w-full rounded-[1.4rem] border border-ink/10 bg-white/75 p-4 text-left transition hover:border-moss/25 hover:bg-white"
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-moss/80">
                      {chunk.section}
                    </p>
                    <span className="text-xs text-ink/45">
                      Rank {chunk.rank.toFixed(1)}
                    </span>
                  </div>
                  <p className="mt-3 text-sm leading-7 text-ink/75">
                    {chunk.snippet}
                  </p>
                </button>
              ))}
            </div>
          </article>
        </section>
      </main>

      <EvidenceDrawer
        citation={activeCitation}
        chunk={activeChunk}
        onClose={() => {
          setActiveCitationId(null);
          setActiveChunkId(null);
        }}
      />
    </div>
  );
}

"use client";

import React from "react";
import type { Citation, EvidenceChunk } from "@shared/analysis";

export function EvidenceDrawer({
  citation,
  chunk,
  onClose,
}: {
  citation: Citation | null;
  chunk: EvidenceChunk | null;
  onClose: () => void;
}) {
  if (!citation && !chunk) {
    return null;
  }

  const section = citation?.section ?? chunk?.section ?? "Evidence";
  const snippet = citation?.snippet ?? chunk?.snippet ?? "";
  const sourceUrl = citation?.source_url ?? chunk?.source_url ?? "#";
  const label = citation ? `Citation ${citation.id}` : "Evidence";

  return (
    <>
      <button
        type="button"
        onClick={onClose}
        className="fixed inset-0 z-40 bg-ink/35 backdrop-blur-sm"
        aria-label="Close evidence drawer"
      />
      <aside className="fixed inset-x-0 bottom-0 z-50 rounded-t-[2rem] border border-ink/10 bg-parchment p-6 shadow-2xl md:inset-y-0 md:right-0 md:left-auto md:w-[28rem] md:rounded-none md:rounded-l-[2rem] md:p-8">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="eyebrow">{label}</p>
            <h3 className="mt-2 font-display text-3xl text-ink">{section}</h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full border border-ink/10 px-4 py-2 text-sm font-semibold text-ink transition hover:border-moss/40 hover:bg-white"
          >
            Close
          </button>
        </div>

        <p className="mt-6 rounded-[1.5rem] bg-white/80 p-5 text-sm leading-7 text-ink/80">
          {snippet}
        </p>

        <div className="mt-6 rounded-[1.5rem] border border-ink/10 bg-white/70 p-5">
          <p className="eyebrow">Source</p>
          <a
            href={sourceUrl}
            target="_blank"
            rel="noreferrer"
            className="mt-3 inline-flex text-sm font-semibold"
          >
            Open filing excerpt
          </a>
        </div>
      </aside>
    </>
  );
}

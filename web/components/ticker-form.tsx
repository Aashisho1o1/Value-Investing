"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { FormEvent, useState, useTransition } from "react";

const SAMPLE_TICKERS = ["AAPL", "MSFT", "KO", "COST"];

export function TickerForm() {
  const router = useRouter();
  const [ticker, setTicker] = useState("AAPL");
  const [isPending, startTransition] = useTransition();

  function submit(nextTicker: string) {
    const normalized = nextTicker.trim().toUpperCase();
    if (!normalized) {
      return;
    }
    startTransition(() => {
      router.push(`/analysis/${normalized}`);
    });
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    submit(ticker);
  }

  return (
    <div className="panel relative overflow-hidden p-8 sm:p-10">
      <div className="absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-moss/50 to-transparent" />
      <p className="eyebrow">10-K Research Aid</p>
      <h1 className="mt-4 max-w-2xl font-display text-4xl leading-tight text-ink sm:text-6xl">
        Turn the latest annual filing into a cited value memo.
      </h1>
      <p className="mt-5 max-w-2xl text-base leading-7 text-ink/75 sm:text-lg">
        Enter a US public ticker and get a conservative first-pass analysis:
        normalized financial trends, a compact scorecard, narrative sections,
        and exact snippets back to the filing.
      </p>

      <form onSubmit={onSubmit} className="mt-8 flex flex-col gap-4 sm:flex-row">
        <label className="sr-only" htmlFor="ticker-input">
          Ticker
        </label>
        <input
          id="ticker-input"
          value={ticker}
          onChange={(event) => setTicker(event.target.value.toUpperCase())}
          placeholder="AAPL"
          className="h-14 flex-1 rounded-full border border-ink/15 bg-white px-6 text-lg uppercase tracking-[0.18em] text-ink outline-none transition focus:border-moss focus:ring-4 focus:ring-moss/10"
        />
        <button
          type="submit"
          disabled={isPending}
          className="h-14 rounded-full bg-ink px-8 text-sm font-semibold uppercase tracking-[0.2em] text-parchment transition hover:bg-pine disabled:cursor-not-allowed disabled:bg-ink/60"
        >
          {isPending ? "Analyzing..." : "Analyze"}
        </button>
      </form>

      <div className="mt-6 flex flex-wrap gap-3">
        {SAMPLE_TICKERS.map((sample) => (
          <button
            key={sample}
            type="button"
            onClick={() => submit(sample)}
            className="rounded-full border border-ink/10 bg-white/70 px-4 py-2 text-sm font-semibold tracking-[0.16em] text-ink transition hover:border-moss/40 hover:bg-moss/10"
          >
            {sample}
          </button>
        ))}
      </div>

      <p className="mt-7 text-sm leading-6 text-ink/60">
        This is a research aid, not investment advice. Intrinsic value remains
        an estimate and the final judgment belongs to the reader.
      </p>
    </div>
  );
}

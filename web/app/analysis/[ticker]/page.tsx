import Link from "next/link";

import { AnalysisDashboard } from "@/components/analysis-dashboard";
import { analyzeTicker } from "@/lib/api";

export default async function AnalysisPage({
  params,
}: {
  params: Promise<{ ticker: string }>;
}) {
  const { ticker } = await params;

  try {
    const response = await analyzeTicker(ticker);
    return <AnalysisDashboard response={response} />;
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unable to analyze this ticker.";

    return (
      <main className="mx-auto max-w-4xl px-5 py-16 sm:px-8">
        <div className="panel p-8">
          <p className="eyebrow">Analysis Error</p>
          <h1 className="mt-3 font-display text-4xl text-ink">
            Could not analyze {ticker.toUpperCase()}
          </h1>
          <p className="mt-4 text-base leading-7 text-ink/70">{message}</p>
          <Link
            href="/"
            className="mt-6 inline-flex rounded-full bg-ink px-5 py-3 text-sm font-semibold uppercase tracking-[0.18em] text-parchment no-underline transition hover:bg-pine"
          >
            Try another ticker
          </Link>
        </div>
      </main>
    );
  }
}


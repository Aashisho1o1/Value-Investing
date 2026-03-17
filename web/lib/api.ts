import type { AnalyzeResponse } from "@shared/analysis";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function analyzeTicker(
  ticker: string,
): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ ticker }),
    cache: "no-store",
  });

  if (!response.ok) {
    let detail = "Unable to analyze ticker";
    try {
      const payload = (await response.json()) as { detail?: string };
      detail = payload.detail ?? detail;
    } catch {
      // Keep the default message when the body is not JSON.
    }
    throw new Error(detail);
  }

  return (await response.json()) as AnalyzeResponse;
}


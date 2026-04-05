import type { TransactionRow, AnalysisRunRow } from "../types/db";

const apiBaseUrl =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:18000";

export async function fetchTransactions(userId: string, limit = 200) {
  const response = await fetch(
    `${apiBaseUrl}/transactions/${encodeURIComponent(userId)}?limit=${limit}`
  );
  if (!response.ok) {
    throw new Error(await response.text());
  }
  const payload = await response.json();
  return (payload.items ?? []) as TransactionRow[];
}

export async function fetchLatestAnalysisRun(userId: string) {
  const response = await fetch(
    `${apiBaseUrl}/analysis-runs/latest/${encodeURIComponent(userId)}`
  );
  if (!response.ok) {
    throw new Error(await response.text());
  }
  const payload = await response.json();
  return payload as AnalysisRunRow | null;
}

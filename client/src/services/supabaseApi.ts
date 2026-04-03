import { supabase } from "../lib/supabaseClient";
import type { TransactionRow, AnalysisRunRow } from "../types/db";

export async function fetchTransactions(userId: string, limit = 200) {
  const { data, error } = await supabase
    .from("transactions")
    .select("*")
    .eq("user_id", userId)
    .order("date", { ascending: true })
    .limit(limit);

  if (error) throw error;
  return data as TransactionRow[];
}

export async function fetchLatestAnalysisRun(userId: string) {
  const { data, error } = await supabase
    .from("analysis_runs")
    .select("*")
    .eq("user_id", userId)
    .order("created_at", { ascending: false })
    .limit(1)
    .maybeSingle();

  if (error) throw error;
  return data as AnalysisRunRow | null;
}

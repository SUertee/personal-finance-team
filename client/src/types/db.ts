export type TransactionRow = {
  id: string;
  user_id: string;
  date: string;        // "2025-03-01"
  month: string;       // "2025-03"
  description: string;
  amount: number;
  balance: number | null;
  type: "debit" | "credit" | string;
  category?: string | null;
  is_anomaly?: boolean | null;
  raw?: string | null;
  created_at?: string;
};

export type AnalysisRunRow = {
  id: string;
  user_id: string;
  created_at: string;
  period_start?: string | null;
  period_end?: string | null;
  monthly_totals?: any; // 你可以后面再细化
  input?: any;
  output?: any;
};

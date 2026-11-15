export interface ReviewItem {
  record_id: string;
  timestamp: string;
  customer_id: string;
  terminal_id: string;
  amount: number;
  rank: number;
  score: number;
  score_kind: "uncalibrated_classifier_score";
  reasons: string[];
  explanation_kind: string;
  warnings: string[];
  review_required: boolean;
  model_version: string;
  validation_status: string;
}
export interface Analysis {
  analyzed_count: number;
  history_count: number;
  top_k: number;
  queue_count: number;
  operations: ReviewItem[];
  warnings: string[];
  model_id: string;
  model_version: string;
  research_status: string;
  score_kind: string;
  processing_time_ms: number;
  disclaimer: string;
}
export interface Metrics {
  n: number;
  positives: number;
  precision: number;
  recall: number;
  average_precision: number;
  f1: number;
  precision_at_1000: number;
  positives_at_1000: number;
  threshold: number;
}
export interface Model {
  model_id: string;
  name: string;
  version: string;
  available: boolean;
  research_status: string;
  recommended_for_live_detection: boolean;
  score_kind: string;
  file_types: string[];
  input_schema: { required: string[] };
  history_requirements: {
    customer_pair_complete_calendar_days: number;
    terminal_days: number;
  };
  limits: {
    max_file_bytes: number;
    max_request_bytes: number;
    max_transactions: number;
    max_history: number;
    max_combined_rows: number;
  };
  limitations: string[];
  benchmark: { test: Metrics; validation: Metrics };
  baselines: { amount: Metrics };
  benchmark_provenance: {
    split_periods?: Record<string, string>;
    terminal_compromise_recall: number;
    test_caveat: string;
    ranking_policy: string;
    source: string;
    date: string;
  };
  disclaimer: string;
}
export interface Health {
  status: "ready" | "unavailable";
  model_available: boolean;
}
export type Source =
  | { kind: "demo" }
  | { kind: "upload"; transactions: File; history: File | null };

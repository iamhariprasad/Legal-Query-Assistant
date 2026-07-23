export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

export interface Citation {
  document_id: string;
  title: string;
  source: string;
  url: string;
  snippet: string;
  score: number;
}

export interface ChatResponse {
  id: string | null;
  answer: string;
  confidence: number;
  citations: Citation[];
  refused: boolean;
  refusal_reason: string | null;
  latency_ms: number;
  metadata: Record<string, unknown>;
}

export interface ChatHistoryItem extends ChatResponse {
  id: string;
  query: string;
  created_at: string;
}

export interface SearchResult {
  document_id: string;
  title: string;
  headline: string;
  source: string;
  url: string;
  docsize: number | null;
  citations: string[];
}

export interface LegalSearchResponse {
  query: string;
  found: number;
  results: SearchResult[];
  cache_hit: boolean;
  latency_ms: number;
}

export interface EvaluationSummary {
  total: number;
  citation_accuracy: number;
  precision: number;
  recall: number;
  faithfulness: number;
  hallucination_rate: number;
  context_recall: number;
  avg_latency_ms: number;
}

export interface EvaluationResult {
  id: string;
  query: string;
  expected_issue: string;
  expected_citations: string[];
  answer: string;
  refused: boolean;
  citation_accuracy: number;
  precision: number;
  recall: number;
  faithfulness: number;
  hallucination_rate: number;
  context_recall: number;
  latency_ms: number;
}

export interface EvaluationResultsResponse {
  summary: EvaluationSummary;
  results: EvaluationResult[];
}

export interface GuardrailLog {
  id: string;
  chat_id: string | null;
  query: string;
  trigger: string;
  reason: string;
  severity: string;
  metadata_json: Record<string, unknown>;
  created_at: string;
}

export interface Metric {
  name: string;
  value: number;
  labels: Record<string, unknown>;
  created_at: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  dependencies: Record<string, string>;
}

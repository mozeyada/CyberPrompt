export interface Prompt {
  prompt_id: string;
  text: string;
  source: 'cysecbench' | 'curated' | 'CySecBench';
  scenario: 'SOC_INCIDENT' | 'CTI_SUMMARY' | 'GRC_MAPPING';
  length_bin: 'XS' | 'S' | 'M' | 'L' | 'XL';
  complexity?: number;
  safety_tag?: 'SAFE_DOC' | 'REDACTED' | 'BLOCKED';
  category?: string;
  metadata?: {
    word_count: number;
    length_bin: 'short' | 'medium' | 'long';
    original_category: string;
    dataset_version: string;
  };
  tags?: string[];
  created_at?: string;
}

export interface TokenMetrics {
  input: number;
  output: number;
  total: number;
}

export interface EconomicsMetrics {
  aud_cost: number;
  unit_price_in: number;
  unit_price_out: number;
  latency_ms: number;
}

export interface RubricScores {
  technical_accuracy: number;
  actionability: number;
  completeness: number;
  compliance_alignment: number;
  risk_awareness: number;
  relevance: number;
  clarity: number;
  composite: number;
}

export interface RiskMetrics {
  hallucination_flags: number;
}

export interface Run {
  run_id: string;
  prompt_id: string;
  model: string;
  scenario: string;
  length_bin: string;
  settings: {
    temperature: number;
    max_output_tokens: number;
    seed: number;
  };
  status: 'queued' | 'running' | 'succeeded' | 'failed';
  tokens?: TokenMetrics;
  economics?: EconomicsMetrics;
  output_ref?: string;
  judge: {
    type: 'llm' | 'human';
    judge_model?: string;
    prompt_ver: string;
  };
  scores?: RubricScores;
  risk_metrics?: RiskMetrics;
  bias_controls: {
    fsp: boolean;
    granularity_demo: boolean;
  };
  created_at: string;
  updated_at: string;
}

export interface RunPlanRequest {
  prompts: string[];
  models: string[];
  repeats: number;
  settings: {
    temperature: number;
    max_output_tokens: number;
    seed: number;
  };
  judge: {
    type: 'llm' | 'human';
    judge_model?: string;
    prompt_ver: string;
  };
  bias_controls: {
    fsp: boolean;
    granularity_demo: boolean;
  };
}

export interface CostQualityPoint {
  model: string;
  length_bin: string;
  scenario: string;
  x: number; // AUD per 1k tokens
  y: number; // Composite score
  count: number;
  cost_std: number;
  composite_std: number;
}

export interface LengthBiasData {
  dimension: string;
  scenario: string;
  bins?: Array<{ length_bin: string; value: number }>;
  models?: Array<{
    model: string;
    slope: number;
    intercept: number;
    r_squared: number;
    p_value: number;
    slope_ci_lower: number;
    slope_ci_upper: number;
    bins: Record<string, { avg_score: number; count: number; scores: number[] }>;
  }>;
  slopes: Array<{
    model: string;
    slope: number;
    intercept: number;
    r_squared: number;
    p_value: number;
    slope_ci_lower: number;
    slope_ci_upper: number;
    bins: Record<string, { avg_score: number; count: number; scores: number[] }>;
  }>;
  bin_data: any[];
}

export interface RiskCurvesData {
  scenario: string;
  length_bins?: Array<{ length_bin: string; value: number }>;
  risk_curves: Record<string, {
    risk_awareness: Array<{ length_bin: string; value: number }>;
    hallucination_rate: Array<{ length_bin: string; value: number }>;
  }>;
  raw_data: any[];
}

export interface Prompt {
  prompt_id: string;
  text: string;
  source: 'cysecbench' | 'curated' | 'CySecBench' | 'adaptive' | 'static';
  scenario: 'SOC_INCIDENT' | 'CTI_SUMMARY' | 'GRC_MAPPING';
  length_bin: 'S' | 'M' | 'L';
  token_count?: number;
  complexity?: number;
  safety_tag?: 'SAFE_DOC' | 'REDACTED' | 'BLOCKED';
  category?: string;
  dataset_version?: string;
  metadata?: {
    word_count?: number;
    token_count?: number;
    length_bin?: 'short' | 'medium' | 'long';
    original_category?: string;
    dataset_version?: string;
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
  source: 'static' | 'adaptive';
  experiment_id?: string;
  dataset_version?: string;
  settings: {
    temperature: number;
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
  ensemble_evaluation?: EnsembleEvaluation;
  created_at: string;
  updated_at: string;
}

export interface JudgeResult {
  judge_model: string;
  scores: RubricScores;
  raw_response: string;
  evaluation_time: string;
  tokens_used: number;
  cost_usd: number;
  fsp_used: boolean;
}

export interface AggregatedScores {
  mean_scores: RubricScores;
  median_scores?: RubricScores;
  std_scores?: RubricScores;
  confidence_95_ci: Record<string, [number, number]>;
}

export interface ReliabilityMetrics {
  pearson_correlations: Record<string, number>;
  fleiss_kappa: number;
  inter_judge_agreement: string;
}

export interface EnsembleEvaluation {
  evaluation_id: string;
  primary_judge?: JudgeResult;
  secondary_judge?: JudgeResult;
  tertiary_judge?: JudgeResult;
  aggregated?: AggregatedScores;
  reliability_metrics?: ReliabilityMetrics;
}

export interface RunPlanRequest {
  prompts: string[];
  models: string[];
  repeats: number;
  settings: {
    temperature: number;
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

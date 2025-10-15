import axios from 'axios';
import type { 
  Prompt, 
  Run, 
  RunPlanRequest, 
  CostQualityPoint, 
  LengthBiasData, 
  RiskCurvesData 
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || 'supersecret1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'x-api-key': API_KEY,
  },
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    return Promise.reject(error);
  }
);

// Prompts API
export const promptsApi = {
  import: async (prompts: any[]): Promise<{ imported: number; rejected: number; prompt_ids: string[] }> => {
    const response = await api.post('/prompts/import', prompts);
    return response.data;
  },

  list: async (params: {
    scenario?: string;
    length_bin?: string;
    source?: string;
    prompt_type?: string;
    include_variants?: boolean;
    q?: string;
    page?: number;
    limit?: number;
  } = {}): Promise<{ prompts: Prompt[]; page: number; limit: number; count: number }> => {
    const response = await api.get('/prompts/', { params });
    return response.data;
  },

  get: async (promptId: string): Promise<{ prompt: Prompt }> => {
    const response = await api.get(`/prompts/${promptId}`);
    return response.data;
  },

  generateFromDocument: async (docId: string): Promise<{
    message: string;
    doc_id: string;
    status: string;
  }> => {
    const response = await api.post(`/prompts/generate-from-document/${docId}`);
    return response.data;
  },
};

// Runs API
export const runsApi = {
  plan: async (planRequest: RunPlanRequest): Promise<{ message: string; run_ids: string[]; total_runs: number }> => {
    const response = await api.post('/runs/plan', planRequest);
    return response.data;
  },

  execute: async (runIds: string[]): Promise<{ results: any[]; summary: any }> => {
    const response = await api.post('/runs/execute/batch', { run_ids: runIds });
    return response.data;
  },

  executeBatch: async (params: {
    prompt_ids: string[];
    model_names: string[];
    include_variants?: boolean;
    bias_controls?: {
      fsp: boolean;
      granularity_demo?: boolean;
    };
    settings?: {
      temperature?: number;
      max_tokens?: number;
    };
    repeats?: number;
  }): Promise<{ results: any[]; summary: any }> => {
    const response = await api.post('/runs/execute/batch', params);
    return response.data;
  },

  executeBatchEnsemble: async (params: {
    prompt_ids: string[];
    model_names: string[];
    ensemble?: boolean;
    include_variants?: boolean;  // FIX: Add include_variants parameter
    bias_controls?: {
      fsp: boolean;
      granularity_demo?: boolean;
    };
    settings?: {
      temperature?: number;
      max_tokens?: number;
    };
    repeats?: number;
  }): Promise<{ results: any[]; summary: any; ensemble_enabled: boolean }> => {
    const response = await api.post('/runs/execute/batch-ensemble', params);
    return response.data;
  },

  addEnsembleToExperiment: async (
    experimentId: string
  ): Promise<{ message: string; results: any[]; summary: any }> => {
    const response = await api.post(`/runs/experiments/${experimentId}/ensemble-evaluate`);
    return response.data;
  },

  list: async (params: {
    model?: string;
    scenario?: string;
    status?: string;
    source?: string;
    experiment_id?: string;
    dataset_version?: string;
    page?: number;
    limit?: number;
  } = {}): Promise<{ runs: Run[]; page: number; limit: number; count: number }> => {
    const response = await api.get('/runs/', { params });
    return response.data;
  },

  get: async (runId: string): Promise<{ run: Run; output: string | null }> => {
    const response = await api.get(`/runs/${runId}`);
    return response.data;
  },

    delete: async (runId: string): Promise<{ message: string }> => {
      const response = await api.delete(`/runs/delete/${runId}`);
      return response.data;
    },

};

// Analytics API
export const analyticsApi = {
  costQualityScatter: async (): Promise<Array<{
    run_id: string;
    model: string;
    aud_cost: number;
    composite_score: number;
  }>> => {
    const response = await api.get('/analytics/cost-quality-scatter');
    return response.data;
  },

  costQuality: async (params: {
    scenario?: string;
    model?: string;
  } = {}): Promise<{ data: CostQualityPoint[] }> => {
    // Convert comma-separated model string to array for backend
    const apiParams = { ...params };
    if (apiParams.model && typeof apiParams.model === 'string') {
      apiParams.model = apiParams.model.split(',');
    }
    const response = await api.get('/analytics/cost_quality', { params: apiParams });
    return response.data;
  },

  lengthBias: async (params: {
    scenario?: string;
    model?: string;
  } = {}): Promise<{ data: LengthBiasData }> => {
    // Convert comma-separated model string to array for backend
    const apiParams = { ...params };
    if (apiParams.model && typeof apiParams.model === 'string') {
      apiParams.model = apiParams.model.split(',');
    }
    const response = await api.get('/analytics/length_bias', { params: apiParams });
    return response.data;
  },

  riskCurves: async (params: {
    scenario?: string;
    model?: string;
  } = {}): Promise<{ data: RiskCurvesData }> => {
    // Convert comma-separated model string to array for backend
    const apiParams = { ...params };
    if (apiParams.model && typeof apiParams.model === 'string') {
      apiParams.model = apiParams.model.split(',');
    }
    const response = await api.get('/analytics/risk_curves', { params: apiParams });
    return response.data;
  },

  riskCost: async (params: {
    scenario?: string;
    model?: string[];
  } = {}): Promise<any> => {
    const response = await api.get('/analytics/risk_cost', { params });
    return response.data;
  },

  bestQualityPerAud: async (params: {
    scenario?: string;
  } = {}): Promise<{ leaderboard: any[] }> => {
    const response = await api.get('/analytics/best_quality_per_aud', { params });
    return response.data;
  },

  coverage: async (): Promise<Array<{
    source: string;
    scenario: string;
    unique_prompt_count: number;
    total_runs: number;
  }>> => {
    const response = await api.get('/analytics/coverage');
    return response.data;
  },

  ensemble: async (params?: {
    scenario?: string;
    length_bin?: string;
    experiment_id?: string;
  }): Promise<any> => {
    const response = await api.get('/analytics/ensemble', { params });
    return response.data;
  },

  ensembleCorrelations: async (params?: {
    scenario?: string;
    min_evaluations?: number;
  }): Promise<any> => {
    const response = await api.get('/analytics/ensemble/correlations', { params });
    return response.data;
  },
};

// Research API
export const researchApi = {
  getScenarioStats: async (): Promise<any> => {
    const response = await api.get('/research/scenarios/stats');
    return response.data;
  },

  filterPrompts: async (params: {
    scenario?: string;
    length_bin?: string;
    category?: string;
    min_tokens?: number;
    max_tokens?: number;
    sample_size?: number;
  } = {}): Promise<any> => {
    const response = await api.get('/research/prompts/filter', { params });
    return response.data;
  },


};



// Adaptive API
export const adaptiveApi = {
  generatePrompts: async (params: {
    document_text: string;
    task_type: string;
    model?: string;
  }): Promise<{
    prompts: string[];
    task_type: string;
    count: number;
  }> => {
    const response = await api.post('/adaptive/generate', params);
    return response.data;
  },
};

// Stats API
export const statsApi = {
  overview: async (): Promise<{
    total_runs: number;
    available_prompts: number;
    total_cost_aud: number;
    avg_quality_overall: number | null;
    last_runs: Array<{
      run_id: string;
      model_id: string;
      scenario: string;
      fsp_enabled: boolean;
      overall: number | null;
      aud_cost: number;
      created_at: string;
    }>;
  }> => {
    const response = await api.get('/stats/overview');
    return response.data;
  },

  analyticsSummary: async (): Promise<{
    total_successful_runs: number;
    total_failed_runs: number;
    avg_cost_per_run: number;
    models_tested: number;
    scenarios_covered: number;
    quality_distribution: {
      excellent: number; // > 4.0
      good: number; // 3.0-4.0
      fair: number; // 2.0-3.0
      poor: number; // < 2.0
    };
    cost_efficiency: {
      model_id: string;
      avg_cost: number;
      avg_quality: number;
      efficiency_score: number;
    }[];
  }> => {
    const response = await api.get('/stats/analytics-summary');
    return response.data;
  },
};

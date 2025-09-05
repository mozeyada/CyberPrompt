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
  }): Promise<{ results: any[]; summary: any }> => {
    const response = await api.post('/runs/execute/batch', params);
    return response.data;
  },

  list: async (params: {
    model?: string;
    scenario?: string;
    status?: string;
    page?: number;
    limit?: number;
  } = {}): Promise<{ runs: Run[]; page: number; limit: number; count: number }> => {
    const response = await api.get('/runs/', { params });
    return response.data;
  },

  get: async (runId: string): Promise<{ run: Run }> => {
    const response = await api.get(`/runs/${runId}`);
    return response.data;
  },

  delete: async (runId: string): Promise<{ message: string }> => {
    const response = await api.delete(`/runs/${runId}`);
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
    const response = await api.get('/analytics/cost_quality', { params });
    return response.data;
  },

  lengthBias: async (params: {
    scenario?: string;
    model?: string;
  } = {}): Promise<{ data: LengthBiasData }> => {
    const response = await api.get('/analytics/length_bias', { params });
    return response.data;
  },

  riskCurves: async (params: {
    scenario?: string;
    model?: string;
  } = {}): Promise<{ data: RiskCurvesData }> => {
    const response = await api.get('/analytics/risk_curves', { params });
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
    min_words?: number;
    max_words?: number;
    sample_size?: number;
  } = {}): Promise<any> => {
    const response = await api.get('/research/prompts/filter', { params });
    return response.data;
  },

  promptLengthAnalysis: async (params: {
    scenario?: string;
    models?: string[];
  } = {}): Promise<any> => {
    const queryParams = new URLSearchParams();
    if (params.scenario) queryParams.append('scenario', params.scenario);
    if (params.models && params.models.length > 0) {
      queryParams.append('models', params.models.join(','));
    }
    
    const response = await api.get(`/research/rq1/prompt-length-analysis?${queryParams}`);
    return response.data;
  },

  adaptiveBenchmarkAnalysis: async (params: {
    scenario?: string;
  } = {}): Promise<any> => {
    const queryParams = new URLSearchParams();
    if (params.scenario) queryParams.append('scenario', params.scenario);
    
    const response = await api.get(`/research/rq2/adaptive-benchmarking?${queryParams}`);
    return response.data;
  },

  fspBiasAnalysis: async (params: {
    scenario?: string;
    models?: string[];
  } = {}): Promise<any> => {
    const queryParams = new URLSearchParams();
    if (params.scenario) queryParams.append('scenario', params.scenario);
    if (params.models && params.models.length > 0) {
      queryParams.append('models', params.models.join(','));
    }
    
    const response = await api.get(`/research/fsp-bias-analysis?${queryParams}`);
    return response.data;
  },

  costEfficiencyAnalysis: async (params: {
    scenario?: string;
    models?: string[];
  } = {}): Promise<any> => {
    const queryParams = new URLSearchParams();
    if (params.scenario) queryParams.append('scenario', params.scenario);
    if (params.models && params.models.length > 0) {
      queryParams.append('models', params.models.join(','));
    }
    
    const response = await api.get(`/research/cost-efficiency?${queryParams}`);
    return response.data;
  },
};

// Documents API
export const documentsApi = {
  create: async (document: {
    filename: string;
    source_type: string;
    content: string;
  }): Promise<{ doc_id: string; message: string }> => {
    const response = await api.post('/documents/', document);
    return response.data;
  },

  list: async (): Promise<Array<{
    doc_id: string;
    filename: string;
    source_type: string;
    created_at: string;
  }>> => {
    const response = await api.get('/documents/');
    return response.data;
  },

  get: async (docId: string): Promise<{
    doc_id: string;
    filename: string;
    source_type: string;
    content: string;
    created_at: string;
  }> => {
    const response = await api.get(`/documents/${docId}`);
    return response.data;
  },

  delete: async (docId: string): Promise<{ message: string }> => {
    const response = await api.delete(`/documents/${docId}`);
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

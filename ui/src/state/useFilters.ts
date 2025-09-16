import { create } from 'zustand';

export interface FilterState {
  // Model filters
  selectedModels: string[];
  setSelectedModels: (models: string[]) => void;
  
  // Scenario filter
  selectedScenario: string | null;
  setSelectedScenario: (scenario: string | null) => void;
  
  // Length bin filters
  selectedLengthBins: string[];
  setSelectedLengthBins: (lengthBins: string[]) => void;
  
  // Rubric dimension filter
  selectedDimension: string;
  setSelectedDimension: (dimension: string) => void;
  
  // Judge type filter
  selectedJudgeType: string | null;
  setSelectedJudgeType: (judgeType: string | null) => void;
  
  // Experiment state
  selectedPrompts: string[];
  setSelectedPrompts: (prompts: string[]) => void;
  includeVariants: boolean;
  setIncludeVariants: (include: boolean) => void;
  experimentConfig: {
    repeats: number;
    temperature: number;
    maxTokens: number;
    seed: number;
    fspEnabled: boolean;
    experimentName: string;
  };
  setExperimentConfig: (config: Partial<FilterState['experimentConfig']>) => void;
  
  // Validation
  validateExperiment: () => string[];
  
  // Metadata generation
  generateExperimentMetadata: () => {
    configHash: string;
    timestamp: string;
    totalRuns: number;
    estimatedCost: number;
  };
  
  // Reset all filters
  resetFilters: () => void;
}

export const useFilters = create<FilterState>((set, get) => ({
  selectedModels: [],
  setSelectedModels: (models) => set({ selectedModels: models }),
  
  selectedScenario: null,
  setSelectedScenario: (scenario) => set({ selectedScenario: scenario }),
  
  selectedLengthBins: [],
  setSelectedLengthBins: (lengthBins) => set({ selectedLengthBins: lengthBins }),
  
  selectedDimension: 'composite',
  setSelectedDimension: (dimension) => set({ selectedDimension: dimension }),
  
  selectedJudgeType: null,
  setSelectedJudgeType: (judgeType) => set({ selectedJudgeType: judgeType }),
  
  selectedPrompts: [],
  setSelectedPrompts: (prompts) => set({ selectedPrompts: prompts }),
  
  includeVariants: false,
  setIncludeVariants: (include) => set({ includeVariants: include }),
  
  experimentConfig: {
    repeats: 3,
    temperature: 0.2,
    maxTokens: 800,
    seed: 42,
    fspEnabled: false,
    experimentName: '',
  },
  setExperimentConfig: (config) => set((state) => ({
    experimentConfig: { ...state.experimentConfig, ...config }
  })),
  
  validateExperiment: () => {
    const state = get();
    const errors: string[] = [];
    
    if (state.selectedPrompts.length === 0) errors.push("No prompts selected");
    if (state.selectedModels.length === 0) errors.push("No models selected");
    if (state.selectedPrompts.some(p => !p || typeof p !== 'string')) errors.push("Invalid prompt IDs");
    if (state.selectedModels.some(m => !m || typeof m !== 'string')) errors.push("Invalid model names");
    
    return errors;
  },
  
  generateExperimentMetadata: () => {
    const state = get();
    const configString = JSON.stringify({
      prompts: state.selectedPrompts.length,
      models: state.selectedModels,
      config: state.experimentConfig
    });
    
    const promptMultiplier = state.includeVariants ? 3 : 1; // S+M+L variants
    const totalRuns = state.selectedPrompts.length * promptMultiplier * state.selectedModels.length * state.experimentConfig.repeats;
    
    return {
      configHash: btoa(configString).slice(0, 8),
      timestamp: new Date().toISOString(),
      totalRuns,
      estimatedCost: totalRuns * 0.03
    };
  },
  
  resetFilters: () => set({
    selectedModels: [],
    selectedScenario: null,
    selectedLengthBins: [],
    selectedDimension: 'composite',
    selectedJudgeType: null,
    selectedPrompts: [],
    includeVariants: false,
    experimentConfig: {
      repeats: 3,
      temperature: 0.2,
      maxTokens: 800,
      seed: 42,
      fspEnabled: false,
      experimentName: '',
    },
  }),
}));

// UI State Store
interface UIState {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  
  selectedRunId: string | null;
  setSelectedRunId: (runId: string | null) => void;
  
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const useUIState = create<UIState>((set) => ({
  isSidebarOpen: false,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setSidebarOpen: (open) => set({ isSidebarOpen: open }),
  
  selectedRunId: null,
  setSelectedRunId: (runId) => set({ selectedRunId: runId }),
  
  activeTab: 'results',
  setActiveTab: (tab) => set({ activeTab: tab }),
}));

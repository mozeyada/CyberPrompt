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
  
  // Reset all filters
  resetFilters: () => void;
}

export const useFilters = create<FilterState>((set) => ({
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
  
  resetFilters: () => set({
    selectedModels: [],
    selectedScenario: null,
    selectedLengthBins: [],
    selectedDimension: 'composite',
    selectedJudgeType: null,
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

import { useState } from 'react'

import { useFilters } from '../state/useFilters'

interface Step3Props {
  selectedPrompts: string[]
  selectedModels: string[]
  experimentConfig: {
    repeats: number
    temperature: number
    maxTokens: number
    seed: number
    fspEnabled: boolean
    experimentName: string
  }
  setExperimentConfig: (config: any) => void
  researchMode: boolean
  setResearchMode: (enabled: boolean) => void
  onRunExperiment: () => void
  isRunning: boolean
  enableEnsemble?: boolean
  setEnableEnsemble?: (enabled: boolean) => void
}

export function Step3_Configure({
  selectedPrompts,
  selectedModels,
  experimentConfig,
  setExperimentConfig,
  researchMode,
  setResearchMode,
  onRunExperiment,
  isRunning,
  enableEnsemble = false,
  setEnableEnsemble = () => {}
}: Step3Props) {
  const [showAdvanced, setShowAdvanced] = useState(false)
  const { includeVariants } = useFilters()
  
  // Account for length variants if enabled
  const promptMultiplier = includeVariants ? 3 : 1 // S+M+L variants
  const actualPromptCount = selectedPrompts.length * promptMultiplier
  const estimatedCost = actualPromptCount * selectedModels.length * experimentConfig.repeats * 0.03
  const totalRuns = actualPromptCount * selectedModels.length * experimentConfig.repeats

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Review & Run Your Test</h2>
        <p className="text-gray-600 mt-2">Final configuration and execution</p>
      </div>

      {/* Summary Box */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">📋 Test Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="font-medium text-blue-900">Selected Prompts</p>
            <p className="text-blue-700">
              {selectedPrompts.length} security scenarios
              {promptMultiplier > 1 && (
                <span className="text-xs block text-blue-600">× {promptMultiplier} variants = {actualPromptCount} total</span>
              )}
            </p>
          </div>
          <div>
            <p className="font-medium text-blue-900">AI Models</p>
            <p className="text-blue-700">{selectedModels.join(', ')}</p>
          </div>
          <div>
            <p className="font-medium text-blue-900">Total Tests</p>
            <p className="text-blue-700">{totalRuns} runs</p>
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6 space-y-6">
        {/* Basic Configuration */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Test Name
            </label>
            <input
              type="text"
              value={experimentConfig.experimentName}
              onChange={(e) => setExperimentConfig({ experimentName: e.target.value })}
              placeholder="SOC Incident Response Test - Dec 2024"
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Test Repetitions
            </label>
            <select
              value={experimentConfig.repeats}
              onChange={(e) => setExperimentConfig({ repeats: parseInt(e.target.value) })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value={1}>1 run (quick test)</option>
              <option value={3}>3 runs (recommended)</option>
              <option value={5}>5 runs (high confidence)</option>
            </select>
          </div>
        </div>

        {/* Bias Controls */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3">🎯 Bias Controls</h4>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={experimentConfig.fspEnabled}
                onChange={(e) => setExperimentConfig({ fspEnabled: e.target.checked })}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">
                Enable Fair Scoring (prevents bias toward longer responses)
              </span>
            </label>
            
            {includeVariants && (
              <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                <div className="flex items-center text-yellow-800">
                  <span className="mr-2">⚠️</span>
                  <span className="text-sm font-medium">
                    Length variants enabled: Each selected prompt will include S+M+L versions (×3 multiplier)
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Advanced Settings Accordion */}
        <div className="border border-gray-200 rounded-lg">
          {/* Ensemble Evaluation - Always Visible */}
          <div className="px-4 pb-4 border-b border-gray-200">
            <div>
              <label className="flex items-center mb-3">
                <input
                  type="checkbox"
                  checked={enableEnsemble}
                  onChange={(e) => setEnableEnsemble(e.target.checked)}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">
                  🧠 Ensemble Evaluation (Multi-Judge)
                </span>
              </label>
              <div className="ml-6 text-xs text-gray-500 mb-3">
                Uses GPT-4o-mini, Claude-3.5-Sonnet, and Llama-3.1-70B for enhanced reliability
              </div>
            </div>
          </div>

          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-gray-50"
          >
            <span className="font-medium text-gray-900">⚙️ Advanced Settings</span>
            <span className="text-gray-500">{showAdvanced ? '−' : '+'}</span>
          </button>
          
          {showAdvanced && (
            <div className="px-4 pb-4 border-t border-gray-200 space-y-4">
              <div>
                <label className="flex items-center mb-3">
                  <input
                    type="checkbox"
                    checked={researchMode}
                    onChange={(e) => setResearchMode(e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700">
                    Research/Advanced Mode
                  </span>
                </label>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Response Length Limit
                  </label>
                  <input
                    type="number"
                    value={experimentConfig.maxTokens}
                    onChange={(e) => setExperimentConfig({ maxTokens: parseInt(e.target.value) })}
                    min="100"
                    max="4000"
                    step="100"
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                
                {researchMode && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Temperature
                      </label>
                      <input
                        type="number"
                        value={experimentConfig.temperature}
                        onChange={(e) => setExperimentConfig({ temperature: parseFloat(e.target.value) })}
                        min="0"
                        max="1"
                        step="0.1"
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Seed
                      </label>
                      <input
                        type="number"
                        value={experimentConfig.seed}
                        onChange={(e) => setExperimentConfig({ seed: parseInt(e.target.value) })}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Final Action */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Ready to Run</h3>
            <p className="text-sm text-gray-600">
              {totalRuns} total tests • Est. time: ~{Math.ceil(totalRuns / 10)} minutes
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-600">Estimated Cost</div>
            <div className="text-2xl font-bold text-blue-600">${estimatedCost.toFixed(2)} AUD</div>
          </div>
        </div>
        
        <button
          onClick={onRunExperiment}
          disabled={isRunning}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-6 py-4 rounded-md font-medium text-lg"
        >
          {isRunning ? 'Running Experiment...' : `🚀 Run Experiment (${totalRuns} tests)`}
        </button>
      </div>
    </div>
  )
}
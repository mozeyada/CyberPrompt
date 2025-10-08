import { useState, useEffect, useRef } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { runsApi } from '../api/client'
import { useFilters } from '../state/useFilters'
import { Step1_Scenarios } from '../components/Step1_Scenarios'
import { Step2_Models } from '../components/Step2_Models'
import { Step3_Configure } from '../components/Step3_Configure'
import { AdaptivePrompting } from './AdaptivePrompting'

export function BenchmarkRunner() {
  const [searchParams] = useSearchParams()
  const [activeTab, setActiveTab] = useState<'standard' | 'adaptive'>('standard')
  const [currentStep, setCurrentStep] = useState(1)
  const [promptSource, setPromptSource] = useState<'static' | 'adaptive'>('static')
  const [lengthBin, setLengthBin] = useState('')
  const [researchMode, setResearchMode] = useState(false)
  const [enableEnsemble, setEnableEnsemble] = useState(true)

  useEffect(() => {
    const tab = searchParams.get('tab')
    if (tab === 'adaptive') {
      setActiveTab('adaptive')
    }
  }, [searchParams])
  
  const {
    selectedPrompts,
    setSelectedPrompts,
    selectedModels,
    setSelectedModels,
    includeVariants,
    experimentConfig,
    setExperimentConfig,
    validateExperiment,
    generateExperimentMetadata
  } = useFilters()
  const [executionStatus, setExecutionStatus] = useState<{
    isRunning: boolean
    totalRuns: number
    completedRuns: number
    failedRuns: number
    currentRun: number
    logs: Array<{id: string, message: string, type: 'info' | 'success' | 'error', timestamp: string}>
    results: Array<{run_id: string, status: string, model: string, cost?: number, quality?: number, error?: string}>
  }>({
    isRunning: false,
    totalRuns: 0,
    completedRuns: 0,
    failedRuns: 0,
    currentRun: 0,
    logs: [],
    results: []
  })

  const addLog = (message: string, type: 'info' | 'success' | 'error' = 'info') => {
    const log = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      message,
      type,
      timestamp: new Date().toLocaleTimeString()
    }
    setExecutionStatus(prev => ({
      ...prev,
      logs: [...prev.logs, log].slice(-50)
    }))
  }

  const executeBatchMutation = useMutation({
    mutationFn: runsApi.executeBatch,
    onSuccess: (data) => {
      const results = data.results.map((result: any) => ({
        run_id: result.run_id,
        status: result.status,
        model: result.model || 'unknown',
        cost: result.economics?.aud_cost,
        quality: result.scores?.composite,
        error: result.error
      }))
      
      const successCount = results.filter((r: any) => r.status === 'succeeded').length
      const failCount = results.filter((r: any) => r.status === 'failed').length
      
      // Clear progress simulation interval
      if ((window as any).currentProgressInterval) {
        clearInterval((window as any).currentProgressInterval)
        delete (window as any).currentProgressInterval
      }
      
      setExecutionStatus(prev => ({
        ...prev,
        isRunning: false,
        completedRuns: successCount,
        failedRuns: failCount,
        currentRun: prev.totalRuns, // Mark as completed
        results
      }))
      
      addLog(`Completed: ${successCount} successful, ${failCount} failed`, successCount > 0 ? 'success' : 'error')
      
      // Log specific errors for failed runs
      results.filter(r => r.status === 'failed').forEach(result => {
        addLog(`Failed run ${result.run_id}: ${result.error || 'Unknown error'}`, 'error')
      })
      
      if (successCount > 0) {
        const totalCost = results.reduce((sum: number, r: any) => sum + (r.cost || 0), 0)
        addLog(`Total cost: $${totalCost.toFixed(4)} AUD`, 'info')
      }
    },
    onError: (error) => {
      addLog(`Experiment failed: ${error}`, 'error')
      setExecutionStatus(prev => ({ ...prev, isRunning: false }))
    }
  })

  const executeEnsembleMutation = useMutation({
    mutationFn: runsApi.executeBatchEnsemble,
    onSuccess: (data) => {
      const results = data.results.map((result: any) => ({
        run_id: result.run_id,
        status: result.status,
        model: result.model || 'unknown',
        cost: result.economics?.aud_cost,
        quality: result.ensemble_evaluation?.aggregated?.mean_scores?.composite || result.scores?.composite,
        error: result.error,
        ensembleEnabled: !!result.ensemble_evaluation
      }))
      
      const successCount = results.filter((r: any) => r.status === 'succeeded').length
      const failCount = results.filter((r: any) => r.status === 'failed').length
      
      // Clear progress simulation interval
      if ((window as any).currentProgressInterval) {
        clearInterval((window as any).currentProgressInterval)
        delete (window as any).currentProgressInterval
      }
      
      setExecutionStatus(prev => ({
        ...prev,
        isRunning: false,
        completedRuns: successCount,
        failedRuns: failCount,
        currentRun: prev.totalRuns, // Mark as completed
        results
      }))
      
      addLog(`Completed: ${successCount} successful, ${failCount} failed`, successCount > 0 ? 'success' : 'error')
      addLog(`Ensemble evaluation: ${data.ensemble_enabled ? 'enabled' : 'disabled'}`, 'info')
      
      // Log specific errors for failed runs
      results.filter(r => r.status === 'failed').forEach(result => {
        addLog(`Failed run ${result.run_id}: ${result.error || 'Unknown error'}`, 'error')
      })
      
      if (successCount > 0) {
        const totalCost = results.reduce((sum: number, r: any) => sum + (r.cost || 0), 0)
        addLog(`Total cost: $${totalCost.toFixed(4)} AUD`, 'info')
      }
    },
    onError: (error) => {
      addLog(`Ensemble experiment failed: ${error}`, 'error')
      setExecutionStatus(prev => ({ ...prev, isRunning: false }))
    }
  })

  const handleRunExperiment = () => {
    console.log('handleRunExperiment called with:', { selectedPrompts, selectedModels })
    
    // Validate experiment configuration
    const errors = validateExperiment()
    if (errors.length > 0) {
      errors.forEach(error => addLog(error, 'error'))
      return
    }
    
    // Validate prompt IDs are not empty or invalid
    const validPromptIds = selectedPrompts.filter(id => id && typeof id === 'string' && id.trim().length > 0)
    if (validPromptIds.length === 0) {
      addLog('No valid prompt IDs selected. Please select prompts first.', 'error')
      return
    }
    if (validPromptIds.length !== selectedPrompts.length) {
      addLog(`Warning: ${selectedPrompts.length - validPromptIds.length} invalid prompt IDs were filtered out`, 'error')
    }

    const promptMultiplier = includeVariants ? 3 : 1 // S+M+L variants
    const totalRuns = validPromptIds.length * promptMultiplier * selectedModels.length * experimentConfig.repeats
    
    setExecutionStatus({
      isRunning: true,
      totalRuns,
      completedRuns: 0,
      failedRuns: 0,
      currentRun: 0,
      logs: [],
      results: []
    })
    
    // Generate experiment metadata for reproducibility
    const metadata = generateExperimentMetadata()
    
    addLog(`Starting experiment with ${totalRuns} runs...`, 'info')
    
    // Simulate progress updates (since backend doesn't provide real-time progress)
    let simulatedProgress = 0
    const progressInterval = setInterval(() => {
      simulatedProgress++
      if (simulatedProgress <= totalRuns) {
        setExecutionStatus(prev => ({
          ...prev,
          currentRun: simulatedProgress
        }))
      } else {
        clearInterval(progressInterval)
      }
    }, 1000) // Update every second
    
    // Store interval reference to clear it when mutation completes
    ;(window as any).currentProgressInterval = progressInterval
    addLog(`Config: ${experimentConfig.repeats} repeats, seed ${experimentConfig.seed}`, 'info')
    addLog(`Metadata: Hash ${metadata.configHash}, Cost ~$${metadata.estimatedCost.toFixed(4)}`, 'info')
    
    const mutation = enableEnsemble ? executeEnsembleMutation : executeBatchMutation
    
    if (enableEnsemble) {
      executeEnsembleMutation.mutate({
        prompt_ids: validPromptIds,
        model_names: selectedModels,
        ensemble: enableEnsemble,
        include_variants: includeVariants,  // FIX: Add include_variants parameter
        bias_controls: {
          fsp: experimentConfig.fspEnabled,
          granularity_demo: false
        },
        settings: {
          temperature: experimentConfig.temperature,
          max_output_tokens: experimentConfig.maxTokens,
        },
        repeats: experimentConfig.repeats
      })
    } else {
      executeBatchMutation.mutate({
        prompt_ids: validPromptIds,
        model_names: selectedModels,
        include_variants: includeVariants,
        bias_controls: {
          fsp: experimentConfig.fspEnabled,
          granularity_demo: false
        },
        settings: {
          temperature: experimentConfig.temperature,
          max_output_tokens: experimentConfig.maxTokens,
        },
        repeats: experimentConfig.repeats
      })
    }
  }

  const canGoNext = () => {
    if (currentStep === 1) return selectedPrompts.length > 0
    if (currentStep === 2) return selectedModels.length > 0
    return true
  }

  const nextStep = () => {
    if (canGoNext() && currentStep < 3) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <Step1_Scenarios
            lengthBin={lengthBin}
            setLengthBin={setLengthBin}
          />
        )
      case 2:
        return (
          <Step2_Models
            selectedModels={selectedModels}
            setSelectedModels={setSelectedModels}
          />
        )
      case 3:
        return (
          <Step3_Configure
            selectedPrompts={selectedPrompts}
            selectedModels={selectedModels}
            experimentConfig={experimentConfig}
            setExperimentConfig={setExperimentConfig}
            researchMode={researchMode}
            setResearchMode={setResearchMode}
            onRunExperiment={handleRunExperiment}
            isRunning={executionStatus.isRunning}
            enableEnsemble={enableEnsemble}
            setEnableEnsemble={setEnableEnsemble}
          />
        )
      default:
        return null
    }
  }

  const tabs = [
    { id: 'standard', name: 'RQ1: Standard Experiments', desc: 'Prompt length analysis', color: 'blue' },
    { id: 'adaptive', name: 'RQ2: Adaptive Experiments', desc: 'Adaptive vs static benchmarking', color: 'green' }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Experiments</h1>
        <p className="text-gray-600">Run research experiments and generate adaptive prompts</p>
      </div>

      {/* Tab Navigation */}
      <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-6">
        <div className="flex justify-center space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as 'standard' | 'adaptive')}
              className={`px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 ${
                activeTab === tab.id
                  ? (tab.color === 'blue' 
                      ? 'bg-blue-600 text-white shadow-lg transform scale-105' 
                      : 'bg-green-600 text-white shadow-lg transform scale-105')
                  : (tab.color === 'blue'
                      ? 'bg-white text-blue-600 border-2 border-blue-200 hover:border-blue-400 hover:bg-blue-50'
                      : 'bg-white text-green-600 border-2 border-green-200 hover:border-green-400 hover:bg-green-50')
              }`}
            >
              <div className="text-center">
                <div className="font-bold">{tab.name}</div>
                <div className={`text-sm mt-1 ${
                  activeTab === tab.id 
                    ? 'text-white opacity-90' 
                    : (tab.color === 'blue' ? 'text-blue-500' : 'text-green-500')
                }`}>
                  {tab.desc}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'standard' && (
        <div className="space-y-6">
          <div className="border-b border-gray-200 pb-4">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-blue-900">RQ1: Standard Experiments</h2>
              <p className="mt-3 text-lg text-blue-700">
                Systematic evaluation of prompt length effects on LLM performance
              </p>
              <div className="mt-4 bg-blue-50 rounded-lg p-4 inline-block">
                <div className="text-sm text-blue-600 font-medium">
                  Research Focus: Cost-Quality Trade-offs • Length Bias Analysis • FSP Validation
                </div>
              </div>
            </div>
        
            {/* Progress Stepper */}
            <div className="mt-6 flex items-center justify-center">
              <div className="flex items-center space-x-4">
                {[1, 2, 3].map((step) => (
                  <div key={step} className="flex items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                      step === currentStep
                        ? 'bg-blue-600 text-white'
                        : step < currentStep
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-300 text-gray-600'
                    }`}>
                      {step < currentStep ? '✓' : step}
                    </div>
                    {step < 3 && (
                      <div className={`w-16 h-0.5 mx-2 ${
                        step < currentStep ? 'bg-green-500' : 'bg-gray-300'
                      }`}></div>
                    )}
                  </div>
                ))}
              </div>
            </div>
        
            <div className="mt-4 flex justify-center space-x-8 text-sm">
              <span className={currentStep === 1 ? 'text-blue-600 font-medium' : 'text-gray-500'}>
                1. Choose Scenarios
              </span>
              <span className={currentStep === 2 ? 'text-blue-600 font-medium' : 'text-gray-500'}>
                2. Select Models
              </span>
              <span className={currentStep === 3 ? 'text-blue-600 font-medium' : 'text-gray-500'}>
                3. Configure & Run
              </span>
            </div>
          </div>

          {/* Current Step Content */}
          <div className="min-h-[600px]">
            {renderCurrentStep()}
          </div>

          {/* Navigation Buttons */}
          <div className="flex justify-between items-center pt-6 border-t border-gray-200">
            <button
              onClick={prevStep}
              disabled={currentStep === 1}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ← Back
            </button>
        
            <div className="text-sm text-gray-500">
              Step {currentStep} of 3
            </div>
        
            {currentStep < 3 ? (
              <button
                onClick={nextStep}
                disabled={!canGoNext()}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next →
              </button>
            ) : (
              <div className="w-20"></div>
            )}
          </div>

          {/* Real-time Execution Dashboard */}
          {(executionStatus.isRunning || executionStatus.logs.length > 0) && (
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Test Execution Status</h3>
                {executionStatus.isRunning && (
                  <div className="flex items-center text-blue-600">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                    Processing run {executionStatus.currentRun + 1} of {executionStatus.totalRuns}...
                  </div>
                )}
              </div>
          
              {/* Enhanced Progress Bar */}
              {executionStatus.totalRuns > 0 && (
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Progress: {executionStatus.completedRuns + executionStatus.failedRuns} / {executionStatus.totalRuns}</span>
                    <span>{Math.round(((executionStatus.completedRuns + executionStatus.failedRuns) / executionStatus.totalRuns) * 100)}%</span>
                  </div>
                  
                  {/* Vintage-style Loading Bar */}
                  <div className="relative w-full bg-gray-800 rounded-none h-6 border-2 border-gray-600 mb-2">
                    <div 
                      className="bg-gradient-to-r from-green-400 to-blue-500 h-full transition-all duration-500 ease-out relative"
                      style={{ width: `${((executionStatus.completedRuns + executionStatus.failedRuns) / executionStatus.totalRuns) * 100}%` }}
                    >
                      {/* Retro scan lines effect */}
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-20 animate-pulse"></div>
                      
                      {/* Progress text overlay */}
                      <div className="absolute inset-0 flex items-center justify-center text-white font-bold text-xs">
                        {executionStatus.isRunning ? `${executionStatus.completedRuns + executionStatus.failedRuns}/${executionStatus.totalRuns}` : 'COMPLETE'}
                      </div>
                    </div>
                    
                    {/* Loading indicator when running */}
                    {executionStatus.isRunning && (
                      <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
                        <div className="flex space-x-1">
                          <div className="w-1 h-3 bg-white animate-pulse"></div>
                          <div className="w-1 h-3 bg-white animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                          <div className="w-1 h-3 bg-white animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex justify-between text-xs text-gray-500">
                    <span className="text-green-600">✓ {executionStatus.completedRuns} successful</span>
                    <span className="text-red-600">✗ {executionStatus.failedRuns} failed</span>
                    <span className="text-blue-600">⏳ {executionStatus.totalRuns - (executionStatus.completedRuns + executionStatus.failedRuns)} pending</span>
                  </div>
                </div>
              )}
          
              {/* Live Logs */}
              <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                <h4 className="font-medium text-gray-900 mb-2">Execution Log</h4>
                <div className="space-y-1 font-mono text-sm">
                  {executionStatus.logs.map(log => (
                    <div key={log.id} className={`flex items-start space-x-2 ${
                      log.type === 'error' ? 'text-red-600' :
                      log.type === 'success' ? 'text-green-600' :
                      'text-gray-600'
                    }`}>
                      <span className="text-gray-400 text-xs">{log.timestamp}</span>
                      <span className={`${
                        log.type === 'error' ? 'text-red-500' :
                        log.type === 'success' ? 'text-green-500' :
                        'text-blue-500'
                      }`}>
                        {log.type === 'error' ? '✗' : log.type === 'success' ? '✓' : 'ℹ'}
                      </span>
                      <span>{log.message}</span>
                    </div>
                  ))}
                  {executionStatus.logs.length === 0 && (
                    <div className="text-gray-400 text-center py-4">No logs yet...</div>
                  )}
                </div>
              </div>
          
              {/* Results Summary */}
              {executionStatus.results.length > 0 && (
                <div className="mt-4">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium text-gray-900">Test Results</h4>
                    {!executionStatus.isRunning && executionStatus.completedRuns > 0 && (
                      <a 
                        href={`/results?experiment=${executionStatus.results[0]?.run_id?.split('_')[0] || 'latest'}`}
                        className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 text-sm font-medium"
                      >
                        View RQ1 Results →
                      </a>
                    )}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {executionStatus.results.map(result => (
                      <div key={result.run_id} className={`p-3 rounded-lg border ${
                        result.status === 'succeeded' ? 'bg-green-50 border-green-200' :
                        result.status === 'failed' ? 'bg-red-50 border-red-200' :
                        'bg-gray-50 border-gray-200'
                      }`}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium text-sm">{result.model}</span>
                          <span className={`text-xs px-2 py-1 rounded ${
                            result.status === 'succeeded' ? 'bg-green-100 text-green-800' :
                            result.status === 'failed' ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {result.status}
                          </span>
                        </div>
                        {result.status === 'succeeded' && (
                          <div className="text-xs text-gray-600">
                            {result.quality && <div>Quality: {result.quality.toFixed(1)}/5.0</div>}
                            {result.cost && <div>Cost: ${result.cost.toFixed(4)} AUD</div>}
                          </div>
                        )}
                        {result.status === 'failed' && result.error && (
                          <div className="text-xs text-red-600 mt-1">
                            Error: {result.error}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Adaptive Tab */}
      {activeTab === 'adaptive' && (
        <AdaptivePrompting />
      )}
    </div>
  )
}
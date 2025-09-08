import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { runsApi } from '../api/client'
import { useFilters } from '../state/useFilters'
import { Step1_Scenarios } from '../components/Step1_Scenarios'
import { Step2_Models } from '../components/Step2_Models'
import { Step3_Configure } from '../components/Step3_Configure'

export function BenchmarkRunner() {
  const [currentStep, setCurrentStep] = useState(1)
  const [promptSource, setPromptSource] = useState<'static' | 'adaptive'>('static')
  const [lengthBin, setLengthBin] = useState('')
  const [researchMode, setResearchMode] = useState(false)
  
  const {
    selectedPrompts,
    setSelectedPrompts,
    selectedModels,
    setSelectedModels,
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
    logs: Array<{id: string, message: string, type: 'info' | 'success' | 'error', timestamp: string}>
    results: Array<{run_id: string, status: string, model: string, cost?: number, quality?: number}>
  }>({
    isRunning: false,
    totalRuns: 0,
    completedRuns: 0,
    failedRuns: 0,
    logs: [],
    results: []
  })

  const addLog = (message: string, type: 'info' | 'success' | 'error' = 'info') => {
    const log = {
      id: Date.now().toString(),
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
        quality: result.scores?.composite
      }))
      
      const successCount = results.filter((r: any) => r.status === 'succeeded').length
      const failCount = results.filter((r: any) => r.status === 'failed').length
      
      setExecutionStatus(prev => ({
        ...prev,
        isRunning: false,
        completedRuns: successCount,
        failedRuns: failCount,
        results
      }))
      
      addLog(`Completed: ${successCount} successful, ${failCount} failed`, successCount > 0 ? 'success' : 'error')
      
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

  const handleRunExperiment = () => {
    console.log('handleRunExperiment called with:', { selectedPrompts, selectedModels })
    
    // Validate experiment configuration
    const errors = validateExperiment()
    if (errors.length > 0) {
      errors.forEach(error => addLog(error, 'error'))
      return
    }

    const totalRuns = selectedPrompts.length * selectedModels.length * experimentConfig.repeats
    
    setExecutionStatus({
      isRunning: true,
      totalRuns,
      completedRuns: 0,
      failedRuns: 0,
      logs: [],
      results: []
    })
    
    // Generate experiment metadata for reproducibility
    const metadata = generateExperimentMetadata()
    
    addLog(`Starting experiment with ${totalRuns} runs...`, 'info')
    addLog(`Config: ${experimentConfig.repeats} repeats, seed ${experimentConfig.seed}`, 'info')
    addLog(`Metadata: Hash ${metadata.configHash}, Cost ~$${metadata.estimatedCost.toFixed(4)}`, 'info')
    
    executeBatchMutation.mutate({
      prompt_ids: selectedPrompts,
      model_names: selectedModels,
      bias_controls: {
        fsp: experimentConfig.fspEnabled,
        granularity_demo: false
      },
      settings: {
        temperature: experimentConfig.temperature,
        max_tokens: experimentConfig.maxTokens
      },
      repeats: experimentConfig.repeats
    })
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
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Prompt Source</h3>
              <div className="flex gap-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="static"
                    checked={promptSource === 'static'}
                    onChange={(e) => setPromptSource(e.target.value as 'static')}
                    className="mr-2"
                  />
                  Static Prompts
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="adaptive"
                    checked={promptSource === 'adaptive'}
                    onChange={(e) => setPromptSource(e.target.value as 'adaptive')}
                    className="mr-2"
                  />
                  Adaptive Prompts
                </label>
              </div>
            </div>
            <Step1_Scenarios
              lengthBin={lengthBin}
              setLengthBin={setLengthBin}
            />
          </div>
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
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-bold text-gray-900">Benchmark Runner</h1>
        <p className="mt-2 text-gray-600">
          Compare AI models for your security operations
        </p>
        
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
                Running tests...
              </div>
            )}
          </div>
          
          {/* Progress Bar */}
          {executionStatus.totalRuns > 0 && (
            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Progress: {executionStatus.completedRuns + executionStatus.failedRuns} / {executionStatus.totalRuns}</span>
                <span>{Math.round(((executionStatus.completedRuns + executionStatus.failedRuns) / executionStatus.totalRuns) * 100)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${((executionStatus.completedRuns + executionStatus.failedRuns) / executionStatus.totalRuns) * 100}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span className="text-green-600">✓ {executionStatus.completedRuns} successful</span>
                <span className="text-red-600">✗ {executionStatus.failedRuns} failed</span>
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
              <h4 className="font-medium text-gray-900 mb-2">Test Results</h4>
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
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
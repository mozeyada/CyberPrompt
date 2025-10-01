import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Badge } from '../components/ui/badge'
import { runsApi, statsApi } from '../api/client'
import { useFilters } from '../state/useFilters'
import { Step1_Scenarios } from '../components/Step1_Scenarios'
import { Step2_Models } from '../components/Step2_Models'
import { Step3_Configure } from '../components/Step3_Configure'
import { Overview } from './Overview'

export function RQ1Flow() {
  const [currentStep, setCurrentStep] = useState<'intro' | 'demo' | 'experiment' | 'results'>('intro')
  const [experimentStep, setExperimentStep] = useState(1)
  const [lengthBin, setLengthBin] = useState('')
  const [researchMode, setResearchMode] = useState(false)
  
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
    logs: Array<{id: string, message: string, type: 'info' | 'success' | 'error', timestamp: string}>
    results: Array<{run_id: string, experiment_id?: string, status: string, model: string, cost?: number, quality?: number, error?: string}>
  }>({
    isRunning: false,
    totalRuns: 0,
    completedRuns: 0,
    failedRuns: 0,
    logs: [],
    results: []
  })
  
  // Use EXISTING API calls
  const { data: stats } = useQuery({
    queryKey: ['stats-overview'], 
    queryFn: statsApi.overview
  })

  const { data: costQualityData } = useQuery({
    queryKey: ['cost-quality'],
    queryFn: () => analyticsApi.costQuality()
  })

  const { data: lengthBiasData } = useQuery({
    queryKey: ['length-bias'],
    queryFn: () => analyticsApi.lengthBias()
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
        experiment_id: result.experiment_id,
        status: result.status,
        model: result.model || 'unknown',
        cost: result.economics?.aud_cost,
        quality: result.scores?.composite,
        error: result.error
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
      
      results.filter(r => r.status === 'failed').forEach(result => {
        addLog(`Failed run ${result.run_id}: ${result.error || 'Unknown error'}`, 'error')
      })
      
      if (successCount > 0) {
        const totalCost = results.reduce((sum: number, r: any) => sum + (r.cost || 0), 0)
        addLog(`Total cost: $${totalCost.toFixed(4)} AUD`, 'info')
        // Auto-advance to results after successful completion
        setTimeout(() => setCurrentStep('results'), 2000)
      }
    },
    onError: (error) => {
      addLog(`Experiment failed: ${error}`, 'error')
      setExecutionStatus(prev => ({ ...prev, isRunning: false }))
    }
  })

  const handleRunExperiment = () => {
    const errors = validateExperiment()
    if (errors.length > 0) {
      errors.forEach(error => addLog(error, 'error'))
      return
    }
    
    const validPromptIds = selectedPrompts.filter(id => id && typeof id === 'string' && id.trim().length > 0)
    if (validPromptIds.length === 0) {
      addLog('No valid prompt IDs selected. Please select prompts first.', 'error')
      return
    }

    const promptMultiplier = includeVariants ? 3 : 1
    const totalRuns = validPromptIds.length * promptMultiplier * selectedModels.length * experimentConfig.repeats
    
    setExecutionStatus({
      isRunning: true,
      totalRuns,
      completedRuns: 0,
      failedRuns: 0,
      logs: [],
      results: []
    })
    
    const metadata = generateExperimentMetadata()
    
    addLog(`Starting RQ1 experiment with ${totalRuns} runs...`, 'info')
    addLog(`Config: ${experimentConfig.repeats} repeats, seed ${experimentConfig.seed}`, 'info')
    addLog(`Metadata: Hash ${metadata.configHash}, Cost ~$${metadata.estimatedCost.toFixed(4)}`, 'info')
    
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
        max_tokens: experimentConfig.maxTokens
      },
      repeats: experimentConfig.repeats
    })
  }

  const nextStep = () => {
    if (currentStep === 'intro') {
      setCurrentStep('demo')
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
    else if (currentStep === 'demo') {
      setCurrentStep('experiment')
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
    else if (currentStep === 'experiment') {
      if (experimentStep < 3) {
        setExperimentStep(experimentStep + 1)
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } else if (executionStatus.completedRuns > 0) {
        setCurrentStep('results')
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    } else if (currentStep === 'results') {
      window.location.href = '/insights'
    }
  }

  const prevStep = () => {
    if (currentStep === 'demo') {
      setCurrentStep('intro')
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
    else if (currentStep === 'experiment') {
      if (experimentStep > 1) {
        setExperimentStep(experimentStep - 1)
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } else {
        setCurrentStep('demo')
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    } else if (currentStep === 'results') {
      setCurrentStep('experiment')
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  const canGoNext = () => {
    if (currentStep !== 'experiment') return true
    if (experimentStep === 1) return selectedPrompts.length > 0
    if (experimentStep === 2) return selectedModels.length > 0
    return true
  }

  const renderExperimentStep = () => {
    switch (experimentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Prompt Source</h3>
              <div className="flex gap-4">
                <label className="flex items-center">
                  <input type="radio" value="static" checked className="mr-2" readOnly />
                  Static Prompts (RQ1 Focus)
                </label>
              </div>
            </div>
            <Step1_Scenarios lengthBin={lengthBin} setLengthBin={setLengthBin} />
          </div>
        )
      case 2:
        return <Step2_Models selectedModels={selectedModels} setSelectedModels={setSelectedModels} />
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

  const renderExperiment = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Run RQ1 Experiment</h2>
        <p className="text-lg text-gray-600">Configure and execute your prompt length analysis</p>
      </div>

      {/* Progress Stepper */}
      <div className="flex items-center justify-center">
        <div className="flex items-center space-x-4">
          {[1, 2, 3].map((step) => (
            <div key={step} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step === experimentStep
                  ? 'bg-blue-600 text-white'
                  : step < experimentStep
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-300 text-gray-600'
              }`}>
                {step < experimentStep ? '✓' : step}
              </div>
              {step < 3 && (
                <div className={`w-16 h-0.5 mx-2 ${
                  step < experimentStep ? 'bg-green-500' : 'bg-gray-300'
                }`}></div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-center space-x-8 text-sm">
        <span className={experimentStep === 1 ? 'text-blue-600 font-medium' : 'text-gray-500'}>
          1. Choose Scenarios
        </span>
        <span className={experimentStep === 2 ? 'text-blue-600 font-medium' : 'text-gray-500'}>
          2. Select Models
        </span>
        <span className={experimentStep === 3 ? 'text-blue-600 font-medium' : 'text-gray-500'}>
          3. Configure & Run
        </span>
      </div>

      {/* Current Step Content */}
      <div className="min-h-[400px]">
        {renderExperimentStep()}
      </div>

      {/* Execution Status */}
      {(executionStatus.isRunning || executionStatus.logs.length > 0) && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">RQ1 Experiment Status</h3>
            {executionStatus.isRunning && (
              <div className="flex items-center text-blue-600">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                Running experiment...
              </div>
            )}
          </div>

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
            </div>
          )}

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
            </div>
          </div>
        </div>
      )}
    </div>
  )

  const renderIntro = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          RQ1: Prompt Length Effects
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          How does prompt length influence LLM cost-quality trade-offs in SOC/GRC tasks?
        </p>
      </div>

      <div className="bg-blue-50 rounded-lg p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Research Question</h2>
        <p className="text-gray-700 mb-4">
          Organizations need to understand whether longer, more detailed prompts provide better 
          security analysis results, or if concise prompts are more cost-effective for routine SOC operations.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded p-4 text-center">
            <div className="text-2xl font-bold text-green-600">100</div>
            <div className="text-sm text-gray-600">Tactical (268-362 tokens)</div>
            <Badge variant="outline" className="mt-2">S</Badge>
          </div>
          <div className="bg-white rounded p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">100</div>
            <div className="text-sm text-gray-600">Analytical (379-485 tokens)</div>
            <Badge variant="outline" className="mt-2">M</Badge>
          </div>
          <div className="bg-white rounded p-4 text-center">
            <div className="text-2xl font-bold text-red-600">100</div>
            <div className="text-sm text-gray-600">Strategic (616-721 tokens)</div>
            <Badge variant="outline" className="mt-2">L</Badge>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-3">FSP Bias Mitigation</h3>
          <p className="text-gray-600 mb-4">
            Focus Sentence Prompting prevents verbosity bias in LLM evaluation, 
            ensuring fair comparison across prompt lengths.
          </p>
          <Badge className="bg-green-100 text-green-800">Length-Invariant Scoring</Badge>
        </div>
        <div className="border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-3">Controlled Study Design</h3>
          <p className="text-gray-600 mb-4">
            Each original prompt has corresponding medium and long variants, 
            enabling systematic analysis of length effects.
          </p>
          <Badge className="bg-blue-100 text-blue-800">952 Research Prompts</Badge>
        </div>
      </div>
    </div>
  )

  const renderDemo = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          RQ1 Demonstration
        </h2>
        <p className="text-lg text-gray-600">
          Quick overview of prompt length effects on cost and quality
        </p>
      </div>

      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4">Key Findings Preview</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded p-4">
            <div className="text-lg font-bold text-green-600">Short Prompts</div>
            <div className="text-sm text-gray-600 mt-2">
              • Lowest cost per token<br/>
              • Fast execution<br/>
              • May lack context
            </div>
          </div>
          <div className="bg-white rounded p-4">
            <div className="text-lg font-bold text-blue-600">Medium Prompts</div>
            <div className="text-sm text-gray-600 mt-2">
              • Balanced cost-quality<br/>
              • SOC context included<br/>
              • Optimal for most tasks
            </div>
          </div>
          <div className="bg-white rounded p-4">
            <div className="text-lg font-bold text-red-600">Long Prompts</div>
            <div className="text-sm text-gray-600 mt-2">
              • Highest quality scores<br/>
              • Comprehensive analysis<br/>
              • Higher token costs
            </div>
          </div>
        </div>
      </div>

      <div className="text-center">
        <p className="text-gray-600 mb-6">
          Ready to run your own RQ1 experiment with controlled prompt length variants?
        </p>
        <p className="text-sm text-gray-500">
          Click "Next" below to proceed to the experiment configuration.
        </p>
      </div>
    </div>
  )

  // Get experiment ID from results
  const experimentId = executionStatus.results.find(r => r.experiment_id)?.experiment_id

  const renderResults = () => {
    // If no experiment_id from API, show all recent results
    const effectiveExperimentId = experimentId || null
    
    return (
      <div>
        <div className="mb-4 text-center">
          <div className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
            {effectiveExperimentId ? `Experiment ${effectiveExperimentId} Results` : 'Latest Experiment Results'}
          </div>
        </div>
        <Overview experimentId={effectiveExperimentId} />
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Progress Indicator */}
      <div className="flex items-center justify-center space-x-4">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
          currentStep === 'intro' ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
        }`}>
          1
        </div>
        <div className="w-16 h-0.5 bg-gray-300"></div>
        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
          currentStep === 'demo' ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
        }`}>
          2
        </div>
        <div className="w-16 h-0.5 bg-gray-300"></div>
        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
          currentStep === 'experiment' ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
        }`}>
          3
        </div>
        <div className="w-16 h-0.5 bg-gray-300"></div>
        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
          currentStep === 'results' ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
        }`}>
          4
        </div>
      </div>

      <div className="flex justify-center space-x-6 text-sm">
        <span className={currentStep === 'intro' ? 'text-blue-600 font-medium' : 'text-gray-500'}>
          Introduction
        </span>
        <span className={currentStep === 'demo' ? 'text-blue-600 font-medium' : 'text-gray-500'}>
          Demo
        </span>
        <span className={currentStep === 'experiment' ? 'text-blue-600 font-medium' : 'text-gray-500'}>
          Experiment
        </span>
        <span className={currentStep === 'results' ? 'text-blue-600 font-medium' : 'text-gray-500'}>
          Results
        </span>
      </div>

      {/* Step Content */}
      <div className="min-h-[600px]">
        {currentStep === 'intro' && renderIntro()}
        {currentStep === 'demo' && renderDemo()}
        {currentStep === 'experiment' && renderExperiment()}
        {currentStep === 'results' && renderResults()}
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200">
        <button
          onClick={prevStep}
          disabled={currentStep === 'intro'}
          className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ← Back
        </button>
        
        <div className="text-sm text-gray-500">
          {currentStep === 'intro' && 'Step 1 of 4'}
          {currentStep === 'demo' && 'Step 2 of 4'}
          {currentStep === 'experiment' && `Step 3 of 4 (${experimentStep}/3)`}
          {currentStep === 'results' && 'Step 4 of 4'}
        </div>
        
        {currentStep === 'experiment' && experimentStep < 3 ? (
          <button
            onClick={nextStep}
            disabled={!canGoNext()}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next →
          </button>
        ) : (
          <button
            onClick={nextStep}
            disabled={currentStep === 'experiment' && executionStatus.isRunning}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {currentStep === 'intro' && 'Next →'}
            {currentStep === 'demo' && 'Start Experiment →'}
            {currentStep === 'experiment' && (executionStatus.completedRuns > 0 ? 'View Results →' : 'Waiting...')}
            {currentStep === 'results' && 'View Detailed Analytics →'}
          </button>
        )}
      </div>
    </div>
  )
}
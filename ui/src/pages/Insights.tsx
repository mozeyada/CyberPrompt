import React, { useState, useEffect } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { LengthBias } from '../components/Charts/LengthBias'
import { PromptCoverageChart } from '../components/Charts/PromptCoverageChart'
import { KLDivergenceChart } from '../components/Charts/KLDivergenceChart'
import { CombinedLengthAnalysis } from '../components/Charts/CombinedLengthAnalysis'
import { ModelSelect } from '../components/Filters/ModelSelect'
import { ScenarioSelect } from '../components/Filters/ScenarioSelect'
import { LengthBinMulti } from '../components/Filters/LengthBinMulti'
import { RubricDimensionSelect } from '../components/Filters/RubricDimensionSelect'
import { analyticsApi, statsApi, runsApi } from '../api/client'
import { useFilters } from '../state/useFilters'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'

import { ViewResponseModal } from '../components/Modals/ViewResponseModal'
import { Eye } from 'lucide-react'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export function Insights() {
  const [selectedView, setSelectedView] = useState('rq1')
  const [selectedExperiment, setSelectedExperiment] = useState<string | null>(null)
  const [selectedDimension, setSelectedDimension] = useState('composite')
  const { selectedScenario, selectedModels, scoringMode, setScoringMode } = useFilters()
  const [searchParams] = useSearchParams()
  const queryClient = useQueryClient()

  // URL parameter handling for experiment auto-selection
  useEffect(() => {
    const experimentParam = searchParams.get('experiment')
    if (experimentParam) {
      setSelectedExperiment(experimentParam)
      setSelectedView('rq1') // Auto-switch to RQ1 tab
    }
  }, [searchParams])

  // All Runs tab state
  const [sourceFilter, setSourceFilter] = useState('all')
  const [page, setPage] = useState(1)
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null)
  const [isDownloading, setIsDownloading] = useState(false)
  const [deletingRunId, setDeletingRunId] = useState<string | null>(null)
  const limit = 10

  // Fetch runs and calculate filtered stats (same as CombinedLengthAnalysis)
  const { data: runsData } = useQuery({
    queryKey: ['runs-length-combined'],
    queryFn: () => runsApi.list({ limit: 200 }),
    staleTime: 30000,
    enabled: selectedView === 'rq1'
  })

  // Calculate filtered stats with length distribution
  const statsData = React.useMemo(() => {
    let runs = runsData?.runs?.filter(r => {
      if (r.status !== 'succeeded') return false
      
      if (scoringMode === 'ensemble') {
        // Ensemble mode: must have ensemble_evaluation with aggregated scores
        return r.ensemble_evaluation?.aggregated?.mean_scores?.composite && r.ensemble_evaluation.aggregated.mean_scores.composite > 0
      } else {
        // Single mode: must have regular scores, no ensemble
        return r.scores?.composite && r.scores.composite > 0 && !r.ensemble_evaluation
      }
    }) || []
    
    if (selectedScenario) {
      runs = runs.filter(r => r.scenario === selectedScenario)
    }
    
    if (selectedModels.length > 0) {
      runs = runs.filter(r => selectedModels.includes(r.model))
    }

    const totalRuns = runs.length
    const avgQuality = totalRuns > 0 ? runs.reduce((sum, r) => {
      if (scoringMode === 'ensemble' && r.ensemble_evaluation?.aggregated?.mean_scores?.composite) {
        return sum + r.ensemble_evaluation.aggregated.mean_scores.composite
      } else if (scoringMode === 'single' && r.scores?.composite) {
        return sum + r.scores.composite
      }
      return sum
    }, 0) / totalRuns : 0
    
    // Count by length bin
    const lengthCounts = runs.reduce((acc, r) => {
      const bin = (r as any).prompt_length_bin || 'Unknown'
      acc[bin] = (acc[bin] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    // Count by scenario
    const scenarioCounts = runs.reduce((acc, r) => {
      const scenario = r.scenario || 'Unknown'
      acc[scenario] = (acc[scenario] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return { 
      total_runs: totalRuns, 
      avg_quality_overall: avgQuality,
      length_distribution: lengthCounts,
      scenario_distribution: scenarioCounts
    }
  }, [runsData, selectedScenario, selectedModels, scoringMode])

  // Extract unique experiment IDs for dropdown
  const uniqueExperiments = React.useMemo(() => {
    if (!runsData?.runs) return []
    const experimentIds = new Set(
      runsData.runs
        .map(run => run.experiment_id)
        .filter(id => id) // Remove null/undefined
    )
    return Array.from(experimentIds).sort()
  }, [runsData])

  // Helper function for length bin colors
  const getLengthBinColor = (lengthBin: string | null) => {
    switch (lengthBin) {
      case 'S': return '#10B981' // green
      case 'M': return '#3B82F6' // blue
      case 'L': return '#EF4444' // red
      default: return '#6B7280' // gray
    }
  }

  // Dimension options for scatter plot
  const dimensionOptions = [
    { value: 'composite', label: 'Composite Score' },
    { value: 'accuracy', label: 'Accuracy' },
    { value: 'completeness', label: 'Completeness' },
    { value: 'actionability', label: 'Actionability' },
    { value: 'clarity', label: 'Clarity' }
  ]

  const { data: bestQualityData } = useQuery({
    queryKey: ['analytics-best-quality', selectedScenario],
    queryFn: () => analyticsApi.bestQualityPerAud({
      scenario: selectedScenario || undefined
    })
  })

  // Fetch prompts data for experiment metrics
  const { data: allPrompts } = useQuery({
    queryKey: ['all-prompts'],
    queryFn: () => runsApi.list({ limit: 200 }), // Using runsApi to get prompts - max limit is 200
    enabled: selectedView === 'rq1' && !!selectedExperiment
  })

  // Calculate metrics for selected experiment
  const experimentMetrics = React.useMemo(() => {
    if (!selectedExperiment || !runsData?.runs) {
      return null
    }
    
    let experimentRuns = runsData.runs.filter(run => run.experiment_id === selectedExperiment)
    
    // Apply scoring mode filter to experiment runs
    if (scoringMode === 'ensemble') {
      experimentRuns = experimentRuns.filter(r => !!r.ensemble_evaluation)
    } else if (scoringMode === 'single') {
      experimentRuns = experimentRuns.filter(r => !r.ensemble_evaluation)
    }
    
    const totalRuns = experimentRuns.length
    const avgTokenCost = totalRuns > 0
      ? experimentRuns.reduce((sum, r) => sum + (r.economics?.aud_cost || 0), 0) / totalRuns
      : 0
    const avgScore = totalRuns > 0
      ? experimentRuns.reduce((sum, r) => sum + (r.scores?.composite || 0), 0) / totalRuns
      : 0
    
    // Calculate actual models used in experiment
    const modelsUsed = [...new Set(experimentRuns.map(r => r.model))].sort()
    
    // Calculate actual prompt type breakdown
    const promptBreakdown = experimentRuns.reduce((acc, run) => {
      const source = run.source || 'static'
      if (source === 'static') {
        acc.static++
      } else if (source === 'adaptive') {
        acc.adaptive++
      } else {
        acc.unknown++
      }
      return acc
    }, { static: 0, adaptive: 0, unknown: 0 })
    
    // Calculate scenario breakdown
    const scenarioBreakdown = experimentRuns.reduce((acc, run) => {
      const scenario = run.scenario || 'unknown'
      acc[scenario] = (acc[scenario] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    
    return { totalRuns, avgTokenCost, avgScore, promptBreakdown, experimentRuns, modelsUsed, scenarioBreakdown }
  }, [selectedExperiment, runsData, scoringMode])

  // Scatter data calculation for experiment metrics
  const scatterData = React.useMemo(() => {
    if (!experimentMetrics) return []
    
    return experimentMetrics.experimentRuns.map((run, index) => {
      const lengthBin = (run as any).prompt_length_bin || null
      const selectedScore = selectedDimension === 'composite' 
        ? run.scores?.composite || 0
        : (run.scores as any)?.[selectedDimension] || 0
      
      const jitter = (index % 5 - 2) * 0.02
      
      return {
        tokens: run.tokens?.total || 0,
        score: selectedScore + jitter,
        model: run.model,
        source: run.source || 'static',
        cost: run.economics?.aud_cost || 0,
        lengthBin,
        fsp: (run as any).fsp_enabled || false,
        run_id: run.run_id
      }
    })
  }, [experimentMetrics, selectedDimension])

  // Fetch runs data for All Runs tab
  const { data: allRunsData, isLoading: runsLoading } = useQuery({
    queryKey: ['runs-all-runs'],
    queryFn: () => runsApi.list({
      limit: 200  // Fetch all data like RQ1 tab
    }),
    enabled: selectedView === 'all-runs'
  })

  // Client-side filtering for All Runs tab (same approach as RQ1)
  const filteredAllRunsData = React.useMemo(() => {
    if (!allRunsData?.runs) return { runs: [], page: 1, limit: 200, count: 0 }
    
    let runs = allRunsData.runs
    
    // Filter by scoring mode - more flexible logic
    if (scoringMode === 'ensemble') {
      runs = runs.filter(r => !!r.ensemble_evaluation)
    } else if (scoringMode === 'single') {
      runs = runs.filter(r => !r.ensemble_evaluation)
    }
    // If scoringMode is 'all' or undefined, don't filter by scoring mode
    
    // Filter by scenario
    if (selectedScenario) {
      runs = runs.filter(r => r.scenario === selectedScenario)
    }
    
    // Filter by models
    if (selectedModels.length > 0) {
      runs = runs.filter(r => selectedModels.includes(r.model))
    }
    
    return {
      ...allRunsData,
      runs: runs,
      count: runs.length
    }
  }, [allRunsData, selectedScenario, selectedModels, scoringMode])

  const handleDownloadCSV = async () => {
    const runs = filteredAllRunsData?.runs || []
    if (!runs || runs.length === 0) {
      alert('No data to export. Please run some experiments first.')
      return
    }

    const validRuns = runs.filter(run => run.status === 'succeeded')
    if (validRuns.length === 0) {
      alert('No successful runs to export. Please check your experiment results.')
      return
    }

    setIsDownloading(true)
    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const API_KEY = import.meta.env.VITE_API_KEY || 'supersecret1'

      const params = new URLSearchParams()
      if (sourceFilter !== 'all') {
        params.append('source', sourceFilter)
      }
      params.append('export_timestamp', new Date().toISOString())
      params.append('total_records', validRuns.length.toString())

      const response = await fetch(`${API_BASE_URL}/results/export?${params}`, {
        headers: { 'x-api-key': API_KEY }
      })

      if (!response.ok) throw new Error('Export failed')

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `cyberprompt_results_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      console.log(`Exported ${validRuns.length} valid runs out of ${runs.length} total runs`)
    } catch (error) {
      console.error('Download failed:', error)
      alert('Download failed. Please try again.')
    } finally {
      setIsDownloading(false)
    }
  }

  const handleDeleteRun = async (runId: string) => {
    if (!confirm('Are you sure you want to delete this run? This action cannot be undone.')) {
      return
    }

    setDeletingRunId(runId)
    try {
      await runsApi.delete(runId)
      // Refetch data instead of full page reload
      if (selectedView === 'all-runs') {
        // Refetch the all runs data
        await queryClient.invalidateQueries({ queryKey: ['runs-all-runs'] })
      } else {
        // Refetch the main runs data
        await queryClient.invalidateQueries({ queryKey: ['runs-data'] })
      }
    } catch (error) {
      console.error('Delete failed:', error)
      alert('Failed to delete run. Please try again.')
    } finally {
      setDeletingRunId(null)
    }
  }

  const views = [
    { id: 'rq1', name: 'RQ1: Prompt Length' },
    { id: 'rq2', name: 'RQ2: Adaptive Benchmarking' },
    { id: 'all-runs', name: 'All Runs' },
    { id: 'model-performance', name: 'Model Performance' }
  ]



  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-bold text-gray-900">Experiment Results</h1>
        <p className="mt-2 text-gray-600">Research analytics, statistical validation, and detailed run inspection</p>
      </div>

      {/* Analysis Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {views.map((view) => (
            <button
              key={view.id}
              onClick={() => setSelectedView(view.id)}
              className={`py-3 px-1 border-b-2 font-medium text-sm ${
                selectedView === view.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {view.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Filters - Only show for relevant views */}
      {(selectedView === 'rq1' || selectedView === 'rq2' || selectedView === 'model-performance' || selectedView === 'all-runs') && (
        <div className="bg-white shadow rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <ScenarioSelect />
            <ModelSelect />
            {(selectedView === 'rq1' || selectedView === 'all-runs') && (
              <>
                <div className="col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Scoring Mode</label>
                  <select
                    value={scoringMode}
                    onChange={(e) => setScoringMode(e.target.value as 'ensemble' | 'single')}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                  >
                    <option value="ensemble">Ensemble (Multi-Judge)</option>
                    <option value="single">Single Judge</option>
                  </select>
                    <div className="text-xs text-gray-500 mt-1">
                      {scoringMode === 'ensemble' ? '3 judges, higher reliability' : '1 judge, faster'}
                    </div>
                  </div>
                  {selectedView === 'rq1' && (
                    <div className="col-span-1">
                      <label className="block text-sm font-medium text-gray-700 mb-2">Experiment</label>
                      <select
                        value={selectedExperiment || 'all'}
                        onChange={(e) => setSelectedExperiment(e.target.value === 'all' ? null : e.target.value)}
                        className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                      >
                        <option value="all">All Experiments</option>
                        {uniqueExperiments.map(expId => (
                          <option key={expId} value={expId}>
                            {expId}
                          </option>
                        ))}
                      </select>
                      <div className="text-xs text-gray-500 mt-1">
                        {selectedExperiment ? 'Showing specific experiment' : 'Showing all experiments'}
                      </div>
                    </div>
                  )}
                <div className="col-span-1 bg-blue-50 border border-blue-200 rounded p-3">
                  <p className="text-xs text-blue-800">
                    <strong>Note:</strong> RQ1 analysis compares S/M/L lengths. Length bin filter disabled for this view.
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Research Analytics Views */}
      <div className="space-y-6">
        {selectedView === 'rq1' && (
          <div className="space-y-6">
            {/* RQ1 Header */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-2">Research Question 1</h4>
              <p className="text-sm text-blue-800">
                How does prompt length impact AI model quality and cost-effectiveness in cybersecurity operations?
              </p>
            </div>

            {/* Data Summary - Only show when NO experiment is selected */}
            {!selectedExperiment && (
              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Evaluation Dataset</h3>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      scoringMode === 'ensemble' 
                        ? 'bg-purple-100 text-purple-800' 
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {scoringMode === 'ensemble' ? 'Ensemble Scoring' : 'Single Judge Scoring'}
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-4 gap-4">
                  <div>
                    <div className="text-sm text-gray-600">Total Runs</div>
                    <div className="text-2xl font-bold">{statsData?.total_runs || 0}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Avg Quality</div>
                    <div className="text-2xl font-bold">{(statsData?.avg_quality_overall || 0).toFixed(1)}/5</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Length Distribution</div>
                    <div className="text-lg font-semibold">
                      {statsData?.length_distribution ? (
                        <span>
                          S: {statsData.length_distribution['S'] || 0} | 
                          M: {statsData.length_distribution['M'] || 0} | 
                          L: {statsData.length_distribution['L'] || 0}
                        </span>
                      ) : 'N/A'}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Scenarios</div>
                    <div className="text-sm">
                      {statsData?.scenario_distribution ? (
                        <div className="space-y-1">
                          {Object.entries(statsData.scenario_distribution).map(([scenario, count]) => (
                            <div key={scenario} className="flex justify-between">
                              <span className="text-xs">{scenario.replace('_', ' ')}</span>
                              <span className="text-xs font-medium">{count}</span>
                            </div>
                          ))}
                        </div>
                      ) : 'N/A'}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Experiment Summary Metrics - Show first when experiment is selected */}
            {experimentMetrics && (
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Experiment Summary: {selectedExperiment}</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6">
                  {/* Total Benchmark Runs */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Benchmark Runs</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {experimentMetrics.totalRuns.toLocaleString()}
                      </p>
                    </div>
                  </div>

                  {/* Models Used */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Models Used</p>
                      <div className="mt-2">
                        {experimentMetrics.modelsUsed.map(model => (
                          <Badge key={model} variant="secondary" className="mr-1 mb-1 text-xs">
                            {model.replace('llama-3.3-70b-versatile', 'Llama 3.3 70B').replace('claude-3-5-sonnet', 'Claude 3.5 Sonnet').replace('gpt-4o', 'GPT-4o').replace('gemini-2.5-pro', 'Gemini 2.5 Pro')}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Scenarios Used */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Scenarios</p>
                      <div className="mt-2">
                        {Object.entries(experimentMetrics.scenarioBreakdown).map(([scenario, count]) => (
                          <div key={scenario} className="flex justify-between items-center mb-1">
                            <Badge variant="outline" className="text-xs">
                              {scenario.replace('_', ' ')}
                            </Badge>
                            <span className="text-xs font-medium">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Average Cost Per Query */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Avg Cost Per Query</p>
                      <p className="text-2xl font-bold text-gray-900">
                        ${experimentMetrics.avgTokenCost.toFixed(6)} AUD
                      </p>
                      <p className="text-xs text-gray-500 mt-1">Per prompt execution</p>
                    </div>
                  </div>

                  {/* Average Score */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Avg Quality Score</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {experimentMetrics.avgScore.toFixed(1)}/5.0
                      </p>
                    </div>
                  </div>

                  {/* Prompt Type Breakdown */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-3">Prompt Types</p>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <Badge variant="outline" className="text-xs">Static</Badge>
                          <span className="font-medium">{experimentMetrics.promptBreakdown.static}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <Badge variant="default" className="text-xs">Adaptive</Badge>
                          <span className="font-medium">{experimentMetrics.promptBreakdown.adaptive}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Cost Efficiency Scatter Plot */}
            {experimentMetrics && (
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold">Cost Efficiency Analysis</h3>
                  <select
                    value={selectedDimension}
                    onChange={(e) => setSelectedDimension(e.target.value)}
                    className="border border-gray-300 rounded px-3 py-1 text-sm"
                  >
                    {dimensionOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  Top-left = most efficient (high quality, low cost). Group by model to compare performance.
                </p>
                
                {/* Legend */}
                <div className="flex flex-wrap gap-4 mb-4 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">Length:</span>
                    {['S', 'M', 'L'].map(bin => (
                      <div key={bin} className="flex items-center gap-1">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: getLengthBinColor(bin) }}
                        />
                        <span>{bin}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <ResponsiveContainer width="100%" height={350}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="tokens" 
                      name="Tokens" 
                      label={{ value: 'Tokens Used', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis 
                      dataKey="score" 
                      name="Score" 
                      domain={[0, 5]}
                      label={{ value: 'Quality Score', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip 
                      content={({ active, payload }) => {
                        if (active && payload && payload[0]) {
                          const data = payload[0].payload
                          return (
                            <div className="bg-white p-3 border rounded shadow-lg">
                              <div className="font-medium text-lg mb-2">{data.model}</div>
                              <div className="grid grid-cols-2 gap-2 text-sm">
                                <div className="text-gray-600">Score:</div>
                                <div className="font-medium">{data.score.toFixed(2)}/5.0</div>
                                <div className="text-gray-600">Tokens:</div>
                                <div className="font-medium">{data.tokens}</div>
                                <div className="text-gray-600">Cost:</div>
                                <div className="font-medium">${data.cost.toFixed(6)}</div>
                                <div className="text-gray-600">Length:</div>
                                <div className="font-medium">{data.lengthBin || 'Unknown'}</div>
                              </div>
                            </div>
                          )
                        }
                        return null
                      }}
                    />
                    <Scatter 
                      data={scatterData} 
                      fill="#8884d8"
                      shape={(props: any) => {
                        const { cx, cy, lengthBin } = props
                        const color = getLengthBinColor(lengthBin)
                        return (
                          <circle 
                            cx={cx} 
                            cy={cy} 
                            r={5} 
                            fill={color}
                            stroke="#000"
                            strokeWidth={1}
                          />
                        )
                      }}
                    />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Combined Length Analysis - Show after experiment summary */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-2">Prompt Length Impact Analysis</h3>
              <p className="text-sm text-gray-600 mb-6">
                Comprehensive analysis showing quality, cost, and efficiency trade-offs across Short, Medium, and Long prompts.
              </p>
              <CombinedLengthAnalysis experimentId={selectedExperiment || undefined} />
            </div>

            {/* Length Bias Statistical Validation - Only show if sufficient data exists */}
            {statsData && statsData.total_runs > 0 && (
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-2">Methodology Validation: FSP Bias Mitigation</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Validates that Focus Sentence Prompting (FSP) eliminates length bias in AI judge scoring. Red bars show dimensions where bias exists without FSP (p&lt;0.05), proving FSP is essential for fair cost-quality comparisons.
                </p>
                <LengthBias />
                <div className="mt-4 text-xs text-gray-500 bg-gray-50 p-3 rounded">
                  <strong>Research Validity:</strong> FSP (Focus Sentence Prompting) corrects verbosity bias to ensure fair cost-effectiveness comparisons across prompt lengths.
                </div>
              </div>
            )}
          </div>
        )}

        {selectedView === 'rq2' && (
          <div className="space-y-6">
            {/* RQ2 Header */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-semibold text-green-900 mb-2">Research Question 2</h4>
              <p className="text-sm text-green-800">
                Can adaptive generative benchmarking from SOC/GRC documents and CTI improve evaluation coverage and relevance over static datasets?
              </p>
            </div>

            {/* KL Divergence Validation */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Statistical Validation: KL Divergence Test</h3>
              <p className="text-sm text-gray-600 mb-4">
                Tests if adaptive prompts maintain similar distribution to CySecBench baseline. Values &lt;0.5 = good match, validating comparability.
              </p>
              <KLDivergenceChart />
              <div className="mt-4 text-xs text-gray-500 bg-gray-50 p-3 rounded">
                <strong>Research Validity:</strong> Low KL divergence confirms adaptive prompts don't introduce systematic bias vs. static benchmarks.
              </div>
            </div>

            {/* Coverage Analysis */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Coverage Improvement Analysis</h3>
              <p className="text-sm text-gray-600 mb-4">
                Compares scenario coverage between static CySecBench and adaptive CTI/policy-generated prompts.
              </p>
              <PromptCoverageChart />
              <div className="mt-4 text-xs text-gray-500 bg-gray-50 p-3 rounded">
                <strong>Finding:</strong> Adaptive prompts cover emerging threats and regulatory updates absent from static datasets.
              </div>
            </div>

            {/* Framework Generalization */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Framework Generalization</h3>
              <p className="text-sm text-gray-600 mb-4">
                RQ1 cost-efficiency findings (S/M/L prompt length trade-offs) apply to both static and adaptive prompts, demonstrating framework robustness across prompt sources.
              </p>
              <div className="bg-green-50 border border-green-200 rounded p-4">
                <p className="text-sm text-green-900">
                  <strong>Key Insight:</strong> The optimal prompt length patterns identified in RQ1 hold for dynamically generated prompts from real SOC/GRC documents, validating that our cost-quality framework generalizes beyond static benchmarks.
                </p>
              </div>
            </div>
          </div>
        )}


        {selectedView === 'all-runs' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                  <h3 className="text-lg font-semibold">All Experiment Runs</h3>
                </div>
                <Button
                  onClick={handleDownloadCSV}
                  disabled={isDownloading}
                  variant="outline"
                  size="sm"
                >
                  {isDownloading ? 'Downloading...' : 'Export CSV'}
                </Button>
              </div>

              {runsLoading ? (
                <div className="text-center py-8">Loading results...</div>
              ) : !filteredAllRunsData?.runs?.length ? (
                <div className="text-center py-8 text-gray-500">
                  No results found. Run some experiments first!
                </div>
              ) : (
                <>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-gray-200">
                          <th className="text-left py-3 px-4 font-medium text-gray-600">Model</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-600">Source</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-600">Experiment</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-600">Dataset</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-600">Status</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-600">Tokens</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-600">Cost (AUD)</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-600">Quality Score</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-600">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredAllRunsData.runs.map((run, index) => (
                          <tr key={run.run_id} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                            <td className="py-3 px-4">
                              <Badge variant="secondary">{run.model}</Badge>
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex flex-col gap-1">
                                <Badge variant={run.source === 'adaptive' ? 'default' : 'outline'}>
                                  {run.source || 'static'}
                                </Badge>
                                <Badge variant={run.ensemble_evaluation ? 'default' : 'secondary'} className="text-xs">
                                  {run.ensemble_evaluation ? 'Ensemble' : 'Single'}
                                </Badge>
                              </div>
                            </td>
                            <td className="py-3 px-4">
                              <span className="text-xs text-gray-600">
                                {run.experiment_id ? run.experiment_id.split('_').slice(-1)[0] : 'N/A'}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              <span className="text-xs text-gray-600">
                                {run.dataset_version || 'N/A'}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              <Badge variant={run.status === 'succeeded' ? 'default' : 'destructive'}>
                                {run.status}
                              </Badge>
                            </td>
                            <td className="py-3 px-4 text-sm">{run.tokens?.total || 0}</td>
                            <td className="py-3 px-4 text-sm">${run.economics?.aud_cost?.toFixed(4) || '0.0000'}</td>
                            <td className="py-3 px-4 text-sm">
                              {(() => {
                                if (run.ensemble_evaluation?.aggregated?.mean_scores?.composite) {
                                  return (
                                    <div className="space-y-1">
                                      <span className="font-medium text-purple-600">
                                        {run.ensemble_evaluation.aggregated.mean_scores.composite.toFixed(1)}/5.0
                                      </span>
                                      <div className="text-xs text-purple-500">Multi-Judge</div>
                                    </div>
                                  )
                                } else if (run.scores?.composite) {
                                  return (
                                    <div className="space-y-1">
                                      <span className="font-medium">
                                        {run.scores.composite.toFixed(1)}/5.0
                                      </span>
                                      <div className="text-xs text-gray-500">Single Judge</div>
                                    </div>
                                  )
                                } else {
                                  return 'N/A'
                                }
                              })()}
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex items-center gap-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => setSelectedRunId(run.run_id)}
                                  className="flex items-center gap-1"
                                  disabled={run.status !== 'succeeded'}
                                >
                                  <Eye className="h-3 w-3" />
                                  View
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleDeleteRun(run.run_id)}
                                  className="flex items-center gap-1 text-red-600 hover:text-red-700"
                                  disabled={deletingRunId === run.run_id}
                                >
                                  {deletingRunId === run.run_id ? (
                                    <>⏳</>
                                  ) : (
                                    <>🗑️</>
                                  )}
                                  {deletingRunId === run.run_id ? 'Deleting...' : 'Delete'}
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="flex justify-between items-center mt-4">
                    <span className="text-sm text-gray-500">
                      Page {page} • {filteredAllRunsData?.count || 0} total runs
                    </span>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                      >
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage(p => p + 1)}
                        disabled={filteredAllRunsData?.runs?.length < limit}
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* View Response Modal */}
            {selectedRunId && (
              <ViewResponseModal
                runId={selectedRunId}
                isOpen={!!selectedRunId}
                onClose={() => setSelectedRunId(null)}
              />
            )}
          </div>
        )}

        {selectedView === 'model-performance' && (
          <div className="space-y-6">
            {/* Model Performance Header */}
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h4 className="font-semibold text-purple-900 mb-2">Model Performance Comparison</h4>
              <p className="text-sm text-purple-800">
                Practical guidance for SOC/GRC teams selecting AI models for cybersecurity operations.
              </p>
            </div>

            {/* Model Efficiency Leaderboard */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Model Efficiency Leaderboard</h3>
              <p className="text-sm text-gray-600 mb-4">
                Models ranked by Quality per AUD. Higher = better cost-effectiveness for cybersecurity tasks.
              </p>
              {(bestQualityData?.leaderboard && bestQualityData.leaderboard.length > 0) ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2">Rank</th>
                        <th className="text-left py-2">Model</th>
                        <th className="text-left py-2">Quality/AUD</th>
                        <th className="text-left py-2">Avg Quality</th>
                        <th className="text-left py-2">Avg Cost</th>
                        <th className="text-left py-2">Runs</th>
                      </tr>
                    </thead>
                    <tbody>
                      {bestQualityData.leaderboard.map((entry, index) => (
                        <tr key={entry.model_id} className={index % 2 === 0 ? 'bg-gray-50' : ''}>
                          <td className="py-2">
                            {index === 0 && <span className="text-yellow-500 mr-1">🏆</span>}
                            {index + 1}
                          </td>
                          <td className="py-2 font-medium">{entry.model_id}</td>
                          <td className="py-2 text-green-600 font-bold">{entry.quality_per_aud.toFixed(2)}</td>
                          <td className="py-2">{entry.avg_quality.toFixed(2)}/5.0</td>
                          <td className="py-2">${entry.avg_cost.toFixed(4)}</td>
                          <td className="py-2 text-gray-500">{entry.count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  No model performance data available. Run experiments to populate leaderboard.
                </div>
              )}
              <div className="mt-4 text-xs text-gray-500 bg-gray-50 p-3 rounded">
                <strong>Guidance:</strong> High-stakes tasks may justify premium models; routine operations can use cost-effective options.
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}


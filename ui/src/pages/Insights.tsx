import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
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

export function Insights() {
  const [selectedView, setSelectedView] = useState('rq1')
  const { selectedScenario, selectedModels, scoringMode, setScoringMode } = useFilters()

  // All Runs tab state
  const [sourceFilter, setSourceFilter] = useState('all')
  const [page, setPage] = useState(1)
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null)
  const [isDownloading, setIsDownloading] = useState(false)
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

    return { 
      total_runs: totalRuns, 
      avg_quality_overall: avgQuality,
      length_distribution: lengthCounts
    }
  }, [runsData, selectedScenario, selectedModels, scoringMode])

  const { data: bestQualityData } = useQuery({
    queryKey: ['analytics-best-quality', selectedScenario],
    queryFn: () => analyticsApi.bestQualityPerAud({
      scenario: selectedScenario || undefined
    })
  })

  // Fetch runs data for All Runs tab
  const { data: allRunsData, isLoading: runsLoading } = useQuery({
    queryKey: ['runs-detailed', page, sourceFilter],
    queryFn: () => runsApi.list({
      page,
      limit,
      ...(sourceFilter !== 'all' && { source: sourceFilter })
    }),
    enabled: selectedView === 'all-runs'
  })

  const handleDownloadCSV = async () => {
    const runs = allRunsData?.runs || []
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
      a.download = `cybercqbench_results_${new Date().toISOString().split('T')[0]}.csv`
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
      {(selectedView === 'rq1' || selectedView === 'rq2' || selectedView === 'model-performance') && (
        <div className="bg-white shadow rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <ScenarioSelect />
            <ModelSelect />
            {selectedView === 'rq1' && (
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

            {/* Data Summary */}
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">📊 Evaluation Dataset</h3>
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
              <div className="grid grid-cols-3 gap-4">
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
              </div>
            </div>

            {/* Combined Length Analysis - THE ANSWER */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-2">Prompt Length Impact Analysis</h3>
              <p className="text-sm text-gray-600 mb-6">
                Comprehensive analysis showing quality, cost, and efficiency trade-offs across Short, Medium, and Long prompts.
              </p>
              <CombinedLengthAnalysis />
            </div>

            {/* Length Bias Statistical Validation */}
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
                  <div className="flex items-center gap-2">
                    <label className="text-sm font-medium text-gray-700">Source:</label>
                    <select 
                      value={sourceFilter} 
                      onChange={(e) => setSourceFilter(e.target.value)} 
                      className="w-32 rounded-md border border-gray-300 px-3 py-1.5 text-sm"
                    >
                      <option value="all">All</option>
                      <option value="static">Static</option>
                      <option value="adaptive">Adaptive</option>
                    </select>
                  </div>
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
              ) : !allRunsData?.runs?.length ? (
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
                        {allRunsData.runs.map((run, index) => (
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
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="flex justify-between items-center mt-4">
                    <span className="text-sm text-gray-500">
                      Page {page} • {allRunsData?.count || 0} total runs
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
                        disabled={allRunsData?.runs?.length < limit}
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


import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { runsApi, statsApi, promptsApi } from '../api/client'
import { Badge } from '../components/ui/badge'

import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter } from 'recharts'
import { CombinedLengthAnalysis } from '../components/Charts/CombinedLengthAnalysis'

export function Overview({ experimentId: propExperimentId }: { experimentId?: string } = {}) {
  const [searchParams] = useSearchParams()
  const experimentId = propExperimentId || searchParams.get('experiment')
  const [selectedDimension, setSelectedDimension] = useState('composite')
  
  const { data: statsOverview, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ['stats-overview'],
    queryFn: statsApi.overview
  })

  const { data: allRuns, isLoading: runsLoading, error: runsError } = useQuery({
    queryKey: ['all-runs', experimentId],
    queryFn: () => runsApi.list(experimentId ? { experiment_id: experimentId } : {})
  })

  const { data: allPrompts, isLoading: promptsLoading, error: promptsError } = useQuery({
    queryKey: ['all-prompts'],
    queryFn: () => promptsApi.list({ limit: 500 })
  })

  // Remove unused recentRuns - we use allRuns.runs.slice(0,5) instead

  // Client-side aggregation - use ONLY experiment runs if experimentId provided
  const experimentRuns = experimentId 
    ? (allRuns?.runs || [])
    : (allRuns?.runs || [])
  
  const totalRuns = experimentRuns.length
  const avgTokenCost = totalRuns > 0
    ? experimentRuns.reduce((sum, r) => sum + (r.economics?.aud_cost || 0), 0) / totalRuns
    : 0
  const avgScore = totalRuns > 0
    ? experimentRuns.reduce((sum, r) => sum + (r.scores?.composite || 0), 0) / totalRuns
    : 0
  
  // Show message when no runs exist
  const hasNoRuns = totalRuns === 0

  // Prompt type breakdown from actual prompt data
  const promptBreakdown = allPrompts?.prompts?.reduce((acc, prompt) => {
    if (prompt.prompt_type === 'adaptive') {
      acc.adaptive += 1
    } else if (prompt.prompt_type === 'static') {
      acc.static += 1
    } else {
      acc.unknown += 1
    }
    return acc
  }, { static: 0, adaptive: 0, unknown: 0 }) || { static: 0, adaptive: 0, unknown: 0 }



  const modelChartData = experimentRuns.reduce((acc, run) => {
    const existing = acc.find(item => item.model === run.model)
    if (existing) {
      existing.count += 1
    } else {
      acc.push({ model: run.model, count: 1 })
    }
    return acc
  }, [] as Array<{model: string, count: number}>) || []

  const getLengthBinColor = (lengthBin: string | null) => {
    switch (lengthBin) {
      case 'S': return '#10B981' // green (268-362 tokens - Tactical)
      case 'M': return '#3B82F6'  // blue (379-485 tokens - Analytical)
      case 'L': return '#EF4444'  // red (616-721 tokens - Strategic)
      case null:
      case undefined:
      default: return '#6B7280'  // gray for null/unknown
    }
  }

  const scatterData = experimentRuns.map((run, index) => {
    // Use prompt_length_bin directly from run data
    const lengthBin = run.prompt_length_bin || null
    const selectedScore = selectedDimension === 'composite' 
      ? run.scores?.composite || 0
      : run.scores?.[selectedDimension] || 0
    
    // Add small jitter to prevent overlapping points
    const jitter = (index % 5 - 2) * 0.02 // Small random offset
    
    return {
      tokens: run.tokens?.total || 0,
      score: selectedScore + jitter,
      model: run.model,
      source: run.source || 'static',
      cost: run.economics?.aud_cost || 0,
      lengthBin,
      fsp: run.fsp_enabled || false,
      allScores: run.scores,
      fill: getLengthBinColor(lengthBin),
      stroke: '#000000',
      strokeWidth: 1,
      run_id: run.run_id // Add for debugging
    }
  }) || []

  const allScoresZero = scatterData.every(point => point.score === 0)
  console.log('Debug - All scores zero:', allScoresZero)
  console.log('Debug - Sample scores:', scatterData.slice(0, 3).map(d => ({run_id: d.model, score: d.score, fsp: d.fsp, tokens: d.tokens})))

  const getModelColor = (model: string) => {
    if (model.includes('gpt-4')) return '#8B5CF6'
    if (model.includes('gpt-3.5')) return '#A855F7'
    if (model.includes('claude')) return '#F97316'
    if (model.includes('gemini')) return '#3B82F6'
    return '#6B7280'
  }

  const dimensionOptions = [
    { value: 'composite', label: 'Composite Score' },
    { value: 'technical_accuracy', label: 'Technical Accuracy' },
    { value: 'actionability', label: 'Actionability' },
    { value: 'completeness', label: 'Completeness' },
    { value: 'compliance_alignment', label: 'Compliance Alignment' },
    { value: 'risk_awareness', label: 'Risk Awareness' },
    { value: 'relevance', label: 'Relevance' },
    { value: 'clarity', label: 'Clarity' }
  ]

  // Split data by FSP status for different shapes
  const fspEnabledData = scatterData.filter(d => d.fsp && d.tokens > 0)
  const fspDisabledData = scatterData.filter(d => !d.fsp && d.tokens > 0)
  
  // Debug logging
  console.log('Debug - Total scatter data points:', scatterData.length)
  console.log('Debug - FSP enabled points:', fspEnabledData.length)
  console.log('Debug - FSP disabled points:', fspDisabledData.length)
  console.log('Debug - Sample data point:', scatterData[0])

  // Helper functions for table
  const getSourceTag = (run: any) => {
    if (run.source === 'adaptive') return { label: 'Adaptive', color: 'bg-green-100 text-green-800' }
    if (run.source === 'curated') return { label: 'Static (Curated)', color: 'bg-blue-100 text-blue-800' }
    return { label: 'Static', color: 'bg-gray-100 text-gray-800' }
  }

  const getScoreBadge = (score: number) => {
    if (score === 0) return { label: '0.0', color: 'bg-gray-100 text-gray-600' }
    if (score < 2.0) return { label: score.toFixed(1), color: 'bg-red-100 text-red-800' }
    if (score <= 3.5) return { label: score.toFixed(1), color: 'bg-yellow-100 text-yellow-800' }
    return { label: score.toFixed(1), color: 'bg-green-100 text-green-800' }
  }

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr + 'Z') // Add Z to indicate UTC
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  }

  const isLoading = statsLoading || runsLoading || promptsLoading
  const hasError = statsError || runsError || promptsError

  if (hasError) {
    return (
      <div className="p-8 text-center">
        <div className="text-red-600 mb-2">Error loading data</div>
        <div className="text-sm text-gray-500">Please check API connectivity</div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          {experimentId ? 'RQ1 Experiment Results' : 'Research Overview'}
        </h1>
        <p className="text-gray-600">
          {experimentId 
            ? `Analysis of ${totalRuns} runs from this experiment` 
            : 'Real-time benchmarking insights from working APIs'}
        </p>
        {experimentId && (
          <div className="mt-2 inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
            Experiment ID: {experimentId}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Benchmark Runs */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Benchmark Runs</p>
              <p className="text-2xl font-bold text-gray-900">
                {isLoading ? '...' : totalRuns.toLocaleString()}
              </p>
            </div>

          </div>
        </div>

        {/* Average Token Cost */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Token Cost</p>
              <p className="text-2xl font-bold text-gray-900">
                {isLoading ? '...' : `$${avgTokenCost.toFixed(4)}`}
              </p>
            </div>

          </div>
        </div>

        {/* Average Score */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Quality Score</p>
              <div className="flex items-center gap-2">
                <p className="text-2xl font-bold text-gray-900">
                  {isLoading ? '...' : `${avgScore.toFixed(1)}/5.0`}
                </p>
                {avgScore === 0 && totalRuns > 0 && !isLoading && (
                  <span title="Backend judge returns zero scores – scoring may be disabled" className="text-yellow-500">
                    ⚠️
                  </span>
                )}
              </div>
            </div>

          </div>
        </div>

        {/* Prompt Type Breakdown */}
        <div className="bg-white rounded-lg shadow p-6">
          <div>
            <p className="text-sm font-medium text-gray-600 mb-3">Prompt Types</p>
            {isLoading ? (
              <div className="text-gray-400">Loading...</div>
            ) : (
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <Badge variant="outline" className="text-xs">Static</Badge>
                  <span className="font-medium">{promptBreakdown.static}</span>
                </div>
                <div className="flex justify-between items-center">
                  <Badge 
                    variant={promptBreakdown.adaptive === 0 ? "destructive" : "default"} 
                    className="text-xs"
                  >
                    Adaptive
                  </Badge>
                  <span className="font-medium">{promptBreakdown.adaptive}</span>
                </div>
                {promptBreakdown.unknown > 0 && (
                  <div className="flex justify-between items-center">
                    <Badge variant="outline" className="text-xs text-gray-400">Unknown</Badge>
                    <span className="font-medium text-gray-400">{promptBreakdown.unknown}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* RQ1 Results: Prompt Length Analysis */}
      {experimentId && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">RQ1: Prompt Length Impact Analysis</h3>
          <p className="text-sm text-gray-600 mb-6">
            Cost-quality trade-offs across Short, Medium, and Long prompts from your experiment
          </p>
          <CombinedLengthAnalysis />
        </div>
      )}

      {/* Chart 3: Enhanced Score vs Token Usage - Full Width */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold">Cost Efficiency Analysis</h3>
            {allScoresZero && !isLoading && (
              <span title="Scores may be disabled" className="text-yellow-500">⚠️</span>
            )}
          </div>
          <div className="flex items-center gap-4">
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
        </div>
        <p className="text-sm text-gray-600 mb-4">Top-left = most efficient (high quality, low cost). Group by model to compare performance.</p>
        
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
            <div className="flex items-center gap-1">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: getLengthBinColor(null) }}
              />
              <span>Unknown</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-medium">Fair Scoring (FSP):</span>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full bg-gray-400 border border-black" />
              <span className="text-gray-700 font-medium">Enabled (Circle)</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-gray-400 border border-black transform rotate-45" />
              <span className="text-gray-700 font-medium">Disabled (Diamond)</span>
            </div>
          </div>
        </div>
        
        {isLoading ? (
          <div className="h-64 flex items-center justify-center text-gray-400">Loading...</div>
        ) : (
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
                    const efficiency = data.tokens > 0 ? (data.score / data.tokens * 1000).toFixed(1) : '0'
                    return (
                      <div className="bg-white p-3 border rounded shadow-lg">
                        <div className="font-medium text-lg mb-2">{data.model}</div>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div>Quality: <strong>{data.score.toFixed(1)}/5</strong></div>
                          <div>Tokens: <strong>{data.tokens.toLocaleString()}</strong></div>
                          <div>Cost: <strong>${data.cost.toFixed(4)}</strong></div>
                          <div>Length: <strong>{data.lengthBin || '?'}</strong></div>
                        </div>
                        <div className="mt-2 pt-2 border-t">
                          <div className="text-xs text-gray-600">Efficiency: {efficiency} pts/1K tokens</div>
                          <div className="text-xs text-gray-600">FSP: {data.fsp ? 'Yes' : 'No'}</div>
                        </div>
                      </div>
                    )
                  }
                  return null
                }}
              />
              {/* FSP Enabled - Circles */}
              <Scatter 
                data={fspEnabledData}
                fillOpacity={0.8}
                name="FSP Enabled"
                shape="circle"
              />
              {/* FSP Disabled - Diamonds */}
              <Scatter 
                data={fspDisabledData}
                fillOpacity={0.8}
                name="FSP Disabled"
                shape="diamond"
              />
            </ScatterChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Recent Benchmark Runs Table */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Benchmark Runs</h3>
        {isLoading ? (
          <div className="text-center py-8 text-gray-400">Loading recent runs...</div>
        ) : hasError ? (
          <div className="text-center py-8 text-red-600">Error loading recent runs</div>
        ) : !allRuns?.runs?.length || hasNoRuns ? (
          <div className="text-center py-8 text-gray-400">
            {hasNoRuns ? 'No benchmark runs yet. Go to Benchmark Runner to create your first experiment!' : 'No runs found'}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Run ID</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Model</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Scenario</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">
                    <div className="flex items-center gap-1">
                      Score
                      <span title="Auto-scored by LLM judge" className="text-gray-400 cursor-help">ℹ️</span>
                    </div>
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Length</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Tokens</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Cost</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">FSP</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Run Time</th>
                </tr>
              </thead>
              <tbody>
                {experimentRuns
                  .filter(run => run.status === 'succeeded')
                  .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                  .slice(0, experimentId ? 50 : 15)
                  .map((run, index) => {
                    const scoreBadge = getScoreBadge(run.scores?.composite || 0)
                    
                    return (
                      <tr key={run.run_id} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                        <td className="py-3 px-4">
                          <div className="text-sm text-gray-900 max-w-xs truncate">
                            {run.run_id.substring(0, 8)}...
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <span className="text-sm font-medium text-gray-900">{run.model}</span>
                        </td>
                        <td className="py-3 px-4">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {run.prompt?.scenario || 'Unknown'}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${scoreBadge.color}`}>
                              {scoreBadge.label}
                            </span>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                            run.prompt_length_bin === 'S' ? 'bg-green-100 text-green-800' :
                            run.prompt_length_bin === 'M' ? 'bg-blue-100 text-blue-800' :
                            run.prompt_length_bin === 'L' ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-600'
                          }`}>
                            {run.prompt_length_bin || '?'}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span className="text-sm text-gray-900">
                            {(run.tokens?.total || 0).toLocaleString()}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span className="text-sm text-gray-900">
                            ${(run.economics?.aud_cost || 0).toFixed(4)}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                            run.fsp_enabled 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-600'
                          }`}>
                            {run.fsp_enabled ? 'Yes' : 'No'}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span className="text-sm text-gray-500">
                            {formatDateTime(run.created_at)}
                          </span>
                        </td>
                      </tr>
                    )
                  })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
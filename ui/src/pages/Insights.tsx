import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { LengthBias } from '../components/Charts/LengthBias'
import { RiskCurves } from '../components/Charts/RiskCurves'
import { RiskCostFrontier } from '../components/Charts/RiskCostFrontier'
import { PromptCoverageChart } from '../components/Charts/PromptCoverageChart'
import { KLDivergenceChart } from '../components/Charts/KLDivergenceChart'
import { ModelSelect } from '../components/Filters/ModelSelect'
import { ScenarioSelect } from '../components/Filters/ScenarioSelect'
import { LengthBinMulti } from '../components/Filters/LengthBinMulti'
import { RubricDimensionSelect } from '../components/Filters/RubricDimensionSelect'
import { analyticsApi, statsApi } from '../api/client'
import { useFilters } from '../state/useFilters'

export function Insights() {
  const [selectedView, setSelectedView] = useState('research')
  const { selectedScenario, selectedModels } = useFilters()
  
  // Fetch analytics summary for research metrics
  const { data: statsData } = useQuery({
    queryKey: ['stats-analytics-summary'],
    queryFn: statsApi.analyticsSummary
  })
  
  const { data: bestQualityData } = useQuery({
    queryKey: ['analytics-best-quality', selectedScenario],
    queryFn: () => analyticsApi.bestQualityPerAud({
      scenario: selectedScenario || undefined
    })
  })
  
  const views = [
    { id: 'research', name: 'Research Questions' },
    { id: 'statistical', name: 'Statistical Analysis' },
    { id: 'validation', name: 'Research Validation' },
    { id: 'advanced', name: 'Advanced Analytics' }
  ]



  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-bold text-gray-900">Advanced Analytics</h1>
        <p className="mt-2 text-gray-600">Statistical analysis and research validation</p>
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

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <ScenarioSelect />
          <ModelSelect />
          <LengthBinMulti />
          {selectedView === 'bias' && <RubricDimensionSelect />}
        </div>
      </div>

      {/* Research Analytics Views */}
      <div className="space-y-6">
        {selectedView === 'research' && (
          <div className="space-y-6">
            {/* Length Bias Analysis */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Length Bias Analysis</h3>
              <LengthBias />
            </div>

            {/* Distribution Validation */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Distribution Validation</h3>
              <KLDivergenceChart />
            </div>
          </div>
        )}

        {selectedView === 'statistical' && (
          <div className="space-y-6">
            {/* Statistical Testing */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Statistical Testing</h3>
              <LengthBias />
            </div>

            {/* Model Efficiency */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Model Efficiency</h3>
              {bestQualityData?.leaderboard && (
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
                      {bestQualityData.leaderboard.slice(0, 10).map((entry, index) => (
                        <tr key={entry.model_id} className={index % 2 === 0 ? 'bg-gray-50' : ''}>
                          <td className="py-2">{index + 1}</td>
                          <td className="py-2 font-medium">{entry.model_id}</td>
                          <td className="py-2 text-green-600 font-bold">{entry.quality_per_aud.toFixed(2)}</td>
                          <td className="py-2">{entry.avg_quality.toFixed(2)}</td>
                          <td className="py-2">${entry.avg_cost.toFixed(4)}</td>
                          <td className="py-2">{entry.count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {selectedView === 'validation' && (
          <div className="space-y-6">
            {/* Validation */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Validation</h3>
              <KLDivergenceChart />
            </div>

            {/* Coverage */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Coverage</h3>
              <PromptCoverageChart />
            </div>
          </div>
        )}

        {selectedView === 'advanced' && (
          <div className="space-y-6">
            {/* Risk Analysis */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Risk Analysis</h3>
              <RiskCurves />
            </div>
            
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Risk-Cost Frontier</h3>
              <RiskCostFrontier />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

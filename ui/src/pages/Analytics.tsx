import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { CostQualityChart } from '../components/Charts/CostQualityChart'
import { LengthBias } from '../components/Charts/LengthBias'
import { RiskCurves } from '../components/Charts/RiskCurves'
import { RiskCostFrontier } from '../components/Charts/RiskCostFrontier'
import { ModelSelect } from '../components/Filters/ModelSelect'
import { ScenarioSelect } from '../components/Filters/ScenarioSelect'
import { LengthBinMulti } from '../components/Filters/LengthBinMulti'
import { RubricDimensionSelect } from '../components/Filters/RubricDimensionSelect'
import { analyticsApi, statsApi } from '../api/client'
import { useFilters } from '../state/useFilters'

export function Analytics() {
  const [selectedView, setSelectedView] = useState('cost_quality')
  const { selectedScenario, selectedModels } = useFilters()
  
  // Fetch real analytics data
  const { data: statsData } = useQuery({
    queryKey: ['stats-analytics-summary'],
    queryFn: statsApi.analyticsSummary
  })
  
  const { data: costQualityData } = useQuery({
    queryKey: ['analytics-cost-quality', selectedScenario, selectedModels],
    queryFn: () => analyticsApi.costQuality({
      scenario: selectedScenario || undefined,
      model: selectedModels.length > 0 ? selectedModels.join(',') : undefined
    })
  })
  
  const { data: bestQualityData } = useQuery({
    queryKey: ['analytics-best-quality', selectedScenario],
    queryFn: () => analyticsApi.bestQualityPerAud({
      scenario: selectedScenario || undefined
    })
  })
  
  const views = [
    { id: 'cost_quality', name: 'Cost vs Quality', icon: '💰' },
    { id: 'risk_curves', name: 'Risk Curves', icon: '📈' },
    { id: 'length_bias', name: 'Length Bias', icon: '📏' },
    { id: 'leaderboard', name: 'Quality per AUD', icon: '🏆' }
  ]



  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-bold text-gray-900">Budget Optimizer</h1>
        <p className="mt-2 text-gray-600">
          Best value AI models - Interactive cost vs quality analysis for SOC/GRC AI decision-making. Find the most cost-effective models for your cybersecurity budget.
        </p>
        <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <span className="text-yellow-600 mr-2">⚠️</span>
            <div className="text-sm">
              <p className="font-medium text-yellow-800">Why Cost-Quality Matters in SOC/GRC:</p>
              <p className="text-yellow-700 mt-1">
                AI adoption in security operations is exploding, but without transparent benchmarking, 
                organizations risk overspending and failing compliance checks. Make data-driven decisions.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* View Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {views.map((view) => (
            <button
              key={view.id}
              onClick={() => setSelectedView(view.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                selectedView === view.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{view.icon}</span>
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
          {selectedView === 'length_bias' && <RubricDimensionSelect />}
        </div>
      </div>

      {/* Analytics Views */}
      <div className="space-y-6">
        {selectedView === 'cost_quality' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="lg:col-span-2 bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">💰 Cost vs Quality Analysis</h3>
              <p className="text-gray-600 mb-4">Interactive scatter plot showing cost-performance trade-offs</p>
              <CostQualityChart />
            </div>
            
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">💡 Cost-Quality Insights</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Best Value Model:</span>
                  <span className="font-medium">{statsData?.best_value_model || 'No data'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Highest Quality:</span>
                  <span className="font-medium">{statsData?.highest_quality_model || 'No data'} ({statsData?.highest_quality_score?.toFixed(1) || 'N/A'}/5.0)</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Lowest Cost:</span>
                  <span className="font-medium">{statsData?.lowest_cost_model || 'No data'} (${statsData?.lowest_cost_amount?.toFixed(4) || 'N/A'} AUD)</span>
                </div>
              </div>
            </div>
            
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">📊 Performance Summary</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Evaluations:</span>
                  <span className="font-medium">{statsData?.total_evaluations?.toLocaleString() || '0'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Avg Composite Score:</span>
                  <span className="font-medium">{statsData?.avg_composite_score?.toFixed(1) || 'No data'}/5.0</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Scenarios Covered:</span>
                  <span className="font-medium">{statsData?.scenarios_covered || '0'} Types</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedView === 'risk_curves' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RiskCurves className="lg:col-span-2" />
            <RiskCostFrontier className="lg:col-span-2" />
          </div>
        )}

        {selectedView === 'length_bias' && (
          <LengthBias />
        )}

        {selectedView === 'leaderboard' && (
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">🏆 Best Quality per AUD Leaderboard</h3>
            <p className="text-gray-600 mb-4">
              Models ranked by quality score per Australian dollar spent
            </p>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rank</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Model</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quality/AUD</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quality Score</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cost (AUD)</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {bestQualityData?.leaderboard?.length > 0 ? bestQualityData.leaderboard.map((item, index) => (
                    <tr key={item.model_id || index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        #{index + 1}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.model_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-green-600">
                        {item.quality_per_aud?.toFixed(1) || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.avg_quality?.toFixed(1) || 'N/A'}/5.0
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${item.avg_cost?.toFixed(4) || 'N/A'}
                      </td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                        No data available. Run some experiments first.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

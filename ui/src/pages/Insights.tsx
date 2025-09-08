import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { CostQualityChart } from '../components/Charts/CostQualityChart'
import { LengthBias } from '../components/Charts/LengthBias'
import { RiskCurves } from '../components/Charts/RiskCurves'
import { RiskCostFrontier } from '../components/Charts/RiskCostFrontier'
import { PromptCoverageChart } from '../components/Charts/PromptCoverageChart'
import { ModelSelect } from '../components/Filters/ModelSelect'
import { ScenarioSelect } from '../components/Filters/ScenarioSelect'
import { LengthBinMulti } from '../components/Filters/LengthBinMulti'
import { RubricDimensionSelect } from '../components/Filters/RubricDimensionSelect'
import { analyticsApi, statsApi } from '../api/client'
import { useFilters } from '../state/useFilters'

export function Insights() {
  const [selectedView, setSelectedView] = useState('cost_score')
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
    { id: 'cost_score', name: 'Cost vs Score', icon: '$' },
    { id: 'bias', name: 'Bias Analysis', icon: '|' },
    { id: 'risk', name: 'Risk Analysis', icon: '!' },
    { id: 'coverage', name: 'Coverage', icon: '#' }
  ]



  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-bold text-gray-900">Insights</h1>
        <p className="mt-2 text-gray-600">
          Advanced analytics and performance insights
        </p>
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
          {selectedView === 'bias' && <RubricDimensionSelect />}
        </div>
      </div>

      {/* Analytics Views */}
      <div className="space-y-6">
        {selectedView === 'cost_score' && (
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Cost vs Quality Analysis</h3>
            <p className="text-gray-600 mb-4">Interactive scatter plot showing cost-performance trade-offs</p>
            <CostQualityChart />
          </div>
        )}

        {selectedView === 'bias' && (
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Length Bias Analysis</h3>
            <p className="text-gray-600 mb-4">FSP vs raw scoring comparison</p>
            <LengthBias />
          </div>
        )}

        {selectedView === 'risk' && (
          <div className="space-y-6">
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Risk Curves Analysis</h3>
              <p className="text-gray-600 mb-4">
                Risk awareness and hallucination rates across prompt lengths
              </p>
              <RiskCurves />
            </div>
            
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Risk-Cost Frontier</h3>
              <p className="text-gray-600 mb-4">
                Optimal balance between cost efficiency and risk mitigation
              </p>
              <RiskCostFrontier />
            </div>
          </div>
        )}

        {selectedView === 'coverage' && (
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Prompt Coverage Analysis</h3>
            <p className="text-gray-600 mb-4">
              Track prompt usage across static and adaptive sources by scenario
            </p>
            <PromptCoverageChart />
          </div>
        )}


      </div>
    </div>
  )
}

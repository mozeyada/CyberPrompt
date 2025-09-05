import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { statsApi } from '../api/client'
import { ResultsTable } from '../components/Tables/ResultsTable'

export function Results() {
  const { data: statsData } = useQuery({
    queryKey: ['stats-analytics-summary'],
    queryFn: statsApi.analyticsSummary
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Evaluation Results
        </h1>
        <p className="text-gray-600">
          Security task outcomes - Comprehensive LLM evaluation results with 7-dimension rubric scoring, token costs, and bias-controlled analysis for cybersecurity operations
        </p>
        <div className="mt-4 flex items-center space-x-4 text-sm text-gray-500">
          <span className="flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            FSP Bias Mitigation Active
          </span>
          <span className="flex items-center">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
            Real-time Cost Tracking
          </span>
          <span className="flex items-center">
            <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
            7-Dimension Rubric
          </span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Runs</p>
              <p className="text-2xl font-bold text-gray-900">{statsData?.total_successful_runs || 0}</p>
            </div>
            <div className="text-3xl">📊</div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Cost</p>
              <p className="text-2xl font-bold text-gray-900">${statsData?.avg_cost_per_run?.toFixed(4) || '0.0000'}</p>
            </div>
            <div className="text-3xl">💰</div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Models Tested</p>
              <p className="text-2xl font-bold text-gray-900">{statsData?.models_tested || 0}</p>
            </div>
            <div className="text-3xl">🤖</div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Scenarios</p>
              <p className="text-2xl font-bold text-gray-900">{statsData?.scenarios_covered || 0}</p>
            </div>
            <div className="text-3xl">🛡️</div>
          </div>
        </div>
      </div>

      {/* Results Table */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Experiment Results</h3>
        <ResultsTable />
      </div>
    </div>
  )
}

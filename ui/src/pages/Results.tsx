import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { statsApi } from '../api/client'
import { ResultsTable } from '../components/Tables/ResultsTable'
import { Badge } from '../components/ui/badge'

export function Results() {
  const [selectedExperiment, setSelectedExperiment] = useState<string | null>(null)
  
  const { data: statsData } = useQuery({
    queryKey: ['stats-analytics-summary'],
    queryFn: statsApi.analyticsSummary
  })
  
  const { data: experiments } = useQuery({
    queryKey: ['experiments'],
    queryFn: () => fetch('http://localhost:8000/runs/experiments', {
      headers: { 'x-api-key': 'supersecret1' }
    }).then(res => res.json())
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

      {/* Experiments Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Experiments</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {experiments?.experiments?.map((exp: any) => (
            <div 
              key={exp.experiment_id}
              className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                selectedExperiment === exp.experiment_id 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedExperiment(
                selectedExperiment === exp.experiment_id ? null : exp.experiment_id
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-sm">{exp.experiment_id}</h4>
                <Badge variant="outline" className="text-xs">
                  {exp.run_count} runs
                </Badge>
              </div>
              <div className="space-y-1 text-xs text-gray-600">
                <div>Models: {exp.models.join(', ')}</div>
                <div>Dataset: {exp.dataset_version || 'Unknown'}</div>
                <div>Completed: {exp.completed_runs}/{exp.run_count}</div>
                <div>Avg Cost: ${exp.avg_cost.toFixed(4)}</div>
                <div>Created: {new Date(exp.created_at).toLocaleDateString()}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Results Table */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {selectedExperiment ? `Experiment: ${selectedExperiment}` : 'All Results'}
          </h3>
          {selectedExperiment && (
            <button
              onClick={() => setSelectedExperiment(null)}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Show All Results
            </button>
          )}
        </div>
        <ResultsTable experimentId={selectedExperiment} />
      </div>
    </div>
  )
}

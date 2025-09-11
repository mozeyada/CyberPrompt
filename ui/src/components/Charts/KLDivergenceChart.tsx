import React from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_KEY = import.meta.env.VITE_API_KEY || 'supersecret1'

interface KLDivergenceData {
  scenario_kl_divergence: number
  length_kl_divergence: number
  interpretation: {
    scenario_interpretation: string
    length_interpretation: string
    overall_assessment: string
  }
  static_count: number
  adaptive_count: number
}

export function KLDivergenceChart() {
  const { data, isLoading, error } = useQuery<KLDivergenceData>({
    queryKey: ['kl-divergence'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/validation/kl-divergence`, {
        headers: { 'x-api-key': API_KEY }
      })
      return response.data
    }
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading KL divergence analysis...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Error loading KL divergence data. Ensure you have both static and adaptive prompts.</p>
      </div>
    )
  }

  if (!data) return null

  const getScoreColor = (score: number) => {
    if (score < 0.5) return 'text-green-600 bg-green-50'
    if (score < 1.0) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getAssessmentColor = (assessment: string) => {
    if (assessment === 'Representative') return 'text-green-600 bg-green-50'
    return 'text-red-600 bg-red-50'
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="border rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-2">Scenario Distribution</h4>
          <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getScoreColor(data.scenario_kl_divergence)}`}>
            KL: {data.scenario_kl_divergence.toFixed(3)}
          </div>
          <p className="text-sm text-gray-600 mt-2">{data.interpretation.scenario_interpretation}</p>
        </div>

        <div className="border rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-2">Length Distribution</h4>
          <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getScoreColor(data.length_kl_divergence)}`}>
            KL: {data.length_kl_divergence.toFixed(3)}
          </div>
          <p className="text-sm text-gray-600 mt-2">{data.interpretation.length_interpretation}</p>
        </div>
      </div>

      {/* Overall Assessment */}
      <div className="border rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">Overall Assessment</h4>
        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getAssessmentColor(data.interpretation.overall_assessment)}`}>
          {data.interpretation.overall_assessment}
        </div>
        <div className="mt-3 text-sm text-gray-600">
          <p>Static prompts: {data.static_count} | Adaptive prompts: {data.adaptive_count}</p>
        </div>
      </div>

      {/* Interpretation Guide */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">Interpretation Guide</h4>
        <div className="text-sm text-gray-600 space-y-1">
          <p><span className="font-medium">KL &lt; 0.5:</span> Very similar distributions (good representativeness)</p>
          <p><span className="font-medium">KL 0.5-1.0:</span> Moderate differences (acceptable drift)</p>
          <p><span className="font-medium">KL &gt; 1.0:</span> Significant differences (potential bias)</p>
        </div>
      </div>
    </div>
  )
}
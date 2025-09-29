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
      <div className="text-center p-8 text-gray-500">
        <p>Need both CySecBench baseline and adaptive prompts to validate RQ2</p>
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
    <div className="space-y-4">
      <div className="text-center">
        <h4 className="text-lg font-medium mb-2">Benchmark Validation</h4>
        <p className="text-sm text-gray-600 mb-4">
          Comparing {data.static_count} CySecBench prompts vs {data.adaptive_count} adaptive prompts from CTI/policy docs
        </p>
        
        <div className={`inline-flex items-center px-4 py-2 rounded-lg text-lg font-medium ${
          data.interpretation.overall_assessment === 'Representative' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-red-100 text-red-800'
        }`}>
          {data.interpretation.overall_assessment === 'Representative' 
            ? 'PASS: Adaptive prompts maintain baseline distribution' 
            : 'FAIL: Adaptive prompts deviate from baseline distribution'
          }
        </div>
        
        <div className="mt-4 bg-gray-50 rounded-lg p-4">
          <div className="text-sm font-medium text-gray-700 mb-2">Statistical Analysis (KL Divergence)</div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">Scenario Coverage:</span>
              <span className={`ml-2 px-2 py-1 rounded text-xs ${
                data.scenario_kl_divergence < 0.5 ? 'bg-green-100 text-green-800' :
                data.scenario_kl_divergence < 1.0 ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {data.scenario_kl_divergence.toFixed(2)}
              </span>
            </div>
            <div>
              <span className="font-medium">Length Distribution:</span>
              <span className={`ml-2 px-2 py-1 rounded text-xs ${
                data.length_kl_divergence < 0.5 ? 'bg-green-100 text-green-800' :
                data.length_kl_divergence < 1.0 ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {data.length_kl_divergence.toFixed(2)}
              </span>
            </div>
          </div>
          <div className="mt-3 text-xs text-gray-600">
            <strong>Research Question 2:</strong> Can adaptive benchmarking maintain coverage without introducing bias?
            <br />
            <strong>Interpretation:</strong> Values &lt;0.5 = Good match, 0.5-1.0 = Acceptable, &gt;1.0 = Significant drift
          </div>
        </div>
        
        {(data.scenario_kl_divergence > 1.0 || data.length_kl_divergence > 1.0) && (
          <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="text-sm font-medium text-yellow-800">Recommendation</div>
            <div className="text-sm text-yellow-700 mt-1">
              Adaptive prompt generation requires tuning to better match baseline distribution patterns
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
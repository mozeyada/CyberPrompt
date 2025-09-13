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
            ? '✅ Adaptive prompts are representative' 
            : '❌ Adaptive prompts drift from baseline'
          }
        </div>
        
        <div className="mt-3 text-xs text-gray-500">
          KL divergence: Scenarios {data.scenario_kl_divergence.toFixed(2)} | Lengths {data.length_kl_divergence.toFixed(2)}
          <br />
          Validates RQ2: Can adaptive benchmarking maintain coverage without bias?
        </div>
        
        {(data.scenario_kl_divergence > 1.0 || data.length_kl_divergence > 1.0) && (
          <div className="mt-3 text-sm text-red-600">
            ⚠️ Adaptive generation may need tuning to match baseline distribution
          </div>
        )}
      </div>
    </div>
  )
}
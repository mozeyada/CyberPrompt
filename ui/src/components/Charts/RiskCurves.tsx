import { useQuery } from '@tanstack/react-query'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts'
import { analyticsApi } from '../../api/client'
import { useFilters } from '../../state/useFilters'

interface RiskCurvesProps {
  className?: string
}

export function RiskCurves({ className = "" }: RiskCurvesProps) {
  const { selectedScenario, selectedModels } = useFilters()

  const { data, isLoading, error } = useQuery({
    queryKey: ['risk_curves', selectedScenario, selectedModels],
    queryFn: async () => {
      return analyticsApi.riskCurves({
        scenario: selectedScenario || undefined,
        model: selectedModels.length > 0 ? selectedModels.join(',') : undefined,
      })
    },
  })

  if (isLoading) {
    return (
      <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
        <h3 className="text-lg font-semibold mb-4">Risk Curves</h3>
        <div className="h-80 flex items-center justify-center">
          <div className="animate-pulse text-gray-500">Loading...</div>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
        <h3 className="text-lg font-semibold mb-4">Risk Curves</h3>
        <div className="h-80 flex items-center justify-center">
          <div className="text-red-500">Error loading data</div>
        </div>
      </div>
    )
  }

  return (
    <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Risk Awareness & Hallucination Rates</h3>
        <div className="text-sm text-gray-500">
          vs Length Bins
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data.length_bins || []}>
          <XAxis dataKey="length_bin" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="risk_awareness" 
            stroke="#10B981" 
            strokeWidth={2}
            name="Risk Awareness"
          />
          <Line 
            type="monotone" 
            dataKey="hallucination_rate" 
            stroke="#EF4444" 
            strokeWidth={2}
            name="Hallucination Rate"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
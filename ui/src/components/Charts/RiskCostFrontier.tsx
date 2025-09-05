import { useQuery } from '@tanstack/react-query'
import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, Tooltip, Legend } from 'recharts'
import { analyticsApi } from '../../api/client'
import { useFilters } from '../../state/useFilters'

interface RiskCostFrontierProps {
  className?: string
}

export function RiskCostFrontier({ className = "" }: RiskCostFrontierProps) {
  const { selectedScenario, selectedModels } = useFilters()

  const { data, isLoading, error } = useQuery({
    queryKey: ['risk_cost', selectedScenario, selectedModels],
    queryFn: async () => {
      return analyticsApi.riskCost({
        scenario: selectedScenario || undefined,
        model: selectedModels.length > 0 ? selectedModels : undefined,
      })
    },
  })

  if (isLoading) {
    return (
      <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
        <h3 className="text-lg font-semibold mb-4">Risk-Cost Frontier</h3>
        <div className="h-80 flex items-center justify-center">
          <div className="animate-pulse text-gray-500">Loading...</div>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
        <h3 className="text-lg font-semibold mb-4">Risk-Cost Frontier</h3>
        <div className="h-80 flex items-center justify-center">
          <div className="text-red-500">Error loading data</div>
        </div>
      </div>
    )
  }

  return (
    <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Risk-Cost Frontier</h3>
        <div className="text-sm text-gray-500">
          Lower-left is better (low cost, low risk)
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart>
          <XAxis 
            type="number" 
            dataKey="x" 
            name="AUD / 1K tokens"
            domain={['dataMin - 0.0001', 'dataMax + 0.0001']}
          />
          <YAxis 
            type="number" 
            dataKey="y" 
            name="Risk Score"
            domain={[0, 1]}
          />
          <Tooltip 
            content={({ active, payload }) => {
              if (active && payload && payload.length > 0) {
                const data = payload[0].payload
                return (
                  <div className="bg-white p-3 rounded-lg shadow-lg border">
                    <p className="font-medium">{data.model}</p>
                    <p className="text-sm">Cost: ${data.x.toFixed(4)} AUD/1K</p>
                    <p className="text-sm">Risk: {(data.y * 100).toFixed(1)}%</p>
                    <p className="text-sm">Hallucinations: {data.hallucination_rate}%</p>
                  </div>
                )
              }
              return null
            }}
          />
          <Legend />
          <Scatter 
            data={data.risk_cost_frontier || []} 
            fill="#3B82F6"
            name="Models"
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}
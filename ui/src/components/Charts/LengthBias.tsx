import { useQuery } from '@tanstack/react-query'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, Cell } from 'recharts'
import { analyticsApi } from '../../api/client'
import { useFilters } from '../../state/useFilters'

interface LengthBiasProps {
  className?: string
}

export function LengthBias({ className = "" }: LengthBiasProps) {
  const { selectedScenario, selectedModels, selectedDimension } = useFilters()

  const { data, isLoading, error } = useQuery({
    queryKey: ['length_bias', selectedScenario, selectedModels, selectedDimension],
    queryFn: async () => {
      return analyticsApi.lengthBias({
        scenario: selectedScenario || undefined,
        model: selectedModels.length > 0 ? selectedModels.join(',') : undefined,
        dimension: selectedDimension,
      })
    },
  })

  if (isLoading) {
    return (
      <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
        <h3 className="text-lg font-semibold mb-4">Length Bias Analysis</h3>
        <div className="h-80 flex items-center justify-center">
          <div className="animate-pulse text-gray-500">Loading...</div>
        </div>
      </div>
    )
  }

  if (error || !data || !data.slopes || data.slopes.length === 0) {
    return (
      <div className="text-center p-8">
        <div className="text-gray-500 mb-2">No length bias data available</div>
        <div className="text-sm text-gray-400">Run experiments with different prompt lengths to see bias analysis</div>
      </div>
    )
  }

  // Transform slopes data for visualization
  const chartData = data.slopes.map((modelData: any) => ({
    model: modelData.model,
    slope: modelData.slope,
    r_squared: modelData.r_squared,
    p_value: modelData.p_value,
    significance: modelData.p_value < 0.05 ? 'Significant' : 'Not Significant'
  }))

  return (
    <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Length Bias Analysis</h3>
        <div className="text-sm text-gray-500">
          {selectedDimension.replace('_', ' ')}
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={chartData}>
          <XAxis dataKey="model" />
          <YAxis label={{ value: 'Bias Slope', angle: -90, position: 'insideLeft' }} />
          <Tooltip 
            formatter={(value: any, name: string) => {
              if (name === 'slope') return [value.toFixed(4), 'Bias Slope']
              return [value, name]
            }}
            labelFormatter={(label) => `Model: ${label}`}
          />
          <Legend />
          <Bar dataKey="slope" name="Length Bias Slope">
            {chartData.map((entry: any, index: number) => (
              <Cell key={`cell-${index}`} fill={entry.significance === 'Significant' ? '#EF4444' : '#6B7280'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      
      {/* Interpretation */}
      <div className="mt-4 text-sm text-gray-600">
        <p><strong>Red bars:</strong> Statistically significant bias (p &lt; 0.05)</p>
        <p><strong>Gray bars:</strong> No significant bias detected</p>
        <p><strong>Positive slope:</strong> Longer prompts get higher scores</p>
      </div>
    </div>
  )
}
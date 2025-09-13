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
        <div className="text-sm text-gray-400 mb-4">Run experiments with different prompt lengths to see bias analysis</div>
        <div className="text-xs text-gray-500">
          Need S/M/L length variants for bias analysis
        </div>
      </div>
    )
  }

  // Transform slopes data for visualization
  const chartData = data.slopes.map((modelData: any) => ({
    model: modelData.model,
    slope: modelData.slope,
    r_squared: modelData.r_squared,
    p_value: modelData.p_value,
    significance: modelData.p_value < 0.05 ? 'Significant' : 'Not Significant',
    slope_ci_lower: modelData.slope_ci_lower,
    slope_ci_upper: modelData.slope_ci_upper,
    effect_size: Math.abs(modelData.slope) > 0.1 ? 'Large' : Math.abs(modelData.slope) > 0.05 ? 'Medium' : 'Small'
  }))

  return (
    <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Length Bias Analysis</h3>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">
            {selectedDimension.replace('_', ' ')}
          </span>
          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
            RQ1 Analysis
          </span>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={chartData}>
          <XAxis dataKey="model" />
          <YAxis label={{ value: 'Bias Slope', angle: -90, position: 'insideLeft' }} />
          <Tooltip 
            content={({ active, payload, label }) => {
              if (active && payload && payload[0]) {
                const data = payload[0].payload
                return (
                  <div className="bg-white p-3 border rounded shadow-lg">
                    <div className="font-medium mb-2">{label}</div>
                    <div className="text-sm space-y-1">
                      <div>Slope: <strong>{data.slope.toFixed(4)}</strong></div>
                      <div>95% CI: [{data.slope_ci_lower?.toFixed(4)}, {data.slope_ci_upper?.toFixed(4)}]</div>
                      <div>R²: <strong>{data.r_squared.toFixed(3)}</strong></div>
                      <div>p-value: <strong>{data.p_value.toFixed(6)}</strong></div>
                      <div>Effect: <strong>{data.effect_size}</strong></div>
                      <div className={`font-medium ${
                        data.significance === 'Significant' ? 'text-red-600' : 'text-gray-600'
                      }`}>
                        {data.significance}
                      </div>
                    </div>
                  </div>
                )
              }
              return null
            }}
          />
          <Legend />
          <Bar dataKey="slope" name="Length Bias Slope">
            {chartData.map((entry: any, index: number) => (
              <Cell key={`cell-${index}`} fill={entry.significance === 'Significant' ? '#EF4444' : '#6B7280'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      
      {/* Quick Interpretation */}
      <div className="mt-4 bg-gray-50 p-3 rounded text-xs text-gray-600">
        <p><strong>Red:</strong> Significant bias (p&lt;0.05) | <strong>Gray:</strong> No bias | <strong>Positive:</strong> Longer=higher scores</p>
        {chartData.some(d => d.significance === 'Significant') && (
          <p className="text-yellow-700 mt-1">⚠️ {chartData.filter(d => d.significance === 'Significant').length} model(s) show significant bias - consider FSP</p>
        )}
      </div>
    </div>
  )
}
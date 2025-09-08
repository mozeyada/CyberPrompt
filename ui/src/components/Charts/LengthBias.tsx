import { useQuery } from '@tanstack/react-query'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts'
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

  if (error || !data) {
    return (
      <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
        <h3 className="text-lg font-semibold mb-4">Length Bias Analysis</h3>
        <div className="h-80 flex items-center justify-center">
          <div className="text-red-500">Error loading data</div>
        </div>
      </div>
    )
  }

  return (
    <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Length Bias Analysis</h3>
        <div className="text-sm text-gray-500">
          {selectedDimension.replace('_', ' ')}
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data.bins || []}>
          <XAxis dataKey="length_bin" />
          <YAxis domain={[0, 5]} />
          <Tooltip />
          <Legend />
          {data.slopes?.map((model: any, index: number) => (
            <Line 
              key={model.model}
              type="monotone" 
              dataKey={model.model}
              stroke={`hsl(${index * 60}, 70%, 50%)`}
              strokeWidth={2}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
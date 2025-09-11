import { useQuery } from '@tanstack/react-query'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { analyticsApi } from '../../api/client'

const MODEL_COLORS = {
  'gpt-4o': '#3B82F6',
  'gpt-3.5-turbo': '#10B981', 
  'claude-3-5-sonnet': '#8B5CF6',
  'gemini-2.5-flash': '#F59E0B'
}

export function useCostQualityData() {
  return useQuery({
    queryKey: ['cost-quality-scatter'],
    queryFn: analyticsApi.costQualityScatter,
    retry: 1,
    staleTime: 30000
  })
}

export function CostQualityChart() {
  const { data, isLoading, error } = useCostQualityData()

  if (isLoading) {
    return <div className="flex justify-center items-center h-64">Loading chart...</div>
  }

  if (error) {
    return <div className="text-red-600 p-4">Error loading chart data</div>
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-center p-8">
        <div className="text-gray-500 mb-2">No cost-quality data available</div>
        <div className="text-sm text-gray-400">Run some experiments first to see analytics</div>
      </div>
    )
  }

  // Group data by model
  const groupedData = data.reduce((acc, point) => {
    if (!acc[point.model]) {
      acc[point.model] = []
    }
    acc[point.model].push({
      x: point.aud_cost,
      y: point.composite_score,
      run_id: point.run_id,
      model: point.model
    })
    return acc
  }, {} as Record<string, Array<{x: number, y: number, run_id: string, model: string}>>)

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 border rounded shadow">
          <p className="font-medium">{data.model}</p>
          <p>Cost: ${data.x.toFixed(4)} AUD</p>
          <p>Quality: {data.y.toFixed(1)}/5.0</p>
          <p className="text-xs text-gray-500">Run: {data.run_id.slice(-8)}</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-96">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            type="number" 
            dataKey="x" 
            name="Cost (AUD)"
            label={{ value: 'Cost (AUD)', position: 'insideBottom', offset: -10 }}
          />
          <YAxis 
            type="number" 
            dataKey="y" 
            name="Quality Score"
            domain={[0, 5]}
            label={{ value: 'Quality Score', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          {Object.entries(groupedData).map(([model, points]) => (
            <Scatter
              key={model}
              name={model}
              data={points}
              fill={MODEL_COLORS[model as keyof typeof MODEL_COLORS] || '#6B7280'}
            />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}
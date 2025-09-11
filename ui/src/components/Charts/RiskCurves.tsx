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

  if (error || !data || !data.risk_curves) {
    return (
      <div className="text-center p-8">
        <div className="text-gray-500 mb-2">No risk analysis data available</div>
        <div className="text-sm text-gray-400">Run experiments to see risk awareness and hallucination analysis</div>
      </div>
    )
  }

  // Transform risk curves data for visualization
  const models = Object.keys(data.risk_curves)
  if (models.length === 0) {
    return (
      <div className="text-center p-8">
        <div className="text-gray-500 mb-2">No risk curves data available</div>
        <div className="text-sm text-gray-400">Need risk_awareness scores in your runs</div>
      </div>
    )
  }

  // Create chart data by combining all models' risk awareness data
  const chartData: any[] = []
  const lengthBins = ['XS', 'S', 'M', 'L', 'XL']
  
  lengthBins.forEach(bin => {
    const dataPoint: any = { length_bin: bin }
    models.forEach(model => {
      const riskData = data.risk_curves[model]?.risk_awareness?.find((item: any) => item.length_bin === bin)
      if (riskData) {
        dataPoint[model] = riskData.value
      }
    })
    if (Object.keys(dataPoint).length > 1) { // Has data beyond just length_bin
      chartData.push(dataPoint)
    }
  })

  return (
    <div className={`rounded-2xl shadow-lg p-6 bg-white ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Risk Awareness & Hallucination Rates</h3>
        <div className="text-sm text-gray-500">
          vs Length Bins
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <XAxis dataKey="length_bin" />
          <YAxis domain={[0, 5]} label={{ value: 'Risk Awareness Score', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          {models.map((model, index) => (
            <Line 
              key={model}
              type="monotone" 
              dataKey={model}
              stroke={`hsl(${index * 60}, 70%, 50%)`}
              strokeWidth={2}
              name={model}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
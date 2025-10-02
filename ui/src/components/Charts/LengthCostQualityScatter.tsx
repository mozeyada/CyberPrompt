import { useQuery } from '@tanstack/react-query'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { runsApi } from '../../api/client'

const LENGTH_BIN_COLORS = {
  S: '#10B981', // Green - Short
  M: '#3B82F6', // Blue - Medium
  L: '#F59E0B'  // Amber - Long
}

const LENGTH_BIN_LABELS = {
  S: 'Short (268-362 tokens)',
  M: 'Medium (379-485 tokens)',
  L: 'Long (616-721 tokens)'
}

export function LengthCostQualityScatter() {
  const { data: runsData, isLoading, error } = useQuery({
    queryKey: ['runs-scatter-length'],
    queryFn: () => runsApi.list({ limit: 200 }),
    retry: 1,
    staleTime: 30000
  })

  if (isLoading) {
    return <div className="flex justify-center items-center h-64">Loading scatter plot...</div>
  }

  if (error) {
    return <div className="text-red-600 p-4">Error loading chart data</div>
  }

  const runs = runsData?.runs || []
  const successfulRuns = runs.filter(run =>
    run.status === 'succeeded' &&
    run.scores?.composite > 0 &&
    run.prompt_length_bin
  )

  if (successfulRuns.length === 0) {
    return (
      <div className="text-center p-8">
        <div className="text-gray-500 mb-2">No cost-quality data available</div>
        <div className="text-sm text-gray-400">Run some experiments first to see analytics</div>
      </div>
    )
  }

  // Group by length bin
  const groupedData = successfulRuns.reduce((acc, run) => {
    const bin = run.prompt_length_bin as 'S' | 'M' | 'L'
    if (!bin) return acc

    if (!acc[bin]) {
      acc[bin] = []
    }

    acc[bin].push({
      x: run.economics.aud_cost,
      y: run.scores.composite,
      run_id: run.run_id,
      model: run.model,
      length_bin: bin,
      tokens: run.tokens.total
    })

    return acc
  }, {} as Record<string, Array<{
    x: number,
    y: number,
    run_id: string,
    model: string,
    length_bin: string,
    tokens: number
  }>>)

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 border rounded shadow">
          <p className="font-medium text-sm mb-1">{LENGTH_BIN_LABELS[data.length_bin as keyof typeof LENGTH_BIN_LABELS]}</p>
          <p className="text-sm">Model: {data.model}</p>
          <p className="text-sm">Cost: ${data.x.toFixed(4)} AUD</p>
          <p className="text-sm">Quality: {data.y.toFixed(2)}/5.0</p>
          <p className="text-sm">Tokens: {data.tokens}</p>
          <p className="text-xs text-gray-500 mt-1">Run: {data.run_id.slice(-8)}</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-96">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 60 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            type="number"
            dataKey="x"
            name="Cost (AUD)"
            label={{
              value: 'Cost per Inference (AUD)',
              position: 'insideBottom',
              offset: -15,
              style: { fontSize: 14, fontWeight: 500 }
            }}
            tickFormatter={(value) => `$${value.toFixed(4)}`}
          />
          <YAxis
            type="number"
            dataKey="y"
            name="Quality Score"
            domain={[0, 5]}
            label={{
              value: 'Quality Score (0-5)',
              angle: -90,
              position: 'insideLeft',
              offset: 10,
              style: { fontSize: 14, fontWeight: 500 }
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            height={36}
            formatter={(value) => LENGTH_BIN_LABELS[value as keyof typeof LENGTH_BIN_LABELS] || value}
          />
          {Object.entries(groupedData).sort((a, b) => {
            const order = { S: 0, M: 1, L: 2 }
            return order[a[0] as 'S' | 'M' | 'L'] - order[b[0] as 'S' | 'M' | 'L']
          }).map(([bin, points]) => (
            <Scatter
              key={bin}
              name={bin}
              data={points}
              fill={LENGTH_BIN_COLORS[bin as keyof typeof LENGTH_BIN_COLORS]}
              shape="circle"
            />
          ))}
        </ScatterChart>
      </ResponsiveContainer>

      {/* Interpretation Guide */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        <div className="bg-green-50 border border-green-200 p-3 rounded">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: LENGTH_BIN_COLORS.S }}></div>
            <strong className="text-green-900">Short Prompts</strong>
          </div>
          <p className="text-green-800">Lowest cost, but may lack detail. Best for simple queries.</p>
        </div>
        <div className="bg-blue-50 border border-blue-200 p-3 rounded">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: LENGTH_BIN_COLORS.M }}></div>
            <strong className="text-blue-900">Medium Prompts</strong>
          </div>
          <p className="text-blue-800">Balance of cost and quality. Often the "sweet spot".</p>
        </div>
        <div className="bg-amber-50 border border-amber-200 p-3 rounded">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: LENGTH_BIN_COLORS.L }}></div>
            <strong className="text-amber-900">Long Prompts</strong>
          </div>
          <p className="text-amber-800">Highest cost. Check if quality gains justify the expense.</p>
        </div>
      </div>
    </div>
  )
}

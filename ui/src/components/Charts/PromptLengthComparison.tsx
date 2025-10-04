import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { runsApi } from '../../api/client'

const LENGTH_BIN_COLORS = {
  S: '#10B981', // Green - Short
  M: '#3B82F6', // Blue - Medium
  L: '#F59E0B'  // Amber - Long
}

const LENGTH_BIN_LABELS = {
  S: 'Short (250-350 tokens)',
  M: 'Medium (350-500 tokens)',
  L: 'Long (600-750 tokens)'
}

interface LengthStats {
  length_bin: 'S' | 'M' | 'L'
  avg_quality: number
  avg_cost: number
  avg_tokens: number
  quality_per_dollar: number
  count: number
}

export function PromptLengthComparison() {
  const { data: runsData, isLoading, error } = useQuery({
    queryKey: ['runs-length-analysis'],
    queryFn: () => runsApi.list({ limit: 200 }),
    retry: 1,
    staleTime: 30000
  })

  if (isLoading) {
    return <div className="flex justify-center items-center h-64">Loading length comparison...</div>
  }

  if (error) {
    return <div className="text-red-600 p-4">Error loading data</div>
  }

  const runs = runsData?.runs || []
  const successfulRuns = runs.filter(run => run.status === 'succeeded' && run.scores?.composite > 0)

  if (successfulRuns.length === 0) {
    return (
      <div className="text-center p-8">
        <div className="text-gray-500 mb-2">No data available</div>
        <div className="text-sm text-gray-400">Run experiments with S/M/L prompts to see comparison</div>
      </div>
    )
  }

  // Aggregate by length bin
  const lengthGroups = successfulRuns.reduce((acc, run) => {
    const bin = run.prompt_length_bin as 'S' | 'M' | 'L'
    if (!bin) return acc

    if (!acc[bin]) {
      acc[bin] = {
        totalQuality: 0,
        totalCost: 0,
        totalPromptTokens: 0,
        count: 0
      }
    }

    acc[bin].totalQuality += run.scores.composite
    acc[bin].totalCost += run.economics.aud_cost
    // Use prompt token_count (the actual prompt length), not total tokens
    acc[bin].totalPromptTokens += run.prompt?.token_count || run.tokens.input
    acc[bin].count += 1

    return acc
  }, {} as Record<string, { totalQuality: number, totalCost: number, totalPromptTokens: number, count: number }>)

  // Calculate averages and metrics
  const lengthStats: LengthStats[] = Object.entries(lengthGroups).map(([bin, stats]) => {
    const avg_quality = stats.totalQuality / stats.count
    const avg_cost = stats.totalCost / stats.count
    const avg_tokens = stats.totalPromptTokens / stats.count
    const quality_per_dollar = avg_quality / avg_cost

    return {
      length_bin: bin as 'S' | 'M' | 'L',
      avg_quality,
      avg_cost,
      avg_tokens,
      quality_per_dollar,
      count: stats.count
    }
  }).sort((a, b) => {
    const order = { S: 0, M: 1, L: 2 }
    return order[a.length_bin] - order[b.length_bin]
  })

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 border rounded shadow">
          <p className="font-medium">{LENGTH_BIN_LABELS[data.length_bin as keyof typeof LENGTH_BIN_LABELS]}</p>
          <p className="text-sm text-gray-600">n = {data.count} runs</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-8">
      {/* Quality Comparison */}
      <div>
        <h4 className="text-md font-semibold mb-3 text-gray-800">Average Quality Score by Prompt Length</h4>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={lengthStats} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="length_bin"
              tickFormatter={(value) => `${value} (~${lengthStats.find(s => s.length_bin === value)?.avg_tokens.toFixed(0)} prompt tokens)`}
            />
            <YAxis
              domain={[0, 5]}
              label={{ value: 'Quality Score (0-5)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="avg_quality" name="Avg Quality" radius={[8, 8, 0, 0]}>
              {lengthStats.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={LENGTH_BIN_COLORS[entry.length_bin]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-2 text-sm text-gray-600 bg-gray-50 p-3 rounded">
          {lengthStats.map(stat => (
            <div key={stat.length_bin}>
              <strong>{stat.length_bin}:</strong> {stat.avg_quality.toFixed(2)}/5.0 quality ({stat.avg_tokens.toFixed(0)} prompt tokens avg, {stat.count} runs)
            </div>
          ))}
        </div>
      </div>

      {/* Cost Comparison */}
      <div>
        <h4 className="text-md font-semibold mb-3 text-gray-800">Average Cost by Prompt Length</h4>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={lengthStats} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="length_bin"
              tickFormatter={(value) => `${value} (~${lengthStats.find(s => s.length_bin === value)?.avg_tokens.toFixed(0)} prompt tokens)`}
            />
            <YAxis
              label={{ value: 'Cost (AUD)', angle: -90, position: 'insideLeft' }}
              tickFormatter={(value) => `$${value.toFixed(4)}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="avg_cost" name="Avg Cost" radius={[8, 8, 0, 0]}>
              {lengthStats.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={LENGTH_BIN_COLORS[entry.length_bin]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-2 text-sm text-gray-600 bg-gray-50 p-3 rounded">
          {lengthStats.map(stat => (
            <div key={stat.length_bin}>
              <strong>{stat.length_bin}:</strong> ${stat.avg_cost.toFixed(4)} AUD average cost ({stat.avg_tokens.toFixed(0)} prompt tokens)
            </div>
          ))}
        </div>
      </div>

      {/* Cost-Efficiency Comparison - MOST IMPORTANT */}
      <div className="border-2 border-blue-200 rounded-lg p-4">
        <h4 className="text-md font-semibold mb-3 text-gray-800">Cost-Efficiency: Quality per Dollar</h4>
        <p className="text-sm text-gray-600 mb-3">Higher is better - shows which length provides best value</p>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={lengthStats} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="length_bin"
              tickFormatter={(value) => `${value} (~${lengthStats.find(s => s.length_bin === value)?.avg_tokens.toFixed(0)} prompt tokens)`}
            />
            <YAxis
              label={{ value: 'Quality Points per Dollar', angle: -90, position: 'insideLeft' }}
              tickFormatter={(value) => value.toFixed(0)}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="quality_per_dollar" name="Quality/$" radius={[8, 8, 0, 0]}>
              {lengthStats.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={LENGTH_BIN_COLORS[entry.length_bin]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-2 text-sm text-gray-600 bg-blue-50 p-3 rounded border border-blue-200">
          <strong className="text-blue-900">Value Comparison:</strong>
          {lengthStats.map(stat => (
            <div key={stat.length_bin}>
              <strong>{stat.length_bin} ({stat.avg_tokens.toFixed(0)} tokens):</strong> {stat.quality_per_dollar.toFixed(0)} quality points per dollar
              {stat.quality_per_dollar === Math.max(...lengthStats.map(s => s.quality_per_dollar)) &&
                <span className="ml-2 text-green-700 font-bold">← BEST VALUE</span>
              }
            </div>
          ))}
        </div>
      </div>

      {/* Summary Stats Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 border">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Length Bin</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Quality</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Cost</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Tokens</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quality/$</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Runs</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {lengthStats.map((stat) => (
              <tr key={stat.length_bin}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className="px-3 py-1 rounded-full text-white font-semibold"
                    style={{ backgroundColor: LENGTH_BIN_COLORS[stat.length_bin] }}
                  >
                    {stat.length_bin}
                  </span>
                  <span className="ml-2 text-sm text-gray-600">
                    {LENGTH_BIN_LABELS[stat.length_bin]}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{stat.avg_quality.toFixed(2)}/5.0</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">${stat.avg_cost.toFixed(4)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{stat.avg_tokens.toFixed(0)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">
                  {stat.quality_per_dollar.toFixed(0)}
                  {stat.quality_per_dollar === Math.max(...lengthStats.map(s => s.quality_per_dollar)) &&
                    <span className="ml-2 text-green-700">★</span>
                  }
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{stat.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

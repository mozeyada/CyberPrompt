import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { runsApi } from '../../api/client'
import { useFilters } from '../../state/useFilters'

const LENGTH_COLORS = { S: '#10B981', M: '#3B82F6', L: '#F59E0B' }

export function CombinedLengthAnalysis() {
  const { selectedScenario, selectedModels } = useFilters()
  
  const { data: runsData, isLoading } = useQuery({
    queryKey: ['runs-length-combined', selectedScenario, selectedModels],
    queryFn: () => runsApi.list({ 
      limit: 200,
      ...(selectedScenario && { scenario: selectedScenario }),
      ...(selectedModels.length > 0 && { models: selectedModels.join(',') })
    }),
    staleTime: 30000
  })

  if (isLoading) return <div className="flex justify-center items-center h-64">Loading...</div>

  // Filters already applied in API query, just filter by status
  const runs = runsData?.runs?.filter(r => r.status === 'succeeded' && r.scores?.composite > 0) || []
  if (runs.length === 0) {
    return <div className="text-center p-8 text-gray-500">Run S/M/L experiments to see analysis</div>
  }

  // Aggregate by length
  const stats = runs.reduce((acc, r) => {
    const bin = r.prompt_length_bin as 'S' | 'M' | 'L'
    if (!bin) return acc
    if (!acc[bin]) acc[bin] = { quality: 0, cost: 0, count: 0 }
    acc[bin].quality += r.scores.composite
    acc[bin].cost += r.economics.aud_cost
    acc[bin].count += 1
    return acc
  }, {} as Record<string, { quality: number; cost: number; count: number }>)

  const data = Object.entries(stats).map(([bin, s]) => {
    const avgQuality = s.quality / s.count
    const avgCost = s.cost / s.count
    return {
      bin,
      quality: avgQuality,
      cost: avgCost,
      // Cost per quality point (lower is better)
      costPerQuality: avgCost / avgQuality,
      // Relative efficiency (higher is better)
      rawEfficiency: avgQuality / avgCost,
      count: s.count
    }
  }).sort((a, b) => ({ S: 0, M: 1, L: 2 }[a.bin] || 0) - ({ S: 0, M: 1, L: 2 }[b.bin] || 0))

  // Calculate relative efficiency index (0-100%)
  const maxRawEfficiency = Math.max(...data.map(d => d.rawEfficiency))
  data.forEach(d => {
    d.efficiency = (d.rawEfficiency / maxRawEfficiency) * 100
  })

  const maxEfficiency = Math.max(...data.map(d => d.efficiency))

  // Calculate insights
  const bestLength = data.find(d => d.efficiency === maxEfficiency)
  const worstLength = data.reduce((min, d) => d.efficiency < min.efficiency ? d : min)
  const qualityDiff = ((bestLength.quality - worstLength.quality) / worstLength.quality * 100).toFixed(1)
  const costDiff = ((worstLength.cost - bestLength.cost) / bestLength.cost * 100).toFixed(1)
  const efficiencyDiff = ((bestLength.efficiency - worstLength.efficiency)).toFixed(1)

  return (
    <div className="space-y-6">
      {/* EXECUTIVE SUMMARY */}
      <div className="bg-gradient-to-r from-blue-50 to-blue-100 border-2 border-blue-500 rounded-lg p-6">
        <div className="flex items-start gap-4">
          <div className="text-4xl">💡</div>
          <div className="flex-1">
            <h4 className="text-xl font-bold text-blue-900 mb-3">Key Finding</h4>
            <p className="text-lg text-blue-900 mb-2">
              <strong>{bestLength.bin} prompts are the sweet spot:</strong>
            </p>
            <ul className="text-base text-blue-800 space-y-2 ml-4">
              <li>✓ Achieve <strong>{bestLength.quality.toFixed(2)}/5.0</strong> quality ({(bestLength.quality/5*100).toFixed(0)}%)</li>
              <li>✓ Cost only <strong>${bestLength.cost.toFixed(4)}</strong> per query</li>
              <li>✓ <strong>{efficiencyDiff}%</strong> more efficient than {worstLength.bin} prompts</li>
            </ul>
            <div className="mt-4 p-3 bg-white rounded border border-blue-300">
              <p className="text-sm text-gray-700">
                <strong>Bottom line:</strong> {worstLength.bin} prompts cost {costDiff}% more but only improve quality by {qualityDiff}% - not worth it!
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* PRIMARY FINDING: RQ1 Answer */}
      <div className="border border-gray-300 rounded-lg p-6 bg-white">
        <h4 className="text-lg font-semibold mb-2 text-gray-900">Cost-Efficiency Comparison</h4>
        <p className="text-sm text-gray-600 mb-4">Which prompt length gives you the best value for money?</p>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} margin={{ top: 10, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="bin" label={{ value: 'Prompt Length', position: 'insideBottom', offset: -10 }} />
            <YAxis label={{ value: 'Efficiency Index (%)', angle: -90, position: 'insideLeft' }} />
            <Tooltip content={({ active, payload }) => {
              if (!active || !payload?.[0]) return null
              const d = payload[0].payload
              return (
                <div className="bg-white p-3 border rounded shadow">
                  <p className="font-bold">{d.bin} Prompts</p>
                  <p className="text-sm">Efficiency: <strong>{d.efficiency.toFixed(1)}%</strong></p>
                  <p className="text-sm">Quality: {d.quality.toFixed(2)}/5.0</p>
                  <p className="text-sm">Cost: ${d.cost.toFixed(4)} AUD</p>
                  <p className="text-sm">Cost/Quality: ${d.costPerQuality.toFixed(5)}</p>
                  <p className="text-xs text-gray-600 mt-1">n={d.count} runs</p>
                </div>
              )
            }} />
            <Bar dataKey="efficiency" radius={[8, 8, 0, 0]}>
              {data.map((d, i) => (
                <Cell key={i} fill={LENGTH_COLORS[d.bin as keyof typeof LENGTH_COLORS]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-3 bg-gray-50 p-4 rounded">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-300">
                <th className="text-left py-2">Length</th>
                <th className="text-left py-2">Quality</th>
                <th className="text-left py-2">Cost/Query</th>
                <th className="text-left py-2">Efficiency</th>
                <th className="text-left py-2">Verdict</th>
              </tr>
            </thead>
            <tbody>
              {data.map(d => (
                <tr key={d.bin} className={d.efficiency === maxEfficiency ? 'bg-green-50 font-semibold' : ''}>
                  <td className="py-2">{d.bin}</td>
                  <td className="py-2">{d.quality.toFixed(2)}/5.0</td>
                  <td className="py-2">${d.cost.toFixed(4)}</td>
                  <td className="py-2">{d.efficiency.toFixed(1)}%</td>
                  <td className="py-2">
                    {d.efficiency === maxEfficiency && <span className="text-green-700 font-bold">✓ BEST VALUE</span>}
                    {d.efficiency < maxEfficiency - 20 && <span className="text-red-600">✗ Too expensive</span>}
                    {d.efficiency >= maxEfficiency - 20 && d.efficiency < maxEfficiency && <span className="text-yellow-600">~ Acceptable</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* PRACTICAL SIGNIFICANCE */}
      <div className="bg-purple-50 border border-purple-300 rounded-lg p-6">
        <h4 className="text-lg font-semibold mb-3 text-purple-900 flex items-center gap-2">
          <span>💰</span> Real-World Impact: 10,000 Queries/Month
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {data.map(d => {
            const monthlyCost = d.cost * 10000
            const savings = monthlyCost - (bestLength.cost * 10000)
            return (
              <div key={d.bin} className={`p-4 rounded-lg ${
                d.efficiency === maxEfficiency ? 'bg-green-100 border-2 border-green-500' : 'bg-white border border-gray-300'
              }`}>
                <div className="text-2xl font-bold mb-1">{d.bin}</div>
                <div className="text-sm space-y-1">
                  <div>Quality: <strong>{d.quality.toFixed(2)}/5.0</strong></div>
                  <div>Monthly: <strong>${monthlyCost.toFixed(2)}</strong></div>
                  {savings > 0 && <div className="text-red-600">+${savings.toFixed(2)} vs optimal</div>}
                  {savings === 0 && <div className="text-green-600 font-bold">✓ OPTIMAL</div>}
                  {savings < 0 && <div className="text-yellow-600">${Math.abs(savings).toFixed(2)} cheaper</div>}
                </div>
              </div>
            )
          })}
        </div>
        <div className="mt-4 p-3 bg-white rounded border border-purple-300 text-sm text-gray-700">
          <strong>Decision:</strong> Using {bestLength.bin} prompts saves ${((worstLength.cost - bestLength.cost) * 10000).toFixed(2)}/month 
          compared to {worstLength.bin}, with only {qualityDiff}% quality difference.
        </div>
      </div>

      {/* METHODOLOGICAL TRANSPARENCY: Component Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-lg p-4 border">
          <h5 className="font-semibold mb-3 text-gray-800">Quality by Length</h5>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="bin" />
              <YAxis domain={[0, 5]} />
              <Tooltip />
              <Bar dataKey="quality" radius={[6, 6, 0, 0]}>
                {data.map((d, i) => <Cell key={i} fill={LENGTH_COLORS[d.bin as keyof typeof LENGTH_COLORS]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="text-xs text-gray-600 mt-2">
            {data.map(d => <div key={d.bin}><strong>{d.bin}:</strong> {d.quality.toFixed(2)}/5.0 ({d.count} runs)</div>)}
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 border">
          <h5 className="font-semibold mb-3 text-gray-800">Cost by Length</h5>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="bin" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="cost" radius={[6, 6, 0, 0]}>
                {data.map((d, i) => <Cell key={i} fill={LENGTH_COLORS[d.bin as keyof typeof LENGTH_COLORS]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="text-xs text-gray-600 mt-2">
            {data.map(d => <div key={d.bin}><strong>{d.bin}:</strong> ${d.cost.toFixed(4)} AUD ({d.count} runs)</div>)}
          </div>
        </div>
      </div>
    </div>
  )
}

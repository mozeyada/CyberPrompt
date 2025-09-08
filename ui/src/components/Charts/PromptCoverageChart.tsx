import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { analyticsApi } from '../../api/client'

type CoverageData = Array<{
  source: string
  scenario: string
  unique_prompt_count: number
  total_runs: number
}>

export function PromptCoverageChart() {
  const { data, isLoading, error } = useQuery<CoverageData>({
    queryKey: ['analytics-coverage'],
    queryFn: () => analyticsApi.coverage()
  })

  if (isLoading) {
    return <div className="flex justify-center items-center h-64">Loading coverage data...</div>
  }

  if (error) {
    return <div className="text-red-600 p-4">Error loading coverage data</div>
  }

  console.log('PromptCoverageChart data:', data)
  
  if (!data || !data.length) {
    return <div className="text-gray-500 p-4">No coverage data available</div>
  }

  // Calculate summary stats
  const totalUniquePrompts = data.reduce((sum, item) => sum + item.unique_prompt_count, 0)
  const totalRuns = data.reduce((sum, item) => sum + item.total_runs, 0)
  const scenarios = [...new Set(data.map(item => item.scenario))]

  // Prepare data for source comparison bar chart
  const sourceData = data.reduce((acc, item) => {
    const existing = acc.find(d => d.source === item.source)
    if (existing) {
      existing.prompts += item.unique_prompt_count
      existing.runs += item.total_runs
    } else {
      acc.push({
        source: item.source,
        prompts: item.unique_prompt_count,
        runs: item.total_runs
      })
    }
    return acc
  }, [] as Array<{ source: string; prompts: number; runs: number }>)

  // Prepare data for scenario vs source heatmap (as stacked bars)
  const scenarioData = scenarios.map(scenario => {
    const scenarioItems = data.filter(item => item.scenario === scenario)
    const result: any = { scenario }
    scenarioItems.forEach(item => {
      result[item.source] = item.unique_prompt_count
    })
    return result
  })

  const COLORS = {
    static: '#6B7280',
    adaptive: '#10B981'
  }

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-900">{totalUniquePrompts}</div>
          <div className="text-sm text-blue-700">Total Unique Prompts</div>
        </div>
        <div className="bg-green-50 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-900">{totalRuns}</div>
          <div className="text-sm text-green-700">Total Runs</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-900">{scenarios.length}</div>
          <div className="text-sm text-purple-700">Scenarios Covered</div>
        </div>
      </div>

      {/* Source Comparison Bar Chart */}
      <div className="bg-white rounded-lg p-6">
        <h4 className="text-lg font-semibold mb-4">Prompts by Source Type</h4>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={sourceData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="source" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="prompts" name="Unique Prompts">
                {sourceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[entry.source as keyof typeof COLORS] || '#6B7280'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Scenario vs Source Stacked Bar Chart */}
      <div className="bg-white rounded-lg p-6">
        <h4 className="text-lg font-semibold mb-4">Prompt Coverage by Scenario</h4>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={scenarioData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="scenario" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="static" stackId="a" fill={COLORS.static} name="Static" />
              <Bar dataKey="adaptive" stackId="a" fill={COLORS.adaptive} name="Adaptive" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
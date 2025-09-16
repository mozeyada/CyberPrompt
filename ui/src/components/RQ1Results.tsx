import { useQuery } from '@tanstack/react-query'
import { runsApi } from '../api/client'
import { Badge } from './ui/badge'

interface RQ1ResultsProps {
  experimentResults: Array<{run_id: string, status: string, model: string, cost?: number, quality?: number}>
}

export function RQ1Results({ experimentResults }: RQ1ResultsProps) {
  // Get the experiment ID from the first result
  const experimentId = experimentResults[0]?.run_id?.split('_')[0]
  
  // Fetch detailed run data for this experiment
  const { data: runData, isLoading } = useQuery({
    queryKey: ['experiment-runs', experimentId],
    queryFn: () => runsApi.list({ experiment_id: experimentId }),
    enabled: !!experimentId
  })

  const runs = runData?.runs?.filter(run => run.status === 'succeeded') || []
  
  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr + 'Z')
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  }

  const getScoreBadge = (score: number) => {
    if (score === 0) return { label: '0.0', color: 'bg-gray-100 text-gray-600' }
    if (score < 2.0) return { label: score.toFixed(1), color: 'bg-red-100 text-red-800' }
    if (score <= 3.5) return { label: score.toFixed(1), color: 'bg-yellow-100 text-yellow-800' }
    return { label: score.toFixed(1), color: 'bg-green-100 text-green-800' }
  }

  if (isLoading) {
    return <div className="text-center py-8">Loading experiment results...</div>
  }

  const totalCost = runs.reduce((sum, run) => sum + (run.economics?.aud_cost || 0), 0)
  const avgQuality = runs.length > 0 
    ? runs.reduce((sum, run) => sum + (run.scores?.composite || 0), 0) / runs.length 
    : 0

  return (
    <div className="space-y-6">
      {/* Experiment Summary */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <span className="text-green-600 text-2xl mr-3">✅</span>
          <div>
            <h3 className="text-lg font-semibold text-green-800">RQ1 Experiment Complete!</h3>
            <p className="text-green-700">Your prompt length analysis has finished successfully.</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{runs.length}</div>
            <div className="text-sm text-gray-600">Successful Runs</div>
          </div>
          <div className="bg-white rounded p-4 text-center">
            <div className="text-2xl font-bold text-green-600">${totalCost.toFixed(4)}</div>
            <div className="text-sm text-gray-600">Total Cost (AUD)</div>
          </div>
          <div className="bg-white rounded p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">{avgQuality.toFixed(1)}/5.0</div>
            <div className="text-sm text-gray-600">Average Quality</div>
          </div>
        </div>
      </div>

      {/* Results Table */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-semibold mb-4">Experiment Results</h3>
        {runs.length === 0 ? (
          <div className="text-center py-8 text-gray-400">No successful runs found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Run ID</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Model</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Scenario</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Quality Score</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Length</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Tokens</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Cost</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Time</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run, index) => {
                  const scoreBadge = getScoreBadge(run.scores?.composite || 0)
                  
                  return (
                    <tr key={run.run_id} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                      <td className="py-3 px-4">
                        <div className="text-sm text-gray-900 max-w-xs truncate">
                          {run.run_id.substring(0, 8)}...
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm font-medium text-gray-900">{run.model}</span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {run.prompt?.scenario || run.scenario || 'Unknown'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${scoreBadge.color}`}>
                          {scoreBadge.label}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                          run.prompt_length_bin === 'S' ? 'bg-green-100 text-green-800' :
                          run.prompt_length_bin === 'M' ? 'bg-blue-100 text-blue-800' :
                          run.prompt_length_bin === 'L' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-600'
                        }`}>
                          {run.prompt_length_bin || '?'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm text-gray-900">
                          {(run.tokens?.total || 0).toLocaleString()}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm text-gray-900">
                          ${(run.economics?.aud_cost || 0).toFixed(4)}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm text-gray-500">
                          {formatDateTime(run.created_at)}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Key Insights */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-800 mb-3">Key Insights from Your RQ1 Experiment</h3>
        <div className="space-y-2 text-blue-700">
          <p>• Tested {runs.length} different model-prompt combinations</p>
          <p>• Average cost per run: ${runs.length > 0 ? (totalCost / runs.length).toFixed(4) : '0.0000'} AUD</p>
          <p>• Quality scores range from {Math.min(...runs.map(r => r.scores?.composite || 0)).toFixed(1)} to {Math.max(...runs.map(r => r.scores?.composite || 0)).toFixed(1)}</p>
          {runs.length > 0 && (
            <p>• Most cost-effective model: {runs.reduce((best, run) => 
              (run.economics?.aud_cost || 0) < (best.economics?.aud_cost || Infinity) ? run : best
            ).model}</p>
          )}
        </div>
      </div>
    </div>
  )
}
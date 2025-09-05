import { RiskCurves } from '../components/Charts/RiskCurves'
import { RiskCostFrontier } from '../components/Charts/RiskCostFrontier'
import { ModelSelect } from '../components/Filters/ModelSelect'
import { ScenarioSelect } from '../components/Filters/ScenarioSelect'

export function Trust() {
  return (
    <div className="space-y-6">
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-bold text-gray-900">Trust & Risk Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Risk awareness, hallucination detection, and trust metrics for SOC/GRC outputs
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ScenarioSelect />
          <ModelSelect />
        </div>
      </div>

      {/* Risk Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Risk Awareness</p>
              <p className="text-2xl font-bold text-green-600">4.2</p>
            </div>
            <div className="text-3xl">🛡️</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Out of 5.0 scale</p>
        </div>
        
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Hallucination Rate</p>
              <p className="text-2xl font-bold text-red-600">12.3%</p>
            </div>
            <div className="text-3xl">⚠️</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Detected false claims</p>
        </div>
        
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Uncertainty Flags</p>
              <p className="text-2xl font-bold text-yellow-600">8.7%</p>
            </div>
            <div className="text-3xl">🤔</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Outputs with uncertainty</p>
        </div>
        
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Trust Score</p>
              <p className="text-2xl font-bold text-blue-600">3.8</p>
            </div>
            <div className="text-3xl">🎯</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Composite reliability</p>
        </div>
      </div>

      {/* Risk Analysis Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RiskCurves />
        <RiskCostFrontier />
      </div>

      {/* Risk Heatmap */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔥 Risk Awareness Heatmap</h3>
        <p className="text-gray-600 mb-4">
          Risk awareness scores across models and length bins
        </p>
        
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Model</th>
                <th className="px-4 py-2 text-center text-sm font-medium text-gray-500">XS</th>
                <th className="px-4 py-2 text-center text-sm font-medium text-gray-500">S</th>
                <th className="px-4 py-2 text-center text-sm font-medium text-gray-500">M</th>
                <th className="px-4 py-2 text-center text-sm font-medium text-gray-500">L</th>
                <th className="px-4 py-2 text-center text-sm font-medium text-gray-500">XL</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {[
                { model: 'gpt-4o', scores: [4.5, 4.3, 4.2, 4.0, 3.8] },
                { model: 'claude-3-5-sonnet', scores: [4.3, 4.2, 4.1, 3.9, 3.7] },
                { model: 'gpt-3.5-turbo', scores: [3.9, 3.8, 3.7, 3.5, 3.3] },
                { model: 'gemini-2.5-flash', scores: [4.0, 3.9, 3.8, 3.6, 3.4] }
              ].map((row) => (
                <tr key={row.model}>
                  <td className="px-4 py-2 font-medium text-gray-900">{row.model}</td>
                  {row.scores.map((score, index) => (
                    <td key={index} className="px-4 py-2 text-center">
                      <div 
                        className={`inline-flex items-center justify-center w-12 h-8 rounded text-white text-sm font-medium ${
                          score >= 4.0 ? 'bg-green-500' :
                          score >= 3.5 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                      >
                        {score.toFixed(1)}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Hallucination Detection */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">🔍 Hallucination Detection</h3>
        <p className="text-gray-600 mb-4">
          Recent outputs flagged for potential hallucinations
        </p>
        
        <div className="space-y-3">
          {[
            { runId: 'run_abc123', model: 'gpt-4o', flags: 2, type: 'Invented CVE references' },
            { runId: 'run_def456', model: 'claude-3-5-sonnet', flags: 1, type: 'Non-existent compliance standard' },
            { runId: 'run_ghi789', model: 'gpt-3.5-turbo', flags: 3, type: 'Fabricated host/asset names' },
            { runId: 'run_jkl012', model: 'gemini-2.5-flash', flags: 1, type: 'Fictional security tools mentioned' }
          ].map(item => (
            <div key={item.runId} className="border border-red-200 rounded-lg p-4 bg-red-50">
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-mono text-sm text-gray-600">{item.runId}</span>
                  <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {item.model}
                  </span>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-red-600">
                    {item.flags} hallucination flags
                  </div>
                  <div className="text-xs text-gray-500">
                    {item.type}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

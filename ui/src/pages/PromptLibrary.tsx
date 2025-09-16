import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { promptsApi, runsApi } from '../api/client'
import { Badge } from '../components/ui/badge'
import { Select } from '../components/ui/select'
import { Input } from '../components/ui/input'

export function PromptLibrary() {
  const [activeTab, setActiveTab] = useState<'prompts' | 'runs'>('prompts')
  const [sourceFilter, setSourceFilter] = useState('all')
  const [scenarioFilter, setScenarioFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['prompts', sourceFilter, scenarioFilter, searchQuery, page],
    queryFn: () => promptsApi.list({
      ...(sourceFilter !== 'all' && { prompt_type: sourceFilter }),
      ...(scenarioFilter !== 'all' && { scenario: scenarioFilter }),
      ...(searchQuery && { q: searchQuery }),
      page,
      limit: 20
    }),
    enabled: activeTab === 'prompts'
  })

  const { data: runsData, isLoading: runsLoading } = useQuery({
    queryKey: ['runs-detailed'],
    queryFn: () => runsApi.list({ limit: 50 }),
    enabled: activeTab === 'runs'
  })

  const prompts = data?.prompts || []

  const tabs = [
    { id: 'prompts', name: 'Browse Prompts', desc: 'Static and adaptive prompts' },
    { id: 'runs', name: 'Experiment Runs', desc: 'Detailed run results with export' }
  ]

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr + 'Z')
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric',
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Data Management</h1>
        <p className="text-gray-600">Browse prompts and detailed experiment results</p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as 'prompts' | 'runs')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div>
                <div>{tab.name}</div>
                <div className="text-xs text-gray-400">{tab.desc}</div>
              </div>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'prompts' && (
        <div className="space-y-6">
          {/* Filters */}
          <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Source</label>
            <Select value={sourceFilter} onChange={(e) => setSourceFilter(e.target.value)}>
              <option value="all">All Sources</option>
              <option value="static">Static</option>
              <option value="adaptive">Adaptive</option>
            </Select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Scenario</label>
            <Select value={scenarioFilter} onChange={(e) => setScenarioFilter(e.target.value)}>
              <option value="all">All Scenarios</option>
              <option value="SOC_INCIDENT">SOC Incident</option>
              <option value="CTI_SUMMARY">CTI Summary</option>
              <option value="GRC_MAPPING">GRC Mapping</option>
            </Select>
          </div>
          
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <Input
              placeholder="Search prompts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Prompts Grid */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="text-center py-8">Loading prompts...</div>
        ) : prompts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No prompts found matching your criteria
          </div>
        ) : (
          prompts.map((prompt) => (
            <div key={prompt.prompt_id} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Badge variant={prompt.scenario === 'SOC_INCIDENT' ? 'default' : 'secondary'}>
                    {prompt.scenario}
                  </Badge>
                  <Badge variant={prompt.source === 'adaptive' ? 'default' : 'outline'}>
                    {prompt.source || 'static'}
                  </Badge>
                  {prompt.length_bin && (
                    <Badge variant="outline">
                      {prompt.length_bin}
                    </Badge>
                  )}
                  {prompt.category && (
                    <Badge variant="secondary">
                      {prompt.category}
                    </Badge>
                  )}
                </div>
                <div className="text-sm text-gray-500">
                  {prompt.token_count && `${prompt.token_count} tokens`}
                </div>
              </div>
              
              <p className="text-gray-700 text-sm leading-relaxed">
                {prompt.text}
              </p>
              
              {prompt.tags && prompt.tags.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {prompt.tags.map((tag, index) => (
                    <span key={index} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-800">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {data && data.count > 20 && (
        <div className="flex justify-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            Previous
          </button>
          <span className="px-4 py-2 text-gray-600">
            Page {page}
          </span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={prompts.length < 20}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
        </div>
      )}

      {/* Experiment Runs Tab */}
      {activeTab === 'runs' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Detailed Experiment Results</h3>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm">
                Export CSV
              </button>
            </div>
            
            {runsLoading ? (
              <div className="text-center py-8">Loading experiment runs...</div>
            ) : !runsData?.runs?.length ? (
              <div className="text-center py-8 text-gray-500">
                No experiment runs found. Run some experiments first!
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Run ID</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Model</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Scenario</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Tech Accuracy</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Actionability</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Completeness</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Compliance</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Risk Awareness</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Relevance</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Clarity</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Composite</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Cost</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {runsData.runs
                      .filter(run => run.status === 'succeeded')
                      .slice(0, 25)
                      .map((run, index) => {
                        const scores = run.scores || {}
                        const compositeBadge = getScoreBadge(scores.composite || 0)
                        
                        return (
                          <tr key={run.run_id} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                            <td className="py-3 px-4 text-sm text-gray-900 max-w-xs truncate">
                              {run.run_id.substring(0, 8)}...
                            </td>
                            <td className="py-3 px-4 text-sm font-medium text-gray-900">{run.model}</td>
                            <td className="py-3 px-4">
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                {run.prompt?.scenario || 'Unknown'}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-sm text-center">{(scores.technical_accuracy || 0).toFixed(1)}</td>
                            <td className="py-3 px-4 text-sm text-center">{(scores.actionability || 0).toFixed(1)}</td>
                            <td className="py-3 px-4 text-sm text-center">{(scores.completeness || 0).toFixed(1)}</td>
                            <td className="py-3 px-4 text-sm text-center">{(scores.compliance_alignment || 0).toFixed(1)}</td>
                            <td className="py-3 px-4 text-sm text-center">{(scores.risk_awareness || 0).toFixed(1)}</td>
                            <td className="py-3 px-4 text-sm text-center">{(scores.relevance || 0).toFixed(1)}</td>
                            <td className="py-3 px-4 text-sm text-center">{(scores.clarity || 0).toFixed(1)}</td>
                            <td className="py-3 px-4">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${compositeBadge.color}`}>
                                {compositeBadge.label}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-sm text-gray-900">
                              ${(run.economics?.aud_cost || 0).toFixed(4)}
                            </td>
                            <td className="py-3 px-4 text-sm text-gray-500">
                              {formatDateTime(run.created_at)}
                            </td>
                          </tr>
                        )
                      })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
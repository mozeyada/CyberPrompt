import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { promptsApi, runsApi } from '../api/client'
import { Badge } from '../components/ui/badge'
import { Select } from '../components/ui/select'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { ViewResponseModal } from '../components/Modals/ViewResponseModal'
import { Eye } from 'lucide-react'

export function PromptLibrary() {
  const [activeTab, setActiveTab] = useState<'prompts' | 'runs'>('prompts')
  const [sourceFilter, setSourceFilter] = useState('all')
  const [scenarioFilter, setScenarioFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [page, setPage] = useState(1)
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null)
  const [isDownloading, setIsDownloading] = useState(false)
  const limit = 10
  const { data, isLoading } = useQuery({
    queryKey: ['prompts', sourceFilter, scenarioFilter, searchQuery],
    queryFn: () => promptsApi.list({
      ...(sourceFilter !== 'all' && { prompt_type: sourceFilter }),
      ...(scenarioFilter !== 'all' && { scenario: scenarioFilter }),
      ...(searchQuery && { q: searchQuery }),
      limit: 500 // Load more prompts
    }),
    enabled: activeTab === 'prompts'
  })

  const { data: runsData, isLoading: runsLoading } = useQuery({
    queryKey: ['runs-detailed', page, sourceFilter],
    queryFn: () => runsApi.list({ 
      page, 
      limit,
      ...(sourceFilter !== 'all' && { source: sourceFilter })
    }),
    enabled: activeTab === 'runs'
  })

  const prompts = data?.prompts || []

  const tabs = [
    { id: 'prompts', name: 'Browse Prompts', desc: 'Static and adaptive prompts' },
    { id: 'runs', name: 'All Results', desc: 'Complete results with response viewing' }
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

  const handleDownloadCSV = async () => {
    const runs = runsData?.runs || []
    if (!runs || runs.length === 0) {
      alert('No data to export. Please run some experiments first.')
      return
    }
    
    const validRuns = runs.filter(run => run.status === 'succeeded')
    if (validRuns.length === 0) {
      alert('No successful runs to export. Please check your experiment results.')
      return
    }
    
    setIsDownloading(true)
    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const API_KEY = import.meta.env.VITE_API_KEY || 'supersecret1'
      
      const params = new URLSearchParams()
      if (sourceFilter !== 'all') {
        params.append('source', sourceFilter)
      }
      params.append('export_timestamp', new Date().toISOString())
      params.append('total_records', validRuns.length.toString())
      
      const response = await fetch(`${API_BASE_URL}/results/export?${params}`, {
        headers: { 'x-api-key': API_KEY }
      })
      
      if (!response.ok) throw new Error('Export failed')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `cybercqbench_results_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      console.log(`Exported ${validRuns.length} valid runs out of ${runs.length} total runs`)
    } catch (error) {
      console.error('Download failed:', error)
      alert('Download failed. Please try again.')
    } finally {
      setIsDownloading(false)
    }
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

      {/* Show total count */}
      {data && (
        <div className="text-center text-gray-600 text-sm">
          Showing {prompts.length} of {data.count} prompts
        </div>
      )}
        </div>
      )}

      {/* All Results Tab */}
      {activeTab === 'runs' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-4">
                <h3 className="text-lg font-semibold">All Results</h3>
                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium text-gray-700">Source:</label>
                  <Select value={sourceFilter} onChange={(e) => setSourceFilter(e.target.value)} className="w-32">
                    <option value="all">All</option>
                    <option value="static">Static</option>
                    <option value="adaptive">Adaptive</option>
                  </Select>
                </div>
              </div>
              <Button 
                onClick={handleDownloadCSV}
                disabled={isDownloading}
                variant="outline"
                size="sm"
              >
                {isDownloading ? 'Downloading...' : 'Export CSV'}
              </Button>
            </div>
            
            {runsLoading ? (
              <div className="text-center py-8">Loading results...</div>
            ) : !runsData?.runs?.length ? (
              <div className="text-center py-8 text-gray-500">
                No results found. Run some experiments first!
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-medium text-gray-600">Model</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-600">Source</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-600">Experiment</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-600">Dataset</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-600">Status</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-600">Tokens</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-600">Cost (AUD)</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-600">Quality Score</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-600">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {runsData.runs.map((run, index) => (
                        <tr key={run.run_id} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                          <td className="py-3 px-4">
                            <Badge variant="secondary">{run.model}</Badge>
                          </td>
                          <td className="py-3 px-4">
                            <Badge variant={run.source === 'adaptive' ? 'default' : 'outline'}>
                              {run.source || 'static'}
                            </Badge>
                          </td>
                          <td className="py-3 px-4">
                            <span className="text-xs text-gray-600">
                              {run.experiment_id ? run.experiment_id.split('_').slice(-1)[0] : 'N/A'}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span className="text-xs text-gray-600">
                              {run.dataset_version || 'N/A'}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <Badge variant={run.status === 'succeeded' ? 'default' : 'destructive'}>
                              {run.status}
                            </Badge>
                          </td>
                          <td className="py-3 px-4 text-sm">{run.tokens?.total || 0}</td>
                          <td className="py-3 px-4 text-sm">${run.economics?.aud_cost?.toFixed(4) || '0.0000'}</td>
                          <td className="py-3 px-4 text-sm">
                            {run.scores?.composite ? `${run.scores.composite.toFixed(1)}/5.0` : 'N/A'}
                          </td>
                          <td className="py-3 px-4">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setSelectedRunId(run.run_id)}
                              className="flex items-center gap-1"
                              disabled={run.status !== 'succeeded'}
                            >
                              <Eye className="h-3 w-3" />
                              View
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                <div className="flex justify-between items-center mt-4">
                  <span className="text-sm text-gray-500">
                    Page {page} • {runsData?.count || 0} total runs
                  </span>
                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      Previous
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => setPage(p => p + 1)}
                      disabled={runsData?.runs?.length < limit}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              </>
            )}
          </div>
          
          {/* View Response Modal */}
          {selectedRunId && (
            <ViewResponseModal
              runId={selectedRunId}
              isOpen={!!selectedRunId}
              onClose={() => setSelectedRunId(null)}
            />
          )}
        </div>
      )}
    </div>
  )
}
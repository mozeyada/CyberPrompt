import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { promptsApi } from '../api/client'
import { Badge } from '../components/ui/badge'
import { Select } from '../components/ui/select'
import { Input } from '../components/ui/input'

export function PromptLibrary() {
  const [activeTab, setActiveTab] = useState<'prompts' | 'adaptive'>('prompts')
  const [sourceFilter, setSourceFilter] = useState('all')
  const [scenarioFilter, setScenarioFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [page, setPage] = useState(1)
  const limit = 10

  const { data, isLoading } = useQuery({
    queryKey: ['prompts', activeTab, sourceFilter, scenarioFilter, searchQuery],
    queryFn: () => promptsApi.list({
      prompt_type: activeTab === 'prompts' ? 'static' : 'adaptive',
      ...(scenarioFilter !== 'all' && { scenario: scenarioFilter }),
      ...(searchQuery && { q: searchQuery }),
      limit: 200 // Load more prompts - max limit is 200
    })
  })

  const prompts = data?.prompts || []

  const tabs = [
    { id: 'prompts', name: 'Static Prompts', desc: 'Browse baseline research prompts' },
    { id: 'adaptive', name: 'Adaptive Prompts', desc: 'Generated prompts from documents' }
  ]


  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Prompt Datasets</h1>
        <p className="text-gray-600">Browse static and adaptive prompt collections</p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as 'prompts' | 'adaptive')}
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

      {/* Adaptive Prompts Tab */}
      {activeTab === 'adaptive' && (
        <div className="space-y-6">
          {/* Same content as prompts tab, but filtered for adaptive */}
          {/* Filters */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Adaptive Prompts</h3>
              <div className="flex gap-4">
                <Select value={scenarioFilter} onChange={(e) => setScenarioFilter(e.target.value)}>
                  <option value="all">All Scenarios</option>
                  <option value="INCIDENT_RESPONSE">Incident Response</option>
                  <option value="THREAT_INTEL">Threat Intelligence</option>
                  <option value="COMPLIANCE">Compliance</option>
                  <option value="VULNERABILITY">Vulnerability Assessment</option>
                </Select>
                <Input
                  placeholder="Search prompts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-64"
                />
              </div>
            </div>

            {isLoading ? (
              <div className="text-center py-8">Loading prompts...</div>
            ) : !prompts.length ? (
              <div className="text-center py-8 text-gray-500">
                No adaptive prompts found. Generate some from documents!
              </div>
            ) : (
              <div className="space-y-4">
                {prompts.map((prompt, index) => (
                  <div key={prompt.prompt_id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex gap-2">
                        <Badge variant="default">Adaptive</Badge>
                        <Badge variant="outline">{prompt.scenario}</Badge>
                        {prompt.length_bin && <Badge variant="secondary">{prompt.length_bin}</Badge>}
                      </div>
                      <span className="text-xs text-gray-500">{prompt.token_count} tokens</span>
                    </div>
                    <p className="text-sm text-gray-700 line-clamp-3">{prompt.text}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
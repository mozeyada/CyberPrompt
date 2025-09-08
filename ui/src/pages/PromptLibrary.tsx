import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { promptsApi } from '../api/client'
import { Badge } from '../components/ui/badge'
import { Select } from '../components/ui/select'
import { Input } from '../components/ui/input'

export function PromptLibrary() {
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
    })
  })

  const prompts = data?.prompts || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Prompt Library</h1>
        <p className="text-gray-600">Browse and manage all saved prompts</p>
      </div>

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
                  {prompt.metadata?.word_count && `${prompt.metadata.word_count} words`}
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
  )
}
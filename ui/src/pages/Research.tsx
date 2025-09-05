import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { researchApi } from '../api/client'

export function Research() {
  const [selectedScenario, setSelectedScenario] = useState<string>('')
  const [selectedLengthBin, setSelectedLengthBin] = useState<string>('')
  const [sampleSize, setSampleSize] = useState<number>(50)

  // Get research dataset statistics
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['research-stats'],
    queryFn: () => researchApi.getScenarioStats()
  })

  // Get filtered prompts for analysis
  const { data: filteredData, isLoading: filterLoading, refetch } = useQuery({
    queryKey: ['research-filter', selectedScenario, selectedLengthBin, sampleSize],
    queryFn: () => researchApi.filterPrompts({
      scenario: selectedScenario || undefined,
      length_bin: selectedLengthBin || undefined,
      sample_size: sampleSize
    }),
    enabled: false // Manual trigger
  })

  const handleFilter = () => {
    refetch()
  }

  const exportData = () => {
    if (filteredData?.prompts) {
      const csv = [
        'prompt_id,text,scenario,category,length_bin,word_count,source',
        ...filteredData.prompts.map((p: any) => 
          `"${p._id}","${p.text.replace(/"/g, '""')}","${p.scenario}","${p.category}","${p.metadata?.length_bin}","${p.metadata?.word_count}","${p.source}"`
        )
      ].join('\n')
      
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `cybercqbench-research-${Date.now()}.csv`
      a.click()
    }
  }

  return (
    <div className="space-y-6">
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-bold text-gray-900">Research Hub</h1>
        <p className="mt-2 text-gray-600">
          Academic insights - Academic tools for RQ1 (length analysis) and RQ2 (adaptive benchmarking) research
        </p>
      </div>

      {/* Research Dataset Overview */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">📊 Research Dataset Overview</h2>
        
        {statsLoading ? (
          <div className="animate-pulse bg-gray-200 h-32 rounded"></div>
        ) : stats ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {Object.entries(stats.research_dataset.scenarios).map(([scenario, data]: [string, any]) => (
              <div key={scenario} className="border rounded-lg p-4">
                <h3 className="font-semibold text-lg mb-2">{scenario}</h3>
                <p className="text-2xl font-bold text-blue-600 mb-3">{data.total_prompts} prompts</p>
                
                <div className="space-y-2">
                  {Object.entries(data.length_bins).map(([bin, binData]: [string, any]) => (
                    <div key={bin} className="flex justify-between text-sm">
                      <span className={`px-2 py-1 rounded text-xs ${
                        bin === 'short' ? 'bg-green-100 text-green-800' :
                        bin === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {bin}
                      </span>
                      <span>{binData.count} ({binData.avg_words}w avg)</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : null}
      </div>

      {/* Research Questions */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-purple-900 mb-4">🔬 Research Questions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg p-4 border">
            <h3 className="font-semibold text-purple-900 mb-2">RQ1: Length vs Performance</h3>
            <p className="text-sm text-purple-700 mb-3">
              How does prompt length correlate with LLM performance across cybersecurity scenarios?
            </p>
            <div className="text-xs text-purple-600">
              <p>• Use length bin filtering below</p>
              <p>• Compare short/medium/long performance</p>
              <p>• Export data for statistical analysis</p>
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-4 border">
            <h3 className="font-semibold text-purple-900 mb-2">RQ2: Adaptive Benchmarking</h3>
            <p className="text-sm text-purple-700 mb-3">
              How do different scenarios (SOC/CTI/GRC) reveal model strengths and weaknesses?
            </p>
            <div className="text-xs text-purple-600">
              <p>• Compare across scenarios</p>
              <p>• Analyze scenario-specific performance</p>
              <p>• Identify adaptive vs static patterns</p>
            </div>
          </div>
        </div>
      </div>

      {/* Research Filtering Tool */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">🔍 Research Data Filtering</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Scenario
            </label>
            <select
              value={selectedScenario}
              onChange={(e) => setSelectedScenario(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">All scenarios</option>
              <option value="SOC_INCIDENT">SOC Incident</option>
              <option value="CTI_SUMMARY">CTI Summary</option>
              <option value="GRC_MAPPING">GRC Mapping</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Length Bin (RQ1)
            </label>
            <select
              value={selectedLengthBin}
              onChange={(e) => setSelectedLengthBin(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">All lengths</option>
              <option value="short">Short (≤15 words)</option>
              <option value="medium">Medium (16-30 words)</option>
              <option value="long">Long (&gt;30 words)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sample Size
            </label>
            <input
              type="number"
              value={sampleSize}
              onChange={(e) => setSampleSize(parseInt(e.target.value))}
              min="1"
              max="200"
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
          
          <div className="flex items-end">
            <button
              onClick={handleFilter}
              disabled={filterLoading}
              className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md"
            >
              {filterLoading ? 'Filtering...' : 'Filter Data'}
            </button>
          </div>
        </div>

        {/* Filter Results */}
        {filteredData && (
          <div className="border-t pt-4">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold">Filtered Results</h3>
                <p className="text-sm text-gray-600">
                  {filteredData.sample_size} prompts from {filteredData.total_count} total
                  {filteredData.research_metadata.avg_word_count && (
                    <span> • Avg: {filteredData.research_metadata.avg_word_count} words</span>
                  )}
                </p>
              </div>
              <button
                onClick={exportData}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm"
              >
                Export CSV
              </button>
            </div>
            
            {/* Length Distribution */}
            {filteredData.research_metadata.length_distribution && (
              <div className="mb-4">
                <h4 className="font-medium mb-2">Length Distribution</h4>
                <div className="flex gap-4">
                  {Object.entries(filteredData.research_metadata.length_distribution).map(([bin, count]: [string, any]) => (
                    <span key={bin} className={`px-3 py-1 rounded text-sm ${
                      bin === 'short' ? 'bg-green-100 text-green-800' :
                      bin === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {bin}: {count}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {/* Sample Prompts */}
            <div className="max-h-64 overflow-y-auto border rounded-lg p-3">
              <h4 className="font-medium mb-2">Sample Prompts</h4>
              <div className="space-y-2">
                {filteredData.prompts.slice(0, 5).map((prompt: any) => (
                  <div key={prompt._id} className="border-l-4 border-purple-200 pl-3 py-2">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs bg-purple-100 text-purple-800 px-2 py-0.5 rounded">
                        {prompt.scenario}
                      </span>
                      <span className="text-xs bg-gray-100 text-gray-800 px-2 py-0.5 rounded">
                        {prompt.metadata?.length_bin} ({prompt.metadata?.word_count}w)
                      </span>
                      <span className="text-xs text-gray-500">{prompt.category}</span>
                    </div>
                    <p className="text-sm text-gray-700">
                      {prompt.text.substring(0, 200)}...
                    </p>
                  </div>
                ))}
                {filteredData.prompts.length > 5 && (
                  <p className="text-sm text-gray-500 text-center py-2">
                    ... and {filteredData.prompts.length - 5} more prompts
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Research Notes */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-yellow-900 mb-3">📝 Research Notes</h2>
        <div className="text-sm text-yellow-800 space-y-2">
          <p><strong>Sample Recommendations:</strong></p>
          <ul className="list-disc list-inside ml-4 space-y-1">
            <li>Small experiment: 50 prompts per scenario (150 total)</li>
            <li>Full experiment: All available prompts per scenario</li>
            <li>Length analysis: Compare performance across short/medium/long bins</li>
            <li>Scenario analysis: Compare SOC vs CTI vs GRC performance patterns</li>
          </ul>
          <p className="mt-3"><strong>Export Format:</strong> CSV with prompt_id, text, scenario, category, length_bin, word_count, source</p>
        </div>
      </div>
    </div>
  )
}
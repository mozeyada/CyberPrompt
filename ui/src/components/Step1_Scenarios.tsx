import React, { useState } from 'react'
import { ScenarioSelect } from './Filters/ScenarioSelect'
import { PromptSelector } from './Selectors/PromptSelector'
import { useFilters } from '../state/useFilters'

interface Step1Props {
  lengthBin: string
  setLengthBin: (bin: string) => void
}

export function Step1_Scenarios({ lengthBin, setLengthBin }: Step1Props) {
  const { selectedScenario, selectedPrompts, setSelectedPrompts } = useFilters()
  const [sourceFilter, setSourceFilter] = useState('all')
  const [includeVariants, setIncludeVariants] = useState(false)
  
  // Reset includeVariants when switching to adaptive prompts
  React.useEffect(() => {
    if (sourceFilter === 'adaptive') {
      setIncludeVariants(false)
    }
  }, [sourceFilter])

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Choose Security Scenarios</h2>
        <p className="text-gray-600 mt-2">Select realistic SOC/GRC tasks to test</p>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div>
            <ScenarioSelect />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Length Filter (Optional)
            </label>
            <select
              value={lengthBin}
              onChange={(e) => setLengthBin(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">All lengths</option>
              <option value="S">S (≤300 tokens)</option>
              <option value="M">M (301-800 tokens)</option>
              <option value="L">L (&gt;800 tokens)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source Type
            </label>
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="all">All Sources</option>
              <option value="static">Static Prompts</option>
              <option value="adaptive">Adaptive Prompts</option>
            </select>
          </div>
        </div>

        <div className="mb-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={includeVariants}
              onChange={(e) => setIncludeVariants(e.target.checked)}
              disabled={sourceFilter === 'adaptive'}
              className={`rounded border-gray-300 text-blue-600 focus:ring-blue-500 ${
                sourceFilter === 'adaptive' ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            />
            <span className={`text-sm font-medium ${
              sourceFilter === 'adaptive' ? 'text-gray-400' : 'text-gray-700'
            }`}>
              Include length variants (S+M+L groups)
            </span>
            <span className="text-xs text-gray-500">
              {sourceFilter === 'adaptive' 
                ? 'Only available for static prompts - adaptive prompts don\'t have variants'
                : 'Select original prompts to automatically include their Medium and Long variants'
              }
            </span>
          </label>
        </div>

        <PromptSelector 
          selectedPrompts={selectedPrompts}
          onPromptsChange={setSelectedPrompts}
          scenario={selectedScenario}
          lengthBin={lengthBin}
          sourceFilter={sourceFilter}
          includeVariants={includeVariants}
        />
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center">
          <span className="text-blue-600 mr-2 font-bold">!</span>
          <div className="text-sm text-blue-800">
            <p className="font-medium">Tip:</p>
            <p>Select 10-20 prompts for a comprehensive comparison. More prompts = more reliable results.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
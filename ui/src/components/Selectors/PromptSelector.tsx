import { useQuery } from '@tanstack/react-query'
import { promptsApi, researchApi } from '../../api/client'
import type { Prompt } from '../../types'

interface PromptSelectorProps {
  selectedPrompts: string[]
  onPromptsChange: (prompts: string[]) => void
  scenario?: string | null
  lengthBin?: string
  sourceFilter?: string
}

export function PromptSelector({ selectedPrompts, onPromptsChange, scenario, lengthBin, sourceFilter }: PromptSelectorProps) {
  const { data: promptsData, isLoading, error } = useQuery({
    queryKey: ['prompts', scenario, lengthBin, sourceFilter],
    queryFn: () => {
      console.log('PromptSelector query:', { scenario, lengthBin, sourceFilter })
      return promptsApi.list({ 
        scenario: scenario || undefined,
        length_bin: lengthBin || undefined,
        ...(sourceFilter && sourceFilter !== 'all' && { prompt_type: sourceFilter }),
        limit: 500 // Show all available prompts
      }).then(data => {
        console.log('Prompts API result:', data)
        return data
      })
    },
    enabled: true
  })

  const handlePromptToggle = (promptId: string) => {
    if (selectedPrompts.includes(promptId)) {
      onPromptsChange(selectedPrompts.filter(id => id !== promptId))
    } else {
      onPromptsChange([...selectedPrompts, promptId])
    }
  }

  const handleSelectAll = () => {
    if (promptsData?.prompts) {
      const promptIds = promptsData.prompts.map((p: any, index: number) => 
        p.prompt_id || `prompt-${index}`
      ).filter(Boolean)
      onPromptsChange(promptIds)
    }
  }

  const handleSelectNone = () => {
    onPromptsChange([])
  }

  if (isLoading) {
    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">Available Prompts</label>
        <div className="animate-pulse bg-gray-200 h-32 rounded-md"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">Available Prompts</label>
        <div className="text-red-600 text-sm">Error loading prompts</div>
      </div>
    )
  }

  const prompts = promptsData?.prompts || []

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          Available Prompts ({prompts.length})
        </label>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleSelectAll}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            Select All
          </button>
          <button
            type="button"
            onClick={handleSelectNone}
            className="text-xs text-gray-600 hover:text-gray-800"
          >
            Select None
          </button>
        </div>
      </div>
      
      <div className="max-h-48 overflow-y-auto border border-gray-300 rounded-md p-3 space-y-2">
        {prompts.length === 0 ? (
          <div className="text-gray-500 text-sm text-center py-4">
            No prompts available. {scenario ? `Try selecting a different scenario.` : 'Import some prompts first.'}
          </div>
        ) : (
          prompts.map((prompt, index) => {
            const uniqueKey = prompt.prompt_id || `prompt-${index}`
            const promptId = prompt.prompt_id || uniqueKey
            return (
            <label key={uniqueKey} className="flex items-start space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedPrompts.includes(promptId)}
                onChange={() => {
                  console.log('Prompt toggle clicked:', { promptId, prompt })
                  handlePromptToggle(promptId)
                }}
                className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                    {prompt.scenario}
                  </span>
                  {prompt.length_bin && (
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      prompt.length_bin === 'XS' ? 'bg-green-100 text-green-800' :
                      prompt.length_bin === 'S' ? 'bg-blue-100 text-blue-800' :
                      prompt.length_bin === 'M' ? 'bg-yellow-100 text-yellow-800' :
                      prompt.length_bin === 'L' ? 'bg-orange-100 text-orange-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {prompt.length_bin}
                    </span>
                  )}
                  {prompt.category && (
                    <span className="text-xs bg-gray-100 text-gray-800 px-2 py-0.5 rounded">
                      {prompt.category}
                    </span>
                  )}
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    prompt.source === 'adaptive' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {prompt.source === 'adaptive' ? 'Adaptive' : 'Static'}
                  </span>
                  {prompt.source === 'CySecBench' && (
                    <span className="text-xs bg-purple-100 text-purple-800 px-2 py-0.5 rounded">
                      Research
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-700 line-clamp-2">
                  {prompt.text.substring(0, 150)}...
                </p>
              </div>
            </label>
            )
          })
        )}
      </div>
      
      <div className="text-xs text-gray-500">
        {selectedPrompts.length} prompt{selectedPrompts.length !== 1 ? 's' : ''} selected
      </div>
    </div>
  )
}
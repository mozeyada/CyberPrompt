import { useQuery } from '@tanstack/react-query'
import { promptsApi, researchApi } from '../../api/client'
import type { Prompt } from '../../types'

interface PromptSelectorProps {
  selectedPrompts: string[]
  onPromptsChange: (prompts: string[]) => void
  scenario?: string | null
  lengthBin?: string
  sourceFilter?: string
  includeVariants?: boolean
}

export function PromptSelector({ selectedPrompts, onPromptsChange, scenario, lengthBin, sourceFilter, includeVariants }: PromptSelectorProps) {
  const { data: promptsData, isLoading, error } = useQuery({
    queryKey: ['prompts', scenario, lengthBin, sourceFilter, includeVariants],
    queryFn: () => {
      console.log('PromptSelector query:', { scenario, lengthBin, sourceFilter, includeVariants })
      return promptsApi.list({ 
        scenario: scenario || undefined,
        length_bin: lengthBin || undefined,
        ...(sourceFilter && sourceFilter !== 'all' && { prompt_type: sourceFilter }),
        include_variants: includeVariants, // Only fetch variants when needed
        limit: 500
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
  
  // Calculate display count based on what's actually shown
  const filteredForDisplay = prompts.filter(prompt => {
    if (includeVariants) {
      return !prompt.metadata?.variant_of
    }
    return true
  })
  const displayCount = filteredForDisplay.length

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          Available Prompts ({displayCount})
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
            No prompts available. {scenario ? 'Try selecting a different scenario.' : 'Import some prompts first.'}
          </div>
        ) : (
          (() => {
            const elements = []
            const filteredPrompts = prompts.filter(prompt => {
              if (includeVariants) {
                return !prompt.metadata?.variant_of
              }
              return true
            })
            
            filteredPrompts.forEach((prompt, index) => {
              const uniqueKey = prompt.prompt_id + '-' + index
              const promptId = prompt.prompt_id || 'prompt-' + index
              
              // Add original prompt
              elements.push(
                <label key={uniqueKey} className="flex items-start space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedPrompts.includes(promptId)}
                    onChange={() => handlePromptToggle(promptId)}
                    className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                        {prompt.scenario}
                      </span>
                      {prompt.length_bin && (
                        <span className={'text-xs px-2 py-0.5 rounded ' + (
                          prompt.length_bin === 'S' ? 'bg-green-100 text-green-800' :
                          prompt.length_bin === 'M' ? 'bg-blue-100 text-blue-800' :
                          prompt.length_bin === 'L' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        )}>
                          {prompt.length_bin}
                        </span>
                      )}
                      {includeVariants && !prompt.metadata?.variant_of && (
                        <span className="text-xs bg-purple-100 text-purple-800 px-2 py-0.5 rounded">
                          +M+L variants
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 line-clamp-2">
                      {prompt.text.substring(0, 150)}...
                    </p>
                  </div>
                </label>
              )
              
              // Add variants if this prompt is selected and variants are enabled
              if (includeVariants && selectedPrompts.includes(promptId)) {
                const variants = prompts.filter(p => p.metadata?.variant_of === promptId)
                console.log(`Variants for ${promptId}:`, variants.map(v => ({ id: v.prompt_id, length: v.length_bin })))
                
                // Remove duplicates and sort variants by length_bin to ensure consistent M, L order
                const uniqueVariants = variants.filter((variant, index, arr) => 
                  arr.findIndex(v => v.prompt_id === variant.prompt_id) === index
                )
                const sortedVariants = uniqueVariants.sort((a, b) => {
                  const order = { 'M': 1, 'L': 2 }
                  return (order[a.length_bin] || 99) - (order[b.length_bin] || 99)
                })
                
                sortedVariants.forEach((variant, vIndex) => {
                  elements.push(
                    <div key={variant.prompt_id + '-variant-' + vIndex} className="ml-6 bg-gray-50 p-2 rounded border-l-2 border-gray-300">
                      <div className="flex items-start space-x-2">
                        <input
                          type="checkbox"
                          checked={true}
                          disabled={true}
                          className="mt-1 rounded border-gray-300 text-blue-600 opacity-50 cursor-not-allowed"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                              {variant.scenario}
                            </span>
                            <span className={'text-xs px-2 py-0.5 rounded ' + (
                              variant.length_bin === 'M' ? 'bg-blue-100 text-blue-800' :
                              variant.length_bin === 'L' ? 'bg-red-100 text-red-800' :
                              'bg-gray-100 text-gray-800'
                            )}>
                              {variant.length_bin} (Auto-included)
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 line-clamp-2">
                            {variant.text.substring(0, 150)}...
                          </p>
                        </div>
                      </div>
                    </div>
                  )
                })
              }
            })
            
            return elements
          })()
        )}
      </div>
      
      <div className="text-xs text-gray-500">
        {includeVariants 
          ? `${selectedPrompts.length} prompt group${selectedPrompts.length !== 1 ? 's' : ''} selected (${selectedPrompts.length * 3} total prompts including variants)`
          : `${selectedPrompts.length} prompt${selectedPrompts.length !== 1 ? 's' : ''} selected`
        }
      </div>
      

    </div>
  )
}
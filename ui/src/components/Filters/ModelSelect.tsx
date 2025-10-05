import { useFilters } from '../../state/useFilters'

const AVAILABLE_MODELS = [
  'gpt-4o',
  'llama-3.3-70b-versatile',
      'gemini-2.5-pro',
  'claude-3-5-sonnet'
]

export function ModelSelect() {
  const { selectedModels, setSelectedModels } = useFilters()

  const handleModelToggle = (model: string) => {
    if (selectedModels.includes(model)) {
      setSelectedModels(selectedModels.filter(m => m !== model))
    } else {
      setSelectedModels([...selectedModels, model])
    }
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">Models</label>
      <div className="space-y-1 max-h-48 overflow-y-auto">
        {AVAILABLE_MODELS.map(model => (
          <label key={model} className="flex items-center">
            <input
              type="checkbox"
              checked={selectedModels.includes(model)}
              onChange={() => handleModelToggle(model)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">{model}</span>
          </label>
        ))}
      </div>
    </div>
  )
}
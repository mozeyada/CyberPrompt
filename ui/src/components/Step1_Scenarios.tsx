import { ScenarioSelect } from './Filters/ScenarioSelect'
import { PromptSelector } from './Selectors/PromptSelector'
import { useFilters } from '../state/useFilters'

interface Step1Props {
  selectedPrompts: string[]
  onPromptsChange: (prompts: string[]) => void
  lengthBin: string
  setLengthBin: (bin: string) => void
}

export function Step1_Scenarios({ selectedPrompts, onPromptsChange, lengthBin, setLengthBin }: Step1Props) {
  const { selectedScenario } = useFilters()

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Choose Security Scenarios</h2>
        <p className="text-gray-600 mt-2">Select realistic SOC/GRC tasks to test</p>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
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
              <option value="xs">Extra Short (≤200 words)</option>
              <option value="s">Short (201-500 words)</option>
              <option value="m">Medium (501-1000 words)</option>
              <option value="l">Long (1001-2000 words)</option>
            </select>
          </div>
        </div>

        <PromptSelector 
          selectedPrompts={selectedPrompts}
          onPromptsChange={onPromptsChange}
          scenario={selectedScenario}
          lengthBin={lengthBin}
        />
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center">
          <span className="text-blue-600 mr-2">💡</span>
          <div className="text-sm text-blue-800">
            <p className="font-medium">Tip:</p>
            <p>Select 10-20 prompts for a comprehensive comparison. More prompts = more reliable results.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
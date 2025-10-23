interface Step2Props {
  selectedModels: string[]
  setSelectedModels: (models: string[]) => void
}

export function Step2_Models({ selectedModels, setSelectedModels }: Step2Props) {
  const models = [
    { id: 'gpt-4o', name: 'GPT-4o', desc: 'High quality, higher cost', color: 'bg-blue-100 text-blue-800' },
    { id: 'claude-3-5-sonnet', name: 'Claude 3.5 Sonnet', desc: 'Excellent reasoning', color: 'bg-purple-100 text-purple-800' },
    { id: 'gemini-2.0-flash-exp', name: 'Gemini 2.0 Flash (Experimental)', desc: 'Latest experimental, fast, cost-effective', color: 'bg-orange-100 text-orange-800' }
  ]

  const toggleModel = (modelId: string) => {
    if (selectedModels.includes(modelId)) {
      setSelectedModels(selectedModels.filter(m => m !== modelId))
    } else {
      setSelectedModels([...selectedModels, modelId])
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Select AI Models to Compare</h2>
        <p className="text-gray-600 mt-2">Choose 2-4 models for best comparison</p>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {models.map(model => (
            <div
              key={model.id}
              onClick={() => toggleModel(model.id)}
              className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                selectedModels.includes(model.id)
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      checked={selectedModels.includes(model.id)}
                      onChange={() => toggleModel(model.id)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <div>
                      <h3 className="font-semibold text-gray-900">{model.name}</h3>
                      <p className="text-sm text-gray-600">{model.desc}</p>
                    </div>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${model.color}`}>
                  AI Model
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-center">
          <span className="text-yellow-600 mr-2">Fast</span>
          <div className="text-sm text-yellow-800">
            <p className="font-medium">Recommendation:</p>
            <p>Select 2-3 models for optimal comparison. More models = higher cost but better insights.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
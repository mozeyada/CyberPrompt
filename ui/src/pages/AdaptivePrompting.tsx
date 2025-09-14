import { useState } from 'react'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Select } from '../components/ui/select'
import { Textarea } from '../components/ui/textarea'
import { Badge } from '../components/ui/badge'
import axios from 'axios'
// PDF parsing removed - use text input for reliable research results

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_KEY = import.meta.env.VITE_API_KEY || 'supersecret1'

interface AdaptivePromptResponse {
  prompts: string[]
  task_type: string
  count: number
}

const taskTypes = [
  { value: 'SOC_INCIDENT', label: 'SOC Incident Response' },
  { value: 'GRC_MAPPING', label: 'GRC Compliance Mapping' },
  { value: 'CTI_SUMMARY', label: 'CTI Threat Intelligence' }
]

export function AdaptivePrompting() {
  const [documentText, setDocumentText] = useState('')
  const [taskType, setTaskType] = useState('')
  const [model, setModel] = useState('gpt-4')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedPrompts, setGeneratedPrompts] = useState<string[]>([])
  const [selectedPrompts, setSelectedPrompts] = useState<Set<number>>(new Set())
  const [error, setError] = useState('')

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (file.name.endsWith('.txt')) {
      try {
        const text = await file.text()
        setDocumentText(text)
        setError('')
      } catch (err) {
        setError('Failed to read text file')
      }
    } else {
      setError('Only .txt files supported. For PDFs, copy and paste the text below.')
    }
  }

  const generatePrompts = async () => {
    if (!documentText.trim() || !taskType) {
      setError('Please provide document text and select a task type')
      return
    }

    setIsGenerating(true)
    setError('')

    try {
      const response = await axios.post<AdaptivePromptResponse>(
        `${API_BASE_URL}/adaptive/generate`,
        {
          document_text: documentText,
          task_type: taskType,
          model: model
        },
        {
          headers: { 'x-api-key': API_KEY }
        }
      )

      setGeneratedPrompts(response.data.prompts)
      setSelectedPrompts(new Set())
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate prompts')
    } finally {
      setIsGenerating(false)
    }
  }

  const togglePromptSelection = (index: number) => {
    const newSelected = new Set(selectedPrompts)
    if (newSelected.has(index)) {
      newSelected.delete(index)
    } else {
      newSelected.add(index)
    }
    setSelectedPrompts(newSelected)
  }

  const saveSelectedPrompts = async () => {
    const selected = generatedPrompts.filter((_, index) => selectedPrompts.has(index))
    
    if (selected.length === 0) {
      setError('Please select at least one prompt to save')
      return
    }

    try {
      const promptsToSave = selected.map((text, index) => ({
        text,
        scenario: taskType, // Direct scenario name (SOC_INCIDENT, GRC_MAPPING, CTI_SUMMARY)
        category: 'Adaptive Generated',
        source: 'adaptive',
        metadata: {
          word_count: text.split(' ').length,
          original_category: 'Adaptive Generated',
          dataset_version: '1.0',
          generation_model: model,
          generation_date: new Date().toISOString().split('T')[0]
        },
        tags: [taskType.toLowerCase()],
        prompt_type: 'adaptive',
        dataset_version: new Date().toISOString().replace(/-/g, '').slice(0, 8), // YYYYMMDD format
        prompt_id: `adaptive_${Date.now()}_${index + 1}`,
        // Token count and length_bin will be calculated by backend
        token_count: undefined,
        length_bin: undefined
      }))

      await axios.post(
        `${API_BASE_URL}/prompts/import`,
        promptsToSave,
        { headers: { 'x-api-key': API_KEY } }
      )

      alert(`Successfully saved ${selected.length} prompts!`)
      setSelectedPrompts(new Set())
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save prompts')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Adaptive Prompting</h1>
        <p className="mt-2 text-gray-600">
          RQ2 Research: Generate adaptive prompts from SOC/GRC policies and CTI for benchmarking validation
        </p>
        <div className="mt-2 text-sm text-blue-600">
          📊 Research Method: Generate adaptive prompts → Compare vs CySecBench baseline using KL divergence
        </div>
      </div>

      {/* Document Upload */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">1. Upload Document</h2>
        <div className="space-y-4">
          <Input
            type="file"
            accept=".txt"
            onChange={handleFileUpload}
            className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibent file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <div className="text-sm text-gray-500">
            📄 Upload .txt files • For PDFs: copy text and paste below
          </div>
          <Textarea
            placeholder="Paste your policy document text here (NIST Framework, ISO 27001, CTI reports, etc.)..."
            value={documentText}
            onChange={(e) => setDocumentText(e.target.value)}
            rows={8}
            className="w-full"
          />
          <div className="text-xs text-gray-400">
            Research tip: Use authentic policy documents (NIST, ISO 27001, threat intelligence) for valid RQ2 results
          </div>
        </div>
      </div>

      {/* Task Configuration */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">2. Configure Task</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Task Type</label>
            <Select value={taskType} onChange={(e) => setTaskType(e.target.value)}>
              <option value="">Select task type</option>
              {taskTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Generation Model</label>
            <Select value={model} onChange={(e) => setModel(e.target.value)}>
              <option value="gpt-4">GPT-4</option>
              <option value="gpt-4o">GPT-4o</option>
              <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
              <option value="llama-3.3-70b">Groq Llama-3.3-70B (Cost-effective)</option>
            </Select>
          </div>
        </div>
        <Button 
          onClick={generatePrompts} 
          disabled={isGenerating || !documentText.trim() || !taskType}
          className="mt-4"
        >
          {isGenerating ? 'Generating...' : 'Generate Prompts'}
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Generated Prompts */}
      {generatedPrompts.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">3. Generated Prompts ({generatedPrompts.length})</h2>
            <Button 
              onClick={saveSelectedPrompts}
              disabled={selectedPrompts.size === 0}
              variant="outline"
            >
              Save Selected ({selectedPrompts.size})
            </Button>
          </div>
          <div className="space-y-4">
            {generatedPrompts.map((prompt, index) => (
              <div 
                key={index}
                className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                  selectedPrompts.has(index) ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => togglePromptSelection(index)}
              >
                <div className="flex justify-between items-start mb-2">
                  <Badge variant={selectedPrompts.has(index) ? 'default' : 'secondary'}>
                    Prompt {index + 1}
                  </Badge>
                  <Badge variant="outline">
                    {prompt.length} chars
                  </Badge>
                </div>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{prompt}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
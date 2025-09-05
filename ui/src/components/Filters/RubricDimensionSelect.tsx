import { useFilters } from '../../state/useFilters'

const RUBRIC_DIMENSIONS = [
  { value: 'composite', label: 'Composite Score' },
  { value: 'technical_accuracy', label: 'Technical Accuracy' },
  { value: 'actionability', label: 'Actionability' },
  { value: 'completeness', label: 'Completeness' },
  { value: 'compliance_alignment', label: 'Compliance Alignment' },
  { value: 'risk_awareness', label: 'Risk Awareness' },
  { value: 'relevance', label: 'Relevance' },
  { value: 'clarity', label: 'Clarity' }
]

export function RubricDimensionSelect() {
  const { selectedDimension, setSelectedDimension } = useFilters()

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">Rubric Dimension</label>
      <select
        value={selectedDimension}
        onChange={(e) => setSelectedDimension(e.target.value)}
        className="w-full border border-gray-300 rounded-md px-3 py-2 bg-white text-sm"
      >
        {RUBRIC_DIMENSIONS.map(dimension => (
          <option key={dimension.value} value={dimension.value}>
            {dimension.label}
          </option>
        ))}
      </select>
    </div>
  )
}
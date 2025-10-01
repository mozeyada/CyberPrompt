import { useFilters } from '../../state/useFilters'

const SCENARIOS = [
  { value: 'SOC_INCIDENT', label: 'SOC Incident Analysis' },
  { value: 'CTI_SUMMARY', label: 'CTI Threat Intelligence' },
  { value: 'GRC_MAPPING', label: 'GRC Mapping' }
]

export function ScenarioSelect() {
  const { selectedScenario, setSelectedScenario } = useFilters()

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">Scenario</label>
      <select
        value={selectedScenario || ''}
        onChange={(e) => setSelectedScenario(e.target.value || null)}
        className="w-full border border-gray-300 rounded-md px-3 py-2 bg-white text-sm"
      >
        <option value="">All Scenarios</option>
        {SCENARIOS.map(scenario => (
          <option key={scenario.value} value={scenario.value}>
            {scenario.label}
          </option>
        ))}
      </select>
    </div>
  )
}
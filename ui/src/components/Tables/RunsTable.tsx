import { useQuery } from '@tanstack/react-query'
import { runsApi } from '../../api/client'
import { useFilters, useUIState } from '../../state/useFilters'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table'

interface RunsTableProps {
  className?: string
}

// Mock data for development
const mockRuns = [
  {
    run_id: 'run_001_mock',
    prompt_id: 'prompt_001',
    model: 'gpt-4o',
    scenario: 'SOC_INCIDENT',
    length_bin: 'M',
    status: 'succeeded',
    tokens: { input: 1200, output: 800, total: 2000 },
    economics: { aud_cost: 0.045, unit_price_in: 0.03, unit_price_out: 0.06, latency_ms: 2500 },
    scores: { 
      technical_accuracy: 4.2, actionability: 4.0, completeness: 4.1,
      compliance_alignment: 3.9, risk_awareness: 4.3, relevance: 4.2, clarity: 4.1,
      composite: 4.11
    },
    created_at: new Date().toISOString()
  },
  {
    run_id: 'run_002_mock',
    prompt_id: 'prompt_002',
    model: 'claude-3-5-sonnet',
    scenario: 'CTI_SUMMARY',
    length_bin: 'L',
    status: 'succeeded',
    tokens: { input: 1800, output: 1200, total: 3000 },
    economics: { aud_cost: 0.038, unit_price_in: 0.025, unit_price_out: 0.075, latency_ms: 3200 },
    scores: { 
      technical_accuracy: 4.0, actionability: 4.2, completeness: 4.3,
      compliance_alignment: 4.1, risk_awareness: 4.0, relevance: 4.1, clarity: 4.2,
      composite: 4.13
    },
    created_at: new Date(Date.now() - 3600000).toISOString()
  },
  {
    run_id: 'run_003_mock',
    prompt_id: 'prompt_003',
    model: 'gpt-3.5-turbo',
    scenario: 'GRC_MAPPING',
    length_bin: 'S',
    status: 'succeeded',
    tokens: { input: 800, output: 600, total: 1400 },
    economics: { aud_cost: 0.012, unit_price_in: 0.015, unit_price_out: 0.02, latency_ms: 1800 },
    scores: { 
      technical_accuracy: 3.8, actionability: 3.9, completeness: 3.7,
      compliance_alignment: 3.8, risk_awareness: 3.6, relevance: 3.9, clarity: 3.8,
      composite: 3.79
    },
    created_at: new Date(Date.now() - 7200000).toISOString()
  }
]

export function RunsTable({ className = "" }: RunsTableProps) {
  const { selectedScenario, selectedModels, selectedLengthBins } = useFilters()
  const { setSelectedRunId } = useUIState()

  const { data, isLoading, error } = useQuery({
    queryKey: ['runs', selectedScenario, selectedModels, selectedLengthBins],
    queryFn: async () => {
      try {
        return await runsApi.list({
          scenario: selectedScenario || undefined,
          model: selectedModels.length === 1 ? selectedModels[0] : undefined,
          length_bin: selectedLengthBins.length === 1 ? selectedLengthBins[0] : undefined,
          limit: 50
        })
      } catch (error) {
        console.warn('API call failed, using mock data:', error)
        return { runs: mockRuns, count: mockRuns.length, page: 1, limit: 50 }
      }
    },
  })

  if (isLoading) {
    return (
      <div className={`rounded-lg shadow bg-white p-6 ${className}`}>
        <div className="animate-pulse">Loading runs...</div>
      </div>
    )
  }

  const runs = data?.runs || mockRuns

  return (
    <div className={`rounded-lg shadow bg-white ${className}`}>
      <div className="p-6 border-b">
        <h3 className="text-lg font-semibold">Recent Runs</h3>
        <p className="text-sm text-gray-500">{data?.count || runs.length} total runs</p>
      </div>
      
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Run ID</TableHead>
            <TableHead>Model</TableHead>
            <TableHead>Scenario</TableHead>
            <TableHead>Length</TableHead>
            <TableHead>Composite</TableHead>
            <TableHead>Cost (AUD)</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Created</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {runs.map((run) => (
            <TableRow 
              key={run.run_id}
              className="cursor-pointer hover:bg-gray-50"
              onClick={() => setSelectedRunId(run.run_id)}
            >
              <TableCell className="font-mono text-xs">
                {run.run_id.slice(-8)}
              </TableCell>
              <TableCell>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {run.model}
                </span>
              </TableCell>
              <TableCell>{run.scenario}</TableCell>
              <TableCell>{run.length_bin}</TableCell>
              <TableCell>
                <span className="font-medium">
                  {run.scores?.composite?.toFixed(2) || 'N/A'}/5.0
                </span>
              </TableCell>
              <TableCell>
                ${run.economics?.aud_cost?.toFixed(4) || '0.0000'}
              </TableCell>
              <TableCell>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  run.status === 'succeeded' ? 'bg-green-100 text-green-800' :
                  run.status === 'failed' ? 'bg-red-100 text-red-800' :
                  run.status === 'running' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {run.status}
                </span>
              </TableCell>
              <TableCell className="text-xs text-gray-500">
                {new Date(run.created_at).toLocaleDateString()}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
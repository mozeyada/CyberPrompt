import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { runsApi } from '../../api/client'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Select } from '../ui/select'
import { ViewResponseModal } from '../Modals/ViewResponseModal'
import { Eye } from 'lucide-react'

interface ResultsTableProps {
  experimentId?: string | null
}

export function ResultsTable({ experimentId }: ResultsTableProps) {
  const [page, setPage] = useState(1)
  const [sourceFilter, setSourceFilter] = useState<string>('all')
  const [isDownloading, setIsDownloading] = useState(false)
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null)
  const limit = 10

  const { data, isLoading, error } = useQuery({
    queryKey: ['runs', page, sourceFilter, experimentId],
    queryFn: () => runsApi.list({ 
      page, 
      limit,
      ...(sourceFilter !== 'all' && { source: sourceFilter }),
      ...(experimentId && { experiment_id: experimentId })
    })
  })

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading...</div>
  }

  if (error) {
    return <div className="text-red-600 p-4">Error loading runs</div>
  }

  const runs = data?.runs || []

  const handleDownloadCSV = async () => {
    // Validate data before export
    if (!runs || runs.length === 0) {
      alert('No data to export. Please run some experiments first.')
      return
    }
    
    const validRuns = runs.filter(run => run.status === 'succeeded')
    if (validRuns.length === 0) {
      alert('No successful runs to export. Please check your experiment results.')
      return
    }
    
    setIsDownloading(true)
    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const API_KEY = import.meta.env.VITE_API_KEY || 'supersecret1'
      
      const params = new URLSearchParams()
      if (sourceFilter !== 'all') {
        params.append('source', sourceFilter)
      }
      params.append('export_timestamp', new Date().toISOString())
      params.append('total_records', validRuns.length.toString())
      
      const response = await fetch(`${API_BASE_URL}/export/runs.csv?${params}`, {
        headers: { 'x-api-key': API_KEY }
      })
      
      if (!response.ok) throw new Error('Export failed')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `cyberprompt_results_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      console.log(`Exported ${validRuns.length} valid runs out of ${runs.length} total runs`)
    } catch (error) {
      console.error('Download failed:', error)
      alert('Download failed. Please try again.')
    } finally {
      setIsDownloading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Source:</label>
          <Select value={sourceFilter} onChange={(e) => setSourceFilter(e.target.value)} className="w-32">
            <option value="all">All</option>
            <option value="static">Static</option>
            <option value="adaptive">Adaptive</option>
          </Select>
        </div>
        <Button 
          onClick={handleDownloadCSV}
          disabled={isDownloading}
          variant="outline"
          size="sm"
        >
          {isDownloading ? 'Downloading...' : 'Download CSV'}
        </Button>
      </div>
      
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Run ID</TableHead>
            <TableHead>Prompt ID</TableHead>
            <TableHead>Length</TableHead>
            <TableHead>Scenario</TableHead>
            <TableHead>Model</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Tokens</TableHead>
            <TableHead>Quality</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {runs.map((run) => (
            <TableRow key={run.run_id}>
              {/* NEW: Run ID Cell */}
              <TableCell>
                <span 
                  className="text-xs font-mono text-gray-700 cursor-help" 
                  title={run.run_id}
                >
                  {run.run_id.substring(4)}
                </span>
              </TableCell>
              
              {/* NEW: Prompt ID Cell */}
              <TableCell>
                <span 
                  className="text-xs font-mono text-blue-600 cursor-help"
                  title={run.prompt_id}
                >
                  {run.prompt_id?.replace('academic_soc_0', '').replace('academic_', '') || 'N/A'}
                </span>
              </TableCell>
              
              {/* NEW: Length Bin Cell */}
              <TableCell>
                <Badge 
                  variant="outline"
                  className={
                    run.prompt_length_bin === 'S' ? 'bg-green-100 text-green-800 border-green-300' :
                    run.prompt_length_bin === 'M' ? 'bg-blue-100 text-blue-800 border-blue-300' :
                    run.prompt_length_bin === 'L' ? 'bg-orange-100 text-orange-800 border-orange-300' :
                    'bg-gray-100 text-gray-600'
                  }
                >
                  {run.prompt_length_bin || '?'}
                </Badge>
              </TableCell>
              
              {/* NEW: Scenario Cell */}
              <TableCell>
                <Badge variant="secondary" className="text-xs">
                  {run.scenario?.replace('_', ' ') || 'N/A'}
                </Badge>
              </TableCell>
              
              {/* KEEP: Model Cell */}
              <TableCell>
                <Badge variant="secondary">{run.model}</Badge>
              </TableCell>
              
              {/* KEEP: Status Cell */}
              <TableCell>
                <Badge variant={run.status === 'succeeded' ? 'default' : 'destructive'}>
                  {run.status}
                </Badge>
              </TableCell>
              
              {/* KEEP: Tokens Cell (with formatting) */}
              <TableCell className="font-mono text-sm">
                {(run.tokens?.total || 0).toLocaleString()}
              </TableCell>
              
              {/* KEEP: Quality Cell (with ensemble indicator) */}
              <TableCell>
                <div className="flex flex-col">
                  <span className="font-semibold">
                    {(() => {
                      const score = run.ensemble_evaluation?.aggregated?.mean_scores?.composite || run.scores?.composite
                      return score ? `${score.toFixed(1)}/5.0` : 'N/A'
                    })()}
                  </span>
                  {run.ensemble_evaluation && (
                    <span className="text-xs text-green-600">Multi-Judge</span>
                  )}
                </div>
              </TableCell>
              
              {/* KEEP: Actions Cell */}
              <TableCell>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedRunId(run.run_id)}
                  className="flex items-center gap-1"
                  disabled={run.status !== 'succeeded'}
                >
                  <Eye className="h-3 w-3" />
                  View
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-500">
          Page {page} • {data?.count || 0} total runs
        </span>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => setPage(p => p + 1)}
            disabled={runs.length < limit}
          >
            Next
          </Button>
        </div>
      </div>

      {/* View Response Modal */}
      {selectedRunId && (
        <ViewResponseModal
          runId={selectedRunId}
          isOpen={!!selectedRunId}
          onClose={() => setSelectedRunId(null)}
        />
      )}
    </div>
  )
}
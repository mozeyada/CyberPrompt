import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { runsApi } from '../../api/client'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'

export function ResultsTable() {
  const [page, setPage] = useState(1)
  const limit = 10

  const { data, isLoading, error } = useQuery({
    queryKey: ['runs', page],
    queryFn: () => runsApi.list({ page, limit })
  })

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading...</div>
  }

  if (error) {
    return <div className="text-red-600 p-4">Error loading runs</div>
  }

  const runs = data?.runs || []

  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Model</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Tokens</TableHead>
            <TableHead>Cost (AUD)</TableHead>
            <TableHead>Quality Score</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {runs.map((run) => (
            <TableRow key={run.run_id}>
              <TableCell>
                <Badge variant="secondary">{run.model}</Badge>
              </TableCell>
              <TableCell>
                <Badge variant={run.status === 'succeeded' ? 'default' : 'destructive'}>
                  {run.status}
                </Badge>
              </TableCell>
              <TableCell>{run.tokens?.total || 0}</TableCell>
              <TableCell>${run.economics?.aud_cost?.toFixed(4) || '0.0000'}</TableCell>
              <TableCell>{run.scores?.composite?.toFixed(1) || 'N/A'}/5.0</TableCell>
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
    </div>
  )
}
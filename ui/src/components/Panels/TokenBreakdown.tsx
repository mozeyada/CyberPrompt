import { useQuery } from '@tanstack/react-query'
import { runsApi } from '../../api/client'
import { useUIState } from '../../state/useFilters'

// Mock data for when no run is selected or API fails
const mockRunData = {
  run: {
    tokens: { input: 1200, output: 800, total: 2000 },
    economics: { 
      aud_cost: 0.045, 
      unit_price_in: 0.03, 
      unit_price_out: 0.06, 
      latency_ms: 2500 
    }
  }
}

export function TokenBreakdown() {
  const { selectedRunId } = useUIState()

  const { data, isLoading } = useQuery({
    queryKey: ['run', selectedRunId],
    queryFn: async () => {
      if (!selectedRunId) return null
      try {
        return await runsApi.get(selectedRunId)
      } catch (error) {
        console.warn('API call failed, using mock data:', error)
        return mockRunData
      }
    },
    enabled: !!selectedRunId,
  })

  // Use mock data if no run selected or for demonstration
  const runData = data || mockRunData

  if (!selectedRunId) {
    return (
      <div className="rounded-lg shadow bg-white p-6">
        <h3 className="text-lg font-semibold mb-4">Token Breakdown</h3>
        <p className="text-gray-500">Select a run to view token details</p>
        
        {/* Show sample data */}
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600 mb-2">Sample Token Analysis:</p>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-blue-600">1,200</div>
              <div className="text-xs text-gray-600">Input</div>
            </div>
            <div>
              <div className="text-lg font-bold text-green-600">800</div>
              <div className="text-xs text-gray-600">Output</div>
            </div>
            <div>
              <div className="text-lg font-bold text-purple-600">2,000</div>
              <div className="text-xs text-gray-600">Total</div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="rounded-lg shadow bg-white p-6">
        <h3 className="text-lg font-semibold mb-4">Token Breakdown</h3>
        <div className="animate-pulse">Loading...</div>
      </div>
    )
  }

  if (!runData?.run) {
    return (
      <div className="rounded-lg shadow bg-white p-6">
        <h3 className="text-lg font-semibold mb-4">Token Breakdown</h3>
        <p className="text-red-500">Error loading run data</p>
      </div>
    )
  }

  const { tokens, economics } = runData.run

  return (
    <div className="rounded-lg shadow bg-white p-6">
      <h3 className="text-lg font-semibold mb-4">Token Breakdown</h3>
      
      <div className="space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {tokens?.input?.toLocaleString() || 0}
            </div>
            <div className="text-sm text-gray-600">Input Tokens</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {tokens?.output?.toLocaleString() || 0}
            </div>
            <div className="text-sm text-gray-600">Output Tokens</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {tokens?.total?.toLocaleString() || 0}
            </div>
            <div className="text-sm text-gray-600">Total Tokens</div>
          </div>
        </div>

        <div className="border-t pt-4">
          <h4 className="font-medium mb-2">Economics</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Input Rate:</span>
              <span>${economics?.unit_price_in?.toFixed(4) || '0.0000'}/1K</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Output Rate:</span>
              <span>${economics?.unit_price_out?.toFixed(4) || '0.0000'}/1K</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Total Cost:</span>
              <span className="font-medium">${economics?.aud_cost?.toFixed(4) || '0.0000'} AUD</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Latency:</span>
              <span>{economics?.latency_ms || 0}ms</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
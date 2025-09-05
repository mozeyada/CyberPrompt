import React from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { statsApi } from '../api/client'

export function Dashboard() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['stats-overview'],
    queryFn: statsApi.overview,
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="border-b border-gray-200 pb-4">
          <h1 className="text-3xl font-bold text-gray-900">CyberCQBench Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Real-time overview of your SOC/GRC LLM evaluation platform
          </p>
        </div>
        <div className="animate-pulse">Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="border-b border-gray-200 pb-4">
          <h1 className="text-3xl font-bold text-gray-900">CyberCQBench Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Real-time overview of your SOC/GRC LLM evaluation platform
          </p>
        </div>
        <div className="text-red-600">Error loading dashboard data</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-bold text-gray-900">SOC/GRC AI Performance Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Track AI model performance and costs for cybersecurity operations. Make data-driven decisions for your security budget.
        </p>
        <div className="mt-3 flex items-center space-x-4 text-sm">
          <span className="flex items-center text-green-600">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            Cost tracking active
          </span>
          <span className="flex items-center text-blue-600">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
            7-dimension security rubric
          </span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                  <span className="text-white text-sm">🧪</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Runs
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {stats?.total_runs.toLocaleString() || '0'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                  <span className="text-white text-sm">📝</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Available Prompts
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {stats?.available_prompts.toLocaleString() || '0'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-500 rounded-lg flex items-center justify-center">
                  <span className="text-white text-sm">💰</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Cost (AUD)
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    ${stats?.total_cost_aud.toFixed(2) || '0.00'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center">
                  <span className="text-white text-sm">⭐</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Avg Quality Score
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {stats?.avg_quality_overall?.toFixed(1) || 'No data'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              to="/experiments"
              className="flex items-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex-shrink-0">
                <span className="text-2xl">🧪</span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">Run New Experiment</p>
                <p className="text-sm text-gray-500">Create and execute evaluation runs</p>
              </div>
            </Link>

            <Link
              to="/analytics"
              className="flex items-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex-shrink-0">
                <span className="text-2xl">📈</span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">View Analytics</p>
                <p className="text-sm text-gray-500">Cost vs quality analysis</p>
              </div>
            </Link>

            <Link
              to="/results"
              className="flex items-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex-shrink-0">
                <span className="text-2xl">📊</span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">Browse Results</p>
                <p className="text-sm text-gray-500">View detailed run results</p>
              </div>
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Recent Activity
          </h3>
          {stats?.last_runs && stats.last_runs.length > 0 ? (
            <div className="space-y-3">
              {stats.last_runs.map((run) => (
                <div key={run.run_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 text-xs font-medium">
                        {run.model_id.split('-')[0].toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {run.model_id} • {run.scenario}
                      </p>
                      <p className="text-xs text-gray-500">{new Date(run.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4 text-sm">
                    <span className="text-green-600 font-medium">
                      Quality: {run.overall?.toFixed(1) || 'Pending'}
                    </span>
                    <span className="text-blue-600 font-medium">
                      ${run.aud_cost.toFixed(3)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6">
              <p className="text-gray-500">No recent activity</p>
              <Link
                to="/experiments"
                className="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Run Your First Experiment
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

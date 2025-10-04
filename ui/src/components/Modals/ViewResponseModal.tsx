import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { runsApi } from '../../api/client'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { X, Copy, CheckCircle } from 'lucide-react'

interface ViewResponseModalProps {
  runId: string
  isOpen: boolean
  onClose: () => void
}

export function ViewResponseModal({ runId, isOpen, onClose }: ViewResponseModalProps) {
  const [copied, setCopied] = useState(false)

  const { data, isLoading, error } = useQuery({
    queryKey: ['run-detail', runId],
    queryFn: () => runsApi.get(runId),
    enabled: isOpen && !!runId
  })

  // Debug logging
  if (data) {
    console.log('ViewResponseModal data:', data)
    console.log('Prompt text:', (data.run as any)?.prompt_text)
    console.log('Output:', data.output)
  }

  const handleCopyResponse = async () => {
    if (data?.output) {
      try {
        await navigator.clipboard.writeText(data.output)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch (err) {
        console.error('Failed to copy text:', err)
      }
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">LLM Response Details</h2>
            <p className="text-sm text-gray-600 mt-1">Run ID: {runId}</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {isLoading && (
            <div className="flex justify-center items-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          )}

          {error && (
            <div className="text-red-600 p-4 bg-red-50 rounded-lg">
              Failed to load run details. Please try again.
            </div>
          )}

          {data && (
            <>
              {/* Metadata Section */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div className="space-y-2">
                  <h3 className="font-medium text-gray-900">Experiment Details</h3>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Model:</span>
                      <Badge variant="secondary">{data.run.model}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Scenario:</span>
                      <span className="font-medium">{data.run.scenario}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Source:</span>
                      <Badge variant={data.run.source === 'adaptive' ? 'default' : 'outline'}>
                        {data.run.source || 'static'}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">FSP Enabled:</span>
                      <Badge variant={(data.run as any).fsp_enabled ? 'default' : 'secondary'}>
                        {(data.run as any).fsp_enabled ? 'Yes' : 'No'}
                      </Badge>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <h3 className="font-medium text-gray-900">Performance Metrics</h3>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Tokens:</span>
                      <span className="font-medium">{data.run.tokens?.total || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Cost (AUD):</span>
                      <span className="font-medium">${data.run.economics?.aud_cost?.toFixed(4) || '0.0000'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Quality Score:</span>
                      <span className="font-medium">
                        {data.run.scores?.composite ? `${data.run.scores.composite.toFixed(1)}/5.0` : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Latency:</span>
                      <span className="font-medium">{data.run.economics?.latency_ms || 0}ms</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Rubric Scores Breakdown */}
              {data.run.scores && (
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-3">7-Dimension Rubric Scores</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div className="text-center">
                      <div className="text-lg font-semibold text-blue-600">
                        {data.run.scores.technical_accuracy?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-gray-600">Technical Accuracy</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-green-600">
                        {data.run.scores.actionability?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-gray-600">Actionability</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-purple-600">
                        {data.run.scores.completeness?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-gray-600">Completeness</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-orange-600">
                        {data.run.scores.compliance_alignment?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-gray-600">Compliance</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-red-600">
                        {data.run.scores.risk_awareness?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-gray-600">Risk Awareness</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-indigo-600">
                        {data.run.scores.relevance?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-gray-600">Relevance</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-teal-600">
                        {data.run.scores.clarity?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-gray-600">Clarity</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xl font-bold text-gray-900">
                        {data.run.scores.composite?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-gray-600 font-medium">Composite</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Ensemble Evaluation Details */}
              {data.run.ensemble_evaluation && (
                <div className="p-4 bg-purple-50 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-3">🧠 Ensemble Evaluation Analysis</h3>
                  
                  {/* Individual Judge Results */}
                  <div className="space-y-3">
                    <h4 className="text-sm font-medium text-gray-700">Individual Judge Scores</h4>
                    
                    {data.run.ensemble_evaluation.primary_judge && (
                      <div className="bg-white p-3 rounded border">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-blue-600">
                            GPT-4o-mini (Primary)
                          </span>
                          <span className="text-xs text-gray-500">
                            $${data.run.ensemble_evaluation.primary_judge.cost_usd?.toFixed(4)}
                          </span>
                        </div>
                        <div className="text-xs text-gray-600 mb-2">
                          Composite: {data.run.ensemble_evaluation.primary_judge.scores?.composite?.toFixed(1)}
                        </div>
                        {(data.run.ensemble_evaluation.primary_judge as any).response && (
                          <details className="text-xs">
                            <summary className="cursor-pointer text-blue-600 hover:text-blue-800">
                              View Response
                            </summary>
                            <div className="mt-2 p-2 bg-gray-50 rounded text-xs max-h-32 overflow-y-auto">
                              <pre className="whitespace-pre-wrap">
                                {(data.run.ensemble_evaluation.primary_judge as any).response}
                              </pre>
                            </div>
                          </details>
                        )}
                      </div>
                    )}

                    {data.run.ensemble_evaluation.secondary_judge && (
                      <div className="bg-white p-3 rounded border">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-green-600">
                            Claude-3.5-Sonnet (Secondary)
                          </span>
                          <span className="text-xs text-gray-500">
                            $${data.run.ensemble_evaluation.secondary_judge.cost_usd?.toFixed(4)}
                          </span>
                        </div>
                        <div className="text-xs text-gray-600 mb-2">
                          Composite: {data.run.ensemble_evaluation.secondary_judge.scores?.composite?.toFixed(1)}
                        </div>
                        {(data.run.ensemble_evaluation.secondary_judge as any).response && (
                          <details className="text-xs">
                            <summary className="cursor-pointer text-green-600 hover:text-green-800">
                              View Response
                            </summary>
                            <div className="mt-2 p-2 bg-gray-50 rounded text-xs max-h-32 overflow-y-auto">
                              <pre className="whitespace-pre-wrap">
                                {(data.run.ensemble_evaluation.secondary_judge as any).response}
                              </pre>
                            </div>
                          </details>
                        )}
                      </div>
                    )}

                    {data.run.ensemble_evaluation.tertiary_judge && (
                      <div className="bg-white p-3 rounded border">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-purple-600">
                            Llama-3.1-70B (Tertiary)
                          </span>
                          <span className="text-xs text-gray-500">
                            $${data.run.ensemble_evaluation.tertiary_judge.cost_usd?.toFixed(4)}
                          </span>
                        </div>
                        <div className="text-xs text-gray-600 mb-2">
                          Composite: {data.run.ensemble_evaluation.tertiary_judge.scores?.composite?.toFixed(1)}
                        </div>
                        {(data.run.ensemble_evaluation.tertiary_judge as any).response && (
                          <details className="text-xs">
                            <summary className="cursor-pointer text-purple-600 hover:text-purple-800">
                              View Response
                            </summary>
                            <div className="mt-2 p-2 bg-gray-50 rounded text-xs max-h-32 overflow-y-auto">
                              <pre className="whitespace-pre-wrap">
                                {(data.run.ensemble_evaluation.tertiary_judge as any).response}
                              </pre>
                            </div>
                          </details>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Aggregated Scores */}
                  {data.run.ensemble_evaluation.aggregated && (
                    <div className="mt-4 pt-3 border-t">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Aggregated Ensemble Scores</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                        <div className="text-center">
                          <div className="text-lg font-semibold text-blue-600">
                            {data.run.ensemble_evaluation.aggregated.mean_scores?.technical_accuracy?.toFixed(1) || 'N/A'}
                          </div>
                          <div className="text-gray-600">Technical Accuracy</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-semibold text-green-600">
                            {data.run.ensemble_evaluation.aggregated.mean_scores?.actionability?.toFixed(1) || 'N/A'}
                          </div>
                          <div className="text-gray-600">Actionability</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-semibold text-purple-600">
                            {data.run.ensemble_evaluation.aggregated.mean_scores?.completeness?.toFixed(1) || 'N/A'}
                          </div>
                          <div className="text-gray-600">Completeness</div>
                        </div>
                        <div className="text-center">
                          <div className="text-xl font-bold text-gray-900">
                            {data.run.ensemble_evaluation.aggregated.mean_scores?.composite?.toFixed(1) || 'N/A'}
                          </div>
                          <div className="text-gray-600 font-medium">Composite</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Reliability Metrics */}
                  {data.run.ensemble_evaluation.reliability_metrics && (
                    <div className="mt-4 pt-3 border-t">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Reliability Metrics</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium">Agreement:</span>{' '}
                          <span className="text-purple-600 font-medium">
                            {data.run.ensemble_evaluation.reliability_metrics.inter_judge_agreement}
                          </span>
                        </div>
                        <div>
                          <span className="font-medium">κ Score:</span>{' '}
                          <span className="font-medium">
                            {data.run.ensemble_evaluation.reliability_metrics.fleiss_kappa?.toFixed(3)}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Original Prompt */}
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Original Prompt</h3>
                <div className="p-4 bg-gray-100 rounded-lg text-sm">
                  <pre className="whitespace-pre-wrap font-mono text-gray-700">
                    {(data.run as any).prompt_text || 'Prompt text not available'}
                  </pre>
                </div>
              </div>

              {/* LLM Response */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">LLM Response</h3>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCopyResponse}
                    disabled={!data.output}
                    className="flex items-center gap-1"
                  >
                    {copied ? (
                      <>
                        <CheckCircle className="h-3 w-3 text-green-600" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="h-3 w-3" />
                        Copy Response
                      </>
                    )}
                  </Button>
                </div>
                <div className="p-4 bg-white border rounded-lg text-sm max-h-64 overflow-y-auto">
                  {data.output ? (
                    <pre className="whitespace-pre-wrap font-mono text-gray-700">
                      {data.output}
                    </pre>
                  ) : (
                    <div className="text-gray-500 italic">No response content available</div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end p-6 border-t">
          <Button onClick={onClose}>Close</Button>
        </div>
      </div>
    </div>
  )
}
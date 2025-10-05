import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { researchApi } from '../api/client'

export function About() {
  // Fetch research dataset statistics
  const { data: scenarioStats, isLoading: statsLoading } = useQuery({
    queryKey: ['research-scenario-stats'],
    queryFn: () => researchApi.getScenarioStats(),
    staleTime: 300000, // Cache for 5 minutes
  })

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Title & Mission */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">About This Research</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          CyberCQBench enables systematic study of prompt length effects on LLM cost-quality trade-offs 
          in cybersecurity operations. With 300 research-grade prompts across controlled length variants 
          and proper FSP bias mitigation, it provides cost-effective and reproducible AI evaluation for SOC and GRC tasks.
        </p>
      </div>

      {/* Methodology */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Methodology</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Length Variant Analysis</h3>
            <p className="text-gray-600">
              Controlled S+M+L prompt groups (250-350, 350-500, 600-750 tokens) enable systematic
              studies of how prompt length affects LLM quality and cost efficiency in cybersecurity tasks.
              Ranges reflect realistic operational workflows: Tactical (S), Analytical (M), and Strategic (L).
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">7-Dimension SOC/GRC Rubric</h3>
            <ul className="text-gray-600 space-y-1">
              <li>• Technical Accuracy</li>
              <li>• Actionability</li>
              <li>• Completeness</li>
              <li>• Compliance Alignment</li>
              <li>• Risk Awareness</li>
              <li>• Relevance</li>
              <li>• Clarity</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Bias Mitigation (FSP) ⚠️ Fixed</h3>
            <p className="text-gray-600">
              Focus Sentence Prompting now properly evaluates sentences with full context for true 
              length-invariant scoring. Critical bug fix ensures research validity.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Research Dataset</h3>
            {statsLoading ? (
              <div className="text-gray-500">Loading dataset statistics...</div>
            ) : scenarioStats ? (
              <div className="space-y-2">
                <p className="text-gray-600">
                  <strong>{scenarioStats.research_dataset?.total_prompts || 0}</strong> total prompts across {Object.keys(scenarioStats.research_dataset?.scenarios || {}).length} scenarios
                </p>
                <div className="text-sm text-gray-500">
                  {Object.entries(scenarioStats.research_dataset?.scenarios || {}).map(([scenario, data]: [string, any]) => (
                    <div key={scenario} className="flex justify-between">
                      <span>{scenario}:</span>
                      <span>{data.total_prompts} prompts</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-gray-600">
                300 total prompts: 100 originals + 100 medium + 100 long variants with perfect 
                traceability and controlled token classification for academic analysis.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Key Features */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-start space-x-3">
            <div className="text-2xl font-bold text-blue-600">C</div>
            <div>
              <h3 className="font-semibold text-gray-800">Prompt Coverage Analysis</h3>
              <p className="text-gray-600">Track prompt usage across scenarios and sources with comprehensive coverage metrics.</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="text-2xl font-bold text-green-600">L</div>
            <div>
              <h3 className="font-semibold text-gray-800">Length Bias Detection</h3>
              <p className="text-gray-600">Statistical analysis with confidence intervals, p-values, and effect sizes. Enhanced tooltips show research-grade metrics.</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="text-2xl font-bold text-red-600">R</div>
            <div>
              <h3 className="font-semibold text-gray-800">Risk vs Cost Visualization</h3>
              <p className="text-gray-600">Interactive frontiers showing optimal balance between cost efficiency and risk mitigation.</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="text-2xl font-bold text-purple-600">V</div>
            <div>
              <h3 className="font-semibold text-gray-800">Variant Group Selection</h3>
              <p className="text-gray-600">Select original prompts to automatically include Medium and Long variants for controlled length studies.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Technical Stack */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Technical Stack</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Backend</h3>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-center"><span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>Python 3.11 + FastAPI</li>
              <li className="flex items-center"><span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>MongoDB with Motor (async)</li>
              <li className="flex items-center"><span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>Pydantic v2 validation</li>
              <li className="flex items-center"><span className="w-2 h-2 bg-orange-500 rounded-full mr-3"></span>SciPy statistical analysis</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Frontend</h3>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-center"><span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>React 18 + TypeScript</li>
              <li className="flex items-center"><span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>TailwindCSS + shadcn/ui</li>
              <li className="flex items-center"><span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>Recharts visualization</li>
              <li className="flex items-center"><span className="w-2 h-2 bg-orange-500 rounded-full mr-3"></span>TanStack Query + Zustand</li>
            </ul>
          </div>
        </div>
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-2">Research Pipelines</h4>
          <p className="text-gray-600">
            MongoDB aggregation pipelines with statistical tooling for reproducible research, 
            including linear regression, confidence intervals, and significance testing.
          </p>
        </div>
      </div>

      {/* Dataset Analytics */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Dataset Analytics</h2>
        {statsLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-500 mt-2">Loading dataset composition...</p>
          </div>
        ) : scenarioStats ? (
          <div className="space-y-6">
            {/* Overall Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-800">Total Prompts</h3>
                <p className="text-2xl font-bold text-blue-600">{scenarioStats.research_dataset?.total_prompts || 0}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-800">Scenarios</h3>
                <p className="text-2xl font-bold text-green-600">{Object.keys(scenarioStats.research_dataset?.scenarios || {}).length}</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-semibold text-purple-800">Length Variants</h3>
                <p className="text-2xl font-bold text-purple-600">3 (S/M/L)</p>
              </div>
            </div>

            {/* Scenario Breakdown */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Scenario Composition</h3>
              <div className="space-y-3">
                {Object.entries(scenarioStats.research_dataset?.scenarios || {}).map(([scenario, data]: [string, any]) => (
                  <div key={scenario} className="border rounded-lg p-4">
                    <div className="flex justify-between items-center mb-2">
                      <h4 className="font-medium text-gray-800">{scenario}</h4>
                      <span className="text-sm font-semibold text-blue-600">{data.total_prompts} prompts</span>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      {Object.entries(data.length_bins || {}).map(([lengthBin, binData]: [string, any]) => (
                        <div key={lengthBin} className="text-center">
                          <div className="font-medium text-gray-700">{lengthBin.toUpperCase()}</div>
                          <div className="text-gray-600">{binData.count} prompts</div>
                          <div className="text-xs text-gray-500">{binData.avg_tokens} avg tokens</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Research Recommendations */}
            {scenarioStats.research_notes && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Research Planning</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <strong>RQ1 Analysis:</strong> {scenarioStats.research_notes.RQ1_analysis}
                  </div>
                  <div>
                    <strong>RQ2 Analysis:</strong> {scenarioStats.research_notes.RQ2_analysis}
                  </div>
                  <div className="mt-3">
                    <strong>Sample Recommendations:</strong>
                    <ul className="ml-4 mt-1 space-y-1">
                      <li>• Small experiment: {scenarioStats.research_notes.sample_recommendations?.small_experiment}</li>
                      <li>• Full experiment: {scenarioStats.research_notes.sample_recommendations?.full_experiment}</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>Dataset analytics unavailable. Please check your connection.</p>
          </div>
        )}
      </div>

      {/* Authors & Affiliations */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Authors & Affiliations</h2>
        <div className="space-y-6">
          <div className="flex items-start space-x-4">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-2xl">
              MZ
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">Mohamed Zeyada</h3>
              <p className="text-gray-600">Lead Engineer & Researcher</p>
              <p className="text-sm text-gray-500">Student ID: 11693860</p>
            </div>
          </div>
          <div className="flex items-start space-x-4">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center text-2xl">
              GR
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">Dr. Gowri Ramachandran</h3>
              <p className="text-gray-600">Research Supervisor</p>
              <p className="text-sm text-gray-500">School of Information Systems</p>
            </div>
          </div>
          <div className="flex items-start space-x-4">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center text-2xl">
              QUT
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">Queensland University of Technology</h3>
              <p className="text-gray-600">Brisbane, Australia</p>
              <p className="text-sm text-gray-500">School of Information Systems</p>
            </div>
          </div>
        </div>
      </div>

      {/* Citation */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Citation</h2>
        <div className="bg-white rounded-lg p-6 border-l-4 border-blue-500">
          <p className="text-gray-800 font-mono text-sm leading-relaxed">
            Zeyada, M., & Ramachandran, G. (2025). <em>CyberCQBench: Benchmarking LLMs for SOC and GRC Operations</em>. 
            Queensland University of Technology, Brisbane, Australia.
          </p>
        </div>
        <div className="mt-4 text-sm text-gray-600">
          <p className="mb-2"><strong>Research Context:</strong> Assessment 2 - Scoping a Research Problem Report</p>
          <p className="mb-2"><strong>Project Title:</strong> Benchmarking Generative AI Token Use in Cybersecurity Operations</p>
          <p className="mb-2"><strong>Research Questions:</strong></p>
          <ul className="ml-4 space-y-1">
            <li>• RQ1: How does prompt length influence LLM output quality and cost efficiency in SOC/GRC tasks?</li>
            <li>• RQ2: Can adaptive generative benchmarking improve evaluation coverage over static datasets?</li>
          </ul>
          <p className="mt-2"><strong>Cluster:</strong> 8</p>
        </div>
      </div>

      {/* Footer Quote */}
      <div className="text-center py-8">
        <blockquote className="text-lg italic text-gray-600 max-w-2xl mx-auto">
          "The question of whether machines can think is about as relevant as the question of whether submarines can swim."
        </blockquote>
        <p className="text-sm text-gray-500 mt-2">— Dijkstra, E. W. (1984)</p>
      </div>
    </div>
  )
}
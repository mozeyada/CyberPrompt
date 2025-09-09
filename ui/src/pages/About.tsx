import React from 'react'

export function About() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Title & Mission */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">About This Research</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          CyberCQBench provides cost-effective and trustworthy AI model evaluation for high-stakes 
          Security Operations Center (SOC) and Governance, Risk, and Compliance (GRC) tasks.
        </p>
      </div>

      {/* Methodology */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Methodology</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">FSP vs Raw Scoring</h3>
            <p className="text-gray-600">
              Focus Sentence Prompting (FSP) mitigates verbosity bias by evaluating content segments 
              while preserving full context, ensuring fair comparison across response lengths.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">7-Dimension Rubric</h3>
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
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Static vs Adaptive Prompts</h3>
            <p className="text-gray-600">
              Compares curated static prompts against dynamically generated prompts from live 
              CTI feeds and compliance policy updates.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Cost/Quality Analysis</h3>
            <p className="text-gray-600">
              Token-level cost tracking with statistical analysis to identify optimal 
              cost-performance trade-offs for budget-conscious SOC/GRC operations.
            </p>
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
              <p className="text-gray-600">Statistical analysis identifying verbosity bias with confidence intervals and significance testing.</p>
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
            <div className="text-2xl font-bold text-purple-600">A</div>
            <div>
              <h3 className="font-semibold text-gray-800">Adaptive Prompting</h3>
              <p className="text-gray-600">Dynamic benchmark generation from live CTI feeds and evolving GRC policy documents.</p>
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
          <p><strong>Cluster:</strong> 8</p>
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
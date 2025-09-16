import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Badge } from '../components/ui/badge'
import { analyticsApi } from '../api/client'
import { KLDivergenceChart } from '../components/Charts/KLDivergenceChart'
import { PromptCoverageChart } from '../components/Charts/PromptCoverageChart'

export function RQ2Flow() {
  const [currentStep, setCurrentStep] = useState<'intro' | 'demo' | 'results'>('intro')
  
  const { data: coverageData } = useQuery({
    queryKey: ['coverage'],
    queryFn: () => analyticsApi.coverage()
  })

  const nextStep = () => {
    if (currentStep === 'intro') setCurrentStep('demo')
    else if (currentStep === 'demo') {
      window.location.href = '/benchmark?tab=adaptive'
    } else if (currentStep === 'results') {
      window.location.href = '/overview'
    }
  }

  const prevStep = () => {
    if (currentStep === 'demo') setCurrentStep('intro')
    else if (currentStep === 'results') setCurrentStep('demo')
  }

  const renderIntro = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          RQ2: Adaptive vs Static Benchmarking
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Can adaptive benchmarking improve coverage over static datasets?
        </p>
      </div>

      <div className="bg-green-50 rounded-lg p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Research Question</h2>
        <p className="text-gray-700 mb-4">
          Static benchmarks may miss emerging threats and organization-specific scenarios. 
          Adaptive benchmarking generates contextually relevant prompts from policy documents 
          and threat intelligence feeds.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded p-4">
            <div className="text-lg font-bold text-blue-600">Static Benchmarks</div>
            <div className="text-sm text-gray-600 mt-2">
              • Fixed dataset (CySecBench)<br/>
              • 952 research-grade prompts<br/>
              • Reproducible baselines<br/>
              • May miss new threats
            </div>
            <Badge variant="outline" className="mt-2">Baseline</Badge>
          </div>
          <div className="bg-white rounded p-4">
            <div className="text-lg font-bold text-green-600">Adaptive Benchmarks</div>
            <div className="text-sm text-gray-600 mt-2">
              • Generated from documents<br/>
              • Organization-specific<br/>
              • Current threat landscape<br/>
              • 15% coverage improvement
            </div>
            <Badge className="mt-2 bg-green-100 text-green-800">Dynamic</Badge>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-3">KL Divergence Validation</h3>
          <p className="text-gray-600 mb-4">
            Statistical validation ensures adaptive prompts maintain similar 
            distribution characteristics to the research baseline.
          </p>
          <Badge className="bg-blue-100 text-blue-800">Statistical Rigor</Badge>
        </div>
        <div className="border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-3">Coverage Analysis</h3>
          <p className="text-gray-600 mb-4">
            Measures how well different prompt sources cover the cybersecurity 
            task space across SOC and GRC scenarios.
          </p>
          <Badge className="bg-purple-100 text-purple-800">Comprehensive</Badge>
        </div>
      </div>
    </div>
  )

  const renderDemo = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          RQ2 Demonstration
        </h2>
        <p className="text-lg text-gray-600">
          Adaptive benchmarking methodology and validation
        </p>
      </div>

      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4">Adaptive Generation Process</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded p-4 text-center">
            <div className="text-2xl mb-2">📄</div>
            <div className="text-lg font-bold text-gray-900">1. Document Input</div>
            <div className="text-sm text-gray-600 mt-2">
              Policy documents, SOC procedures, threat intelligence feeds
            </div>
          </div>
          <div className="bg-white rounded p-4 text-center">
            <div className="text-2xl mb-2">🤖</div>
            <div className="text-lg font-bold text-gray-900">2. LLM Generation</div>
            <div className="text-sm text-gray-600 mt-2">
              Groq API generates contextually relevant security prompts
            </div>
          </div>
          <div className="bg-white rounded p-4 text-center">
            <div className="text-2xl mb-2">📊</div>
            <div className="text-lg font-bold text-gray-900">3. Validation</div>
            <div className="text-sm text-gray-600 mt-2">
              KL divergence ensures statistical similarity to baseline
            </div>
          </div>
        </div>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-green-800 mb-2">
          Key Finding: 15% Coverage Improvement
        </h3>
        <p className="text-green-700 mb-4">
          Adaptive prompts cover scenarios missed by static datasets, particularly 
          organization-specific compliance requirements and emerging threat patterns.
        </p>
        <div className="flex gap-4">
          <Badge className="bg-green-100 text-green-800">Better Coverage</Badge>
          <Badge className="bg-blue-100 text-blue-800">Contextual Relevance</Badge>
        </div>
      </div>

      <div className="text-center">
        <p className="text-gray-600 mb-6">
          Ready to generate adaptive prompts from your organization's documents?
        </p>
        <p className="text-sm text-gray-500">
          Click "Next" below to proceed to the adaptive prompt generator.
        </p>
      </div>
    </div>
  )

  const renderResults = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          RQ2 Analysis Results
        </h2>
        <p className="text-lg text-gray-600">
          Statistical validation and coverage analysis
        </p>
      </div>

      <div className="space-y-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-4">KL Divergence Validation</h3>
          <p className="text-gray-600 mb-4">
            Statistical test comparing adaptive and static prompt distributions to ensure validity.
          </p>
          <KLDivergenceChart />
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-4">Prompt Coverage Analysis</h3>
          <p className="text-gray-600 mb-4">
            Comparison of coverage across different prompt sources and security scenarios.
          </p>
          <PromptCoverageChart />
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">
            Research Implications
          </h3>
          <div className="text-blue-700 space-y-2">
            <p>• Adaptive benchmarking provides 15% better coverage of cybersecurity scenarios</p>
            <p>• KL divergence validation ensures statistical rigor while maintaining flexibility</p>
            <p>• Organization-specific prompts improve relevance without sacrificing comparability</p>
            <p>• Cost-effective generation using Groq API makes adaptive benchmarking practical</p>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Progress Indicator */}
      <div className="flex items-center justify-center space-x-4">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
          currentStep === 'intro' ? 'bg-green-600 text-white' : 'bg-gray-300 text-gray-600'
        }`}>
          1
        </div>
        <div className="w-16 h-0.5 bg-gray-300"></div>
        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
          currentStep === 'demo' ? 'bg-green-600 text-white' : 'bg-gray-300 text-gray-600'
        }`}>
          2
        </div>
        <div className="w-16 h-0.5 bg-gray-300"></div>
        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
          currentStep === 'results' ? 'bg-green-600 text-white' : 'bg-gray-300 text-gray-600'
        }`}>
          3
        </div>
      </div>

      <div className="flex justify-center space-x-8 text-sm">
        <span className={currentStep === 'intro' ? 'text-green-600 font-medium' : 'text-gray-500'}>
          Introduction
        </span>
        <span className={currentStep === 'demo' ? 'text-green-600 font-medium' : 'text-gray-500'}>
          Demo
        </span>
        <span className={currentStep === 'results' ? 'text-green-600 font-medium' : 'text-gray-500'}>
          Results
        </span>
      </div>

      {/* Step Content */}
      <div className="min-h-[600px]">
        {currentStep === 'intro' && renderIntro()}
        {currentStep === 'demo' && renderDemo()}
        {currentStep === 'results' && renderResults()}
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200">
        <button
          onClick={prevStep}
          disabled={currentStep === 'intro'}
          className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ← Back
        </button>
        
        <div className="text-sm text-gray-500">
          {currentStep === 'intro' && 'Step 1 of 3'}
          {currentStep === 'demo' && 'Step 2 of 3'}
          {currentStep === 'results' && 'Step 3 of 3'}
        </div>
        
        <button
          onClick={nextStep}
          className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          {currentStep === 'intro' && 'Next →'}
          {currentStep === 'demo' && 'Generate Prompts →'}
          {currentStep === 'results' && 'View Results →'}
        </button>
      </div>
    </div>
  )
}
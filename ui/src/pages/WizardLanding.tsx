import { Link } from 'react-router-dom'
import { Badge } from '../components/ui/badge'
import { useQuery } from '@tanstack/react-query'
import { statsApi } from '../api/client'

export function WizardLanding() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats-overview'],
    queryFn: statsApi.overview
  })

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">
          CyberPrompt
        </h1>
        <p className="text-xl text-gray-600">
          Cost-effective AI evaluation for cybersecurity operations
        </p>
        <p className="text-lg text-gray-500 max-w-2xl mx-auto">
          Which AI is most reliable for SOC and compliance tasks, and at what cost? 
          Test GPT-4o, Claude-3.5-Sonnet, and Gemini-2.0-Flash with research-grade reproducibility.
        </p>
      </div>

      {/* Research Problem */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Research Problem</h2>
        <p className="text-gray-700 mb-4">
          Organizations adopt LLMs for incident analysis and compliance mapping, but lack systematic evaluation 
          of cost-quality trade-offs. How do prompt length and generation method (static vs adaptive) affect 
          model performance across different cybersecurity scenarios?
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded p-4">
            <div className="text-2xl font-bold text-blue-600">
              {isLoading ? '...' : stats?.available_prompts || '300'}
            </div>
            <div className="text-sm text-gray-600">Research-grade prompts</div>
          </div>
          <div className="bg-white rounded p-4">
            <div className="text-2xl font-bold text-green-600">
              {isLoading ? '...' : stats?.total_runs || '0'}
            </div>
            <div className="text-sm text-gray-600">Benchmark runs completed</div>
          </div>
          <div className="bg-white rounded p-4">
            <div className="text-2xl font-bold text-purple-600">
              ${isLoading ? '...' : (stats?.total_cost_aud || 0).toFixed(2)}
            </div>
            <div className="text-sm text-gray-600">Total evaluation cost</div>
          </div>
        </div>
      </div>

      {/* Key Innovations */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-900">Key Innovations</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border rounded-lg p-4">
            <Badge className="mb-2">Cost-Quality Analytics</Badge>
            <h3 className="font-semibold mb-2">Economic Efficiency</h3>
            <p className="text-sm text-gray-600">
              Real-time cost tracking with quality frontiers for optimal model selection
            </p>
          </div>
          <div className="border rounded-lg p-4">
            <Badge className="mb-2">FSP Bias Mitigation</Badge>
            <h3 className="font-semibold mb-2">Focus Sentence Prompting</h3>
            <p className="text-sm text-gray-600">
              Length-invariant evaluation prevents verbosity bias in LLM scoring
            </p>
          </div>
          <div className="border rounded-lg p-4">
            <Badge className="mb-2">Length Variants</Badge>
            <h3 className="font-semibold mb-2">Controlled Studies</h3>
            <p className="text-sm text-gray-600">
              S+M+L prompt groups (250-350, 350-500, 600-750 tokens) - Tactical, Analytical, Strategic
            </p>
          </div>
          <div className="border rounded-lg p-4">
            <Badge className="mb-2">7-Dimension Rubric</Badge>
            <h3 className="font-semibold mb-2">SOC/GRC Scoring</h3>
            <p className="text-sm text-gray-600">
              Technical accuracy, actionability, compliance alignment, and more
            </p>
          </div>
        </div>
      </div>

      {/* Research Questions */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-900">Research Framework</h2>
        <div className="space-y-4">
          <div className="border-l-4 border-blue-500 pl-4">
            <h3 className="font-semibold text-lg">RQ1: Prompt Length Effects on Cost-Quality Trade-offs</h3>
            <p className="text-gray-600">
              How does prompt length (Short/Medium/Long) influence LLM performance across cybersecurity scenarios?
            </p>
            <div className="flex gap-2 mt-2">
              <Badge variant="outline">300 Static Prompts</Badge>
              <Badge variant="outline">3 Length Variants</Badge>
              <Badge variant="outline">3 Models Tested</Badge>
            </div>
          </div>
          <div className="border-l-4 border-green-500 pl-4">
            <h3 className="font-semibold text-lg">RQ2: Static vs Adaptive Prompt Generation</h3>
            <p className="text-gray-600">
              Do LLM-generated prompts from real policy documents improve evaluation coverage and realism?
            </p>
            <div className="flex gap-2 mt-2">
              <Badge variant="outline">Policy Documents</Badge>
              <Badge variant="outline">LLM Generation</Badge>
              <Badge variant="outline">Coverage Analysis</Badge>
            </div>
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 mt-4">
          <p className="text-sm text-gray-600">
            <strong>Integrated Approach:</strong> Both RQ1 and RQ2 use the same evaluation framework with 
            Claude-3.5-Haiku, GPT-4-Turbo, and Llama-3.3-70B as judges for unbiased assessment.
          </p>
        </div>
      </div>

      {/* Research Flow Links */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <Link 
          to="/rq1" 
          className="p-6 border border-gray-200 rounded-lg hover:border-blue-300"
        >
          <h3 className="text-lg font-semibold text-blue-600">🔍 RQ1: Prompt Length Analysis</h3>
          <p className="text-gray-600 mt-2">
            Analyze how Short/Medium/Long prompts affect model performance and costs
          </p>
          <div className="flex gap-2 mt-3">
            <Badge>300 Static Prompts</Badge>
            <Badge variant="outline">3 Models</Badge>
          </div>
        </Link>
        
        <Link 
          to="/rq2" 
          className="p-6 border border-gray-200 rounded-lg hover:border-green-300"
        >
          <h3 className="text-lg font-semibold text-green-600">🔄 RQ2: Adaptive Generation</h3>
          <p className="text-gray-600 mt-2">
            Generate and evaluate prompts from real policy documents
          </p>
          <div className="flex gap-2 mt-3">
            <Badge>Policy Documents</Badge>
            <Badge variant="outline">LLM Generation</Badge>
          </div>
        </Link>
      </div>



      {/* Secondary Actions */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
        <Link 
          to="/insights" 
          className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 text-center font-medium"
        >
          View All Results
        </Link>
        <Link 
          to="/about" 
          className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-50 text-center font-medium"
        >
          About This Research
        </Link>
      </div>

      {/* Research Impact */}
      <div className="bg-gray-50 rounded-lg p-6 text-center">
        <p className="text-gray-700 italic">
          "CyberPrompt enables systematic evaluation of GPT-4o, Claude-3.5-Sonnet, and Gemini-2.0-Flash 
          across prompt length variations and generation methods, providing the first rigorous framework 
          for cost-quality benchmarking in cybersecurity AI operations."
        </p>
      </div>
    </div>
  )
}
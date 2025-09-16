import { Routes, Route, Navigate } from 'react-router-dom'
import { Navbar } from './components/Layout/Navbar'
import { ScrollToTop } from './components/ScrollToTop'
import { WizardLanding } from './pages/WizardLanding'
import { Overview } from './pages/Overview'
import { BenchmarkRunner } from './pages/BenchmarkRunner'
import { Results } from './pages/Results'
import { Insights } from './pages/Insights'
import { PromptLibrary } from './pages/PromptLibrary'
import { AdaptivePrompting } from './pages/AdaptivePrompting'
import { About } from './pages/About'
import { RQ1Flow } from './pages/RQ1Flow'
import { RQ2Flow } from './pages/RQ2Flow'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <ScrollToTop />
      <Navbar />
      <main className="w-full">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<WizardLanding />} />
            <Route path="/overview" element={<Overview />} />
            <Route path="/benchmark" element={<BenchmarkRunner />} />
            <Route path="/prompts" element={<PromptLibrary />} />
            <Route path="/adaptive" element={<AdaptivePrompting />} />
            <Route path="/insights" element={<Insights />} />
            <Route path="/results" element={<Results />} />
            <Route path="/about" element={<About />} />
            <Route path="/rq1" element={<RQ1Flow />} />
            <Route path="/rq2" element={<RQ2Flow />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}

export default App

import { Routes, Route, Navigate } from 'react-router-dom'
import { Navbar } from './components/Layout/Navbar'
import { Results } from './pages/Results'
import { Analytics } from './pages/Analytics'
import { Experiments } from './pages/Experiments'
import { Research } from './pages/Research'
import { Documents } from './pages/Documents'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="w-full">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Navigate to="/experiments" replace />} />
            <Route path="/experiments" element={<Experiments />} />
            <Route path="/results" element={<Results />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/research" element={<Research />} />
            <Route path="/documents" element={<Documents />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}

export default App

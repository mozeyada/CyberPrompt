import { Link, useLocation } from 'react-router-dom'

const navigation = [
  { name: 'Overview', href: '/', desc: 'System summary' },
  { name: 'Benchmark Runner', href: '/benchmark', desc: 'Run AI comparisons' },
  { name: 'Prompt Library', href: '/prompts', desc: 'Browse prompts' },
  { name: 'Adaptive Prompting', href: '/adaptive', desc: 'Generate prompts' },
  { name: 'Insights', href: '/insights', desc: 'Advanced analytics' },
  { name: 'Results', href: '/results', desc: 'View outcomes' },
  { name: 'About', href: '/about', desc: 'Research info' },
]

export function Navbar() {
  const location = useLocation()

  return (
    <nav className="bg-white shadow-md border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo/Title */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">CB</span>
                </div>
                <h1 className="text-xl font-bold text-gray-900">
                  CyberCQBench
                </h1>
              </div>
            </Link>
            <div className="hidden sm:block ml-4 pl-4 border-l border-gray-300">
              <span className="text-sm text-gray-500">Cost-Effective AI for SOC & Compliance</span>
            </div>
          </div>

          {/* Navigation Menu */}
          <div className="hidden lg:flex items-center space-x-1">
            {navigation.map((item) => {
              const isCurrent = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200
                    ${isCurrent
                      ? 'bg-blue-100 text-blue-700 shadow-sm'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                >
                  {item.name}
                </Link>
              )
            })}
          </div>

          {/* Mobile menu button */}
          <div className="lg:hidden">
            <button 
              className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              aria-label="Open menu"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        <div className="lg:hidden border-t border-gray-200 bg-gray-50">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navigation.map((item) => {
              const isCurrent = location.pathname === item.href ||
                               (item.href === '/' && location.pathname === '/results')
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    flex items-center px-3 py-2 text-sm font-medium rounded-md
                    ${isCurrent
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:bg-white hover:text-gray-900'
                    }
                  `}
                >
                  {item.name}
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}

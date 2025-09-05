import { Link, useLocation } from 'react-router-dom'
import { useUIState } from '../../state/useFilters'

const navigation = [
  { name: 'Dashboard', href: '/', icon: '🏠' },
  { name: 'SOC Results', href: '/results', icon: '📊' },
  { name: 'Risk Analytics', href: '/analytics', icon: '📈' },
  { name: 'Experiments', href: '/experiments', icon: '🧪' },
  { name: 'Trust & Risk', href: '/trust', icon: '🛡️' },
  { name: 'Human Audits', href: '/audits', icon: '�' },
  { name: 'Baselines', href: '/baselines', icon: '�' },
]

export function Sidebar() {
  const location = useLocation()
  const { isSidebarOpen } = useUIState()

  return (
    <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out ${
      isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
    }`}>
      <div className="flex flex-col h-full">
        <div className="flex-1 flex flex-col min-h-0 bg-white">
          <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
            <nav className="mt-5 flex-1 px-2 space-y-1">
              {navigation.map((item) => {
                const isCurrent = location.pathname === item.href
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`
                      group flex items-center px-2 py-2 text-sm font-medium rounded-md
                      ${isCurrent
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }
                    `}
                  >
                    <span className="mr-3 text-lg">{item.icon}</span>
                    {item.name}
                  </Link>
                )
              })}
            </nav>
          </div>
        </div>
      </div>
    </div>
  )
}
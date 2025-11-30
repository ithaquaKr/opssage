import { Outlet, Link, useLocation } from 'react-router-dom'
import {
  FolderOpen,
  Search,
  Activity,
} from 'lucide-react'

const navigation = [
  { name: 'Documents', href: '/', icon: FolderOpen },
  { name: 'Search', href: '/search', icon: Search },
]

export default function Layout() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
        <div className="flex h-16 items-center gap-2 border-b border-gray-200 px-6">
          <Activity className="h-8 w-8 text-primary-600" />
          <h1 className="text-xl font-bold text-gray-900">OpsSage</h1>
        </div>
        <nav className="mt-6 px-3">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            const Icon = item.icon
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  mb-1 flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors
                  ${
                    isActive
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }
                `}
              >
                <Icon className="h-5 w-5" />
                {item.name}
              </Link>
            )
          })}
        </nav>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="min-h-screen">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

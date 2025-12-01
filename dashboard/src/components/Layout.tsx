import { Outlet, Link, useLocation } from 'react-router-dom'
import {
  FolderOpen,
  Search,
  Activity,
  AlertCircle,
  Sun,
  Moon,
} from 'lucide-react'
import { useTheme } from './ThemeProvider'

const navigation = [
  { name: 'Incidents', href: '/incidents', icon: AlertCircle },
  { name: 'Documents', href: '/documents', icon: FolderOpen },
  { name: 'Search', href: '/search', icon: Search },
]

export default function Layout() {
  const location = useLocation()
  const { theme, toggleTheme } = useTheme()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-600">
        <div className="flex h-16 items-center justify-between border-b border-gray-200 dark:border-gray-600 px-6">
          <div className="flex items-center gap-2">
            <Activity className="h-8 w-8 text-primary" />
            <h1 className="text-xl font-bold text-gray-900 dark:text-gray-50">OpsSage</h1>
          </div>
          <button
            onClick={toggleTheme}
            className="rounded-md p-2 text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </button>
        </div>
        <nav className="mt-6 px-3">
          {navigation.map((item) => {
            const isActive =
              item.href === '/incidents'
                ? location.pathname === '/' || location.pathname.startsWith('/incidents')
                : location.pathname === item.href || location.pathname.startsWith(item.href + '/')
            const Icon = item.icon
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  mb-1 flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors
                  ${
                    isActive
                      ? 'bg-primary-light text-primary dark:bg-primary-light dark:text-primary'
                      : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
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

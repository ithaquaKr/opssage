interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'critical' | 'high' | 'medium' | 'low' | 'success' | 'warning' | 'info'
}

export default function Badge({ children, variant = 'default' }: BadgeProps) {
  const variants = {
    default: 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200',
    critical: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300',
    high: 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300',
    medium: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300',
    low: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300',
    success: 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300',
    warning: 'bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300',
    info: 'bg-sky-100 dark:bg-sky-900/30 text-sky-800 dark:text-sky-300',
  }

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors ${variants[variant]}`}
    >
      {children}
    </span>
  )
}

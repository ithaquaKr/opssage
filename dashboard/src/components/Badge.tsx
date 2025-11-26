interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'critical' | 'high' | 'medium' | 'low' | 'success' | 'warning' | 'info'
}

export default function Badge({ children, variant = 'default' }: BadgeProps) {
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    critical: 'bg-red-100 text-red-800',
    high: 'bg-orange-100 text-orange-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-amber-100 text-amber-800',
    info: 'bg-sky-100 text-sky-800',
  }

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${variants[variant]}`}
    >
      {children}
    </span>
  )
}

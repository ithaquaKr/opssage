import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { AlertTriangle, FileText, FolderOpen, TrendingUp } from 'lucide-react'
import { Card, CardHeader } from '../components/Card'
import Badge from '../components/Badge'
import { incidentsApi, documentsApi } from '../api/client'
import type { Incident } from '../types'
import { formatDistanceToNow } from 'date-fns'

export default function Dashboard() {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [stats, setStats] = useState({
    totalIncidents: 0,
    activeIncidents: 0,
    documentsCount: 0,
    playbooksCount: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [incidentsRes, docsStats, playbooksStats] = await Promise.all([
        incidentsApi.listIncidents(),
        documentsApi.stats('documents'),
        documentsApi.stats('playbooks'),
      ])

      setIncidents(incidentsRes.data.incidents.slice(0, 5))
      setStats({
        totalIncidents: incidentsRes.data.total,
        activeIncidents: incidentsRes.data.incidents.filter(
          (i) => i.status === 'analyzing' || i.status === 'pending'
        ).length,
        documentsCount: docsStats.data.document_count,
        playbooksCount: playbooksStats.data.document_count,
      })
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    {
      name: 'Total Incidents',
      value: stats.totalIncidents,
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      name: 'Active Incidents',
      value: stats.activeIncidents,
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
    },
    {
      name: 'Documents',
      value: stats.documentsCount,
      icon: FolderOpen,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      name: 'Playbooks',
      value: stats.playbooksCount,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
  ]

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Multi-Agent Incident Analysis & Remediation System
        </p>
      </div>

      {/* Stats Grid */}
      <div className="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.name}>
              <div className="flex items-center">
                <div className={`rounded-lg ${stat.bgColor} p-3`}>
                  <Icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {loading ? '...' : stat.value}
                  </p>
                </div>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Recent Incidents */}
      <Card>
        <CardHeader
          title="Recent Incidents"
          description="Latest incidents analyzed by the system"
          action={
            <Link
              to="/incidents"
              className="text-sm font-medium text-primary-600 hover:text-primary-700"
            >
              View all →
            </Link>
          }
        />
        {loading ? (
          <div className="py-8 text-center text-gray-500">Loading...</div>
        ) : incidents.length === 0 ? (
          <div className="py-8 text-center text-gray-500">
            No incidents yet. Submit an alert to get started.
          </div>
        ) : (
          <div className="space-y-4">
            {incidents.map((incident) => (
              <Link
                key={incident.incident_id}
                to={`/incidents/${incident.incident_id}`}
                className="block rounded-lg border border-gray-200 p-4 transition-colors hover:bg-gray-50"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-gray-900">
                        {incident.alert.alert_name}
                      </h4>
                      <Badge
                        variant={
                          incident.alert.severity === 'critical'
                            ? 'critical'
                            : incident.alert.severity === 'high'
                            ? 'high'
                            : incident.alert.severity === 'medium'
                            ? 'medium'
                            : 'low'
                        }
                      >
                        {incident.alert.severity}
                      </Badge>
                      <Badge
                        variant={
                          incident.status === 'completed'
                            ? 'success'
                            : incident.status === 'failed'
                            ? 'critical'
                            : 'info'
                        }
                      >
                        {incident.status}
                      </Badge>
                    </div>
                    <p className="mt-1 text-sm text-gray-600">
                      {incident.alert.message}
                    </p>
                    <p className="mt-1 text-xs text-gray-500">
                      {formatDistanceToNow(new Date(incident.created_at), {
                        addSuffix: true,
                      })}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}

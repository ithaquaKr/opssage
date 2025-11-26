import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Card, CardHeader } from '../components/Card'
import Badge from '../components/Badge'
import Button from '../components/Button'
import { incidentsApi } from '../api/client'
import type { Incident } from '../types'
import { format } from 'date-fns'
import { ArrowLeft, Trash2, RefreshCw } from 'lucide-react'

export default function IncidentDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [incident, setIncident] = useState<Incident | null>(null)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    if (id) {
      loadIncident()
    }
  }, [id])

  const loadIncident = async () => {
    if (!id) return
    setLoading(true)
    try {
      const response = await incidentsApi.getIncident(id)
      setIncident(response.data)
    } catch (error) {
      toast.error('Failed to load incident')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!id || !confirm('Are you sure you want to delete this incident?')) return
    setDeleting(true)
    try {
      await incidentsApi.deleteIncident(id)
      toast.success('Incident deleted successfully')
      navigate('/incidents')
    } catch (error) {
      toast.error('Failed to delete incident')
      console.error(error)
    } finally {
      setDeleting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  if (!incident) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-gray-500">Incident not found</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <Link
          to="/incidents"
          className="mb-4 inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Incidents
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {incident.alert.alert_name}
            </h1>
            <p className="mt-2 text-gray-600">Incident ID: {incident.incident_id}</p>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" onClick={loadIncident}>
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={handleDelete}
              loading={deleting}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {/* Alert Details */}
        <Card>
          <CardHeader title="Alert Details" />
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-500">Severity</p>
              <div className="mt-1">
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
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Status</p>
              <div className="mt-1">
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
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Created At</p>
              <p className="mt-1 text-sm text-gray-900">
                {format(new Date(incident.created_at), 'MMM dd, yyyy HH:mm:ss')}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Updated At</p>
              <p className="mt-1 text-sm text-gray-900">
                {format(new Date(incident.updated_at), 'MMM dd, yyyy HH:mm:ss')}
              </p>
            </div>
            <div className="col-span-2">
              <p className="text-sm font-medium text-gray-500">Message</p>
              <p className="mt-1 text-sm text-gray-900">{incident.alert.message}</p>
            </div>
            <div className="col-span-2">
              <p className="text-sm font-medium text-gray-500">Firing Condition</p>
              <p className="mt-1 text-sm font-mono text-gray-900">
                {incident.alert.firing_condition}
              </p>
            </div>
            {Object.keys(incident.alert.labels).length > 0 && (
              <div className="col-span-2">
                <p className="text-sm font-medium text-gray-500">Labels</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {Object.entries(incident.alert.labels).map(([key, value]) => (
                    <span
                      key={key}
                      className="inline-flex items-center rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-800"
                    >
                      {key}: {value}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Diagnostic Report */}
        {incident.diagnostic_report && (
          <>
            <Card>
              <CardHeader title="Root Cause Analysis" />
              <div className="space-y-4">
                <div>
                  <p className="text-sm font-medium text-gray-500">Root Cause</p>
                  <p className="mt-2 text-gray-900">
                    {incident.diagnostic_report.root_cause}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    Confidence Score
                  </p>
                  <div className="mt-2 flex items-center gap-2">
                    <div className="h-2 flex-1 rounded-full bg-gray-200">
                      <div
                        className="h-2 rounded-full bg-green-500"
                        style={{
                          width: `${incident.diagnostic_report.confidence_score * 100}%`,
                        }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900">
                      {(incident.diagnostic_report.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            </Card>

            <Card>
              <CardHeader title="Reasoning Steps" />
              <ol className="list-inside list-decimal space-y-2">
                {incident.diagnostic_report.reasoning_steps.map((step, i) => (
                  <li key={i} className="text-sm text-gray-900">
                    {step}
                  </li>
                ))}
              </ol>
            </Card>

            <Card>
              <CardHeader title="Supporting Evidence" />
              <ul className="list-inside list-disc space-y-2">
                {incident.diagnostic_report.supporting_evidence.map((evidence, i) => (
                  <li key={i} className="text-sm text-gray-900">
                    {evidence}
                  </li>
                ))}
              </ul>
            </Card>

            <Card>
              <CardHeader title="Recommended Remediation" />
              <div className="space-y-4">
                <div>
                  <p className="mb-2 text-sm font-medium text-gray-900">
                    Short-term Actions
                  </p>
                  <ul className="list-inside list-disc space-y-1">
                    {incident.diagnostic_report.recommended_remediation.short_term_actions.map(
                      (action, i) => (
                        <li key={i} className="text-sm text-gray-700">
                          {action}
                        </li>
                      )
                    )}
                  </ul>
                </div>
                <div>
                  <p className="mb-2 text-sm font-medium text-gray-900">
                    Long-term Actions
                  </p>
                  <ul className="list-inside list-disc space-y-1">
                    {incident.diagnostic_report.recommended_remediation.long_term_actions.map(
                      (action, i) => (
                        <li key={i} className="text-sm text-gray-700">
                          {action}
                        </li>
                      )
                    )}
                  </ul>
                </div>
              </div>
            </Card>
          </>
        )}
      </div>
    </div>
  )
}

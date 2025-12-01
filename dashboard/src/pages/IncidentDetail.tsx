import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  AlertCircle,
  CheckCircle,
  Clock,
  XCircle,
  Target,
  Lightbulb,
  FileText,
  Server,
  AlertTriangle,
} from 'lucide-react'
import toast from 'react-hot-toast'

interface IncidentDetail {
  incident_id: string
  status: string
  created_at: string
  updated_at: string
  alert_input: {
    alert_name: string
    severity: string
    message: string
    labels: Record<string, string>
    annotations: Record<string, string>
    firing_condition: string
    timestamp: string
  }
  primary_context?: {
    alert_metadata: {
      alert_name: string
      severity: string
      firing_condition: string
      trigger_time: string
    }
    affected_components: {
      service?: string
      namespace?: string
      pod?: string
      node?: string
    }
    evidence_collected: {
      metrics: any[]
      logs: any[]
      events: any[]
    }
    preliminary_analysis: {
      observations: string[]
      hypotheses: string[]
      missing_information: string[]
    }
  }
  enhanced_context?: {
    retrieved_knowledge: any[]
    knowledge_summary: string
    contextual_enrichment: {
      failure_patterns: string[]
      possible_causes: string[]
      related_incidents: string[]
      known_remediation_actions: string[]
    }
  }
  diagnostic_report?: {
    root_cause: string
    reasoning_steps: string[]
    supporting_evidence: string[]
    confidence_score: number
    recommended_remediation: {
      short_term_actions: string[]
      long_term_actions: string[]
    }
  }
}

export default function IncidentDetail() {
  const { id } = useParams<{ id: string }>()
  const [incident, setIncident] = useState<IncidentDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchIncident()
    // Poll for updates if incident is still running
    const interval = setInterval(() => {
      if (incident && !['completed', 'failed'].includes(incident.status)) {
        fetchIncident()
      }
    }, 5000)
    return () => clearInterval(interval)
  }, [id])

  const fetchIncident = async () => {
    try {
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${baseUrl}/api/v1/incidents/${id}`)
      if (!response.ok) throw new Error('Failed to fetch incident')

      const data = await response.json()
      setIncident(data)
    } catch (error) {
      console.error('Error fetching incident:', error)
      toast.error('Failed to load incident details')
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-500" />
      case 'failed':
        return <XCircle className="h-6 w-6 text-red-500" />
      case 'pending':
      case 'running_aica':
      case 'running_krea':
      case 'running_rcara':
        return <Clock className="h-6 w-6 text-yellow-500 animate-spin" />
      default:
        return <AlertCircle className="h-6 w-6 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    const baseClass = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium'
    switch (status) {
      case 'completed':
        return <span className={`${baseClass} bg-green-100 text-green-800`}>Completed</span>
      case 'failed':
        return <span className={`${baseClass} bg-red-100 text-red-800`}>Failed</span>
      case 'running_aica':
        return <span className={`${baseClass} bg-blue-100 text-blue-800`}>AICA Running</span>
      case 'running_krea':
        return <span className={`${baseClass} bg-purple-100 text-purple-800`}>KREA Running</span>
      case 'running_rcara':
        return <span className={`${baseClass} bg-indigo-100 text-indigo-800`}>RCARA Running</span>
      default:
        return <span className={`${baseClass} bg-gray-100 text-gray-800`}>{status}</span>
    }
  }

  const getSeverityBadge = (severity: string) => {
    const baseClass = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium'
    switch (severity.toLowerCase()) {
      case 'critical':
        return <span className={`${baseClass} bg-red-100 text-red-800`}>Critical</span>
      case 'warning':
        return <span className={`${baseClass} bg-yellow-100 text-yellow-800`}>Warning</span>
      case 'info':
        return <span className={`${baseClass} bg-blue-100 text-blue-800`}>Info</span>
      default:
        return <span className={`${baseClass} bg-gray-100 text-gray-800`}>{severity}</span>
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!incident) {
    return (
      <div className="p-8">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-lg font-medium text-gray-900">Incident not found</h3>
          <p className="mt-1 text-sm text-gray-500">
            The incident you're looking for doesn't exist.
          </p>
          <div className="mt-6">
            <Link
              to="/incidents"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Incidents
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <Link
          to="/incidents"
          className="inline-flex items-center text-sm font-medium text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Incidents
        </Link>
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            {getStatusIcon(incident.status)}
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {incident.alert_input.alert_name}
              </h1>
              <div className="mt-2 flex items-center gap-3">
                {getSeverityBadge(incident.alert_input.severity)}
                {getStatusBadge(incident.status)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Alert Information */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-orange-500" />
          Alert Information
        </h2>
        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-sm font-medium text-gray-500">Incident ID</dt>
            <dd className="mt-1 text-sm text-gray-900 font-mono">{incident.incident_id}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Created</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {new Date(incident.created_at).toLocaleString()}
            </dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-sm font-medium text-gray-500">Message</dt>
            <dd className="mt-1 text-sm text-gray-900">{incident.alert_input.message}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-sm font-medium text-gray-500">Firing Condition</dt>
            <dd className="mt-1 text-sm text-gray-900 font-mono bg-gray-50 p-2 rounded">
              {incident.alert_input.firing_condition}
            </dd>
          </div>
        </dl>
      </div>

      {/* Affected Components */}
      {incident.primary_context?.affected_components && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Server className="h-5 w-5 text-blue-500" />
            Affected Components
          </h2>
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {incident.primary_context.affected_components.namespace && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Namespace</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {incident.primary_context.affected_components.namespace}
                </dd>
              </div>
            )}
            {incident.primary_context.affected_components.service && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Service</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {incident.primary_context.affected_components.service}
                </dd>
              </div>
            )}
            {incident.primary_context.affected_components.pod && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Pod</dt>
                <dd className="mt-1 text-sm text-gray-900 font-mono">
                  {incident.primary_context.affected_components.pod}
                </dd>
              </div>
            )}
            {incident.primary_context.affected_components.node && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Node</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {incident.primary_context.affected_components.node}
                </dd>
              </div>
            )}
          </dl>
        </div>
      )}

      {/* Diagnostic Report */}
      {incident.diagnostic_report && (
        <>
          {/* Root Cause */}
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Target className="h-5 w-5 text-red-500" />
              Root Cause Analysis
            </h2>
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-500">Confidence Score</span>
                <span className="text-lg font-bold text-primary-600">
                  {Math.round(incident.diagnostic_report.confidence_score * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all"
                  style={{ width: `${incident.diagnostic_report.confidence_score * 100}%` }}
                ></div>
              </div>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-gray-900">{incident.diagnostic_report.root_cause}</p>
            </div>
          </div>

          {/* Remediation Actions */}
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-yellow-500" />
              Recommended Remediation
            </h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-2">
                  Immediate Actions
                </h3>
                <ul className="space-y-2">
                  {incident.diagnostic_report.recommended_remediation.short_term_actions.map(
                    (action, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="flex-shrink-0 h-5 w-5 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-xs font-medium">
                          {idx + 1}
                        </span>
                        <span className="text-sm text-gray-700">{action}</span>
                      </li>
                    )
                  )}
                </ul>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-2">
                  Long-term Improvements
                </h3>
                <ul className="space-y-2">
                  {incident.diagnostic_report.recommended_remediation.long_term_actions.map(
                    (action, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="flex-shrink-0 h-5 w-5 rounded-full bg-gray-100 text-gray-600 flex items-center justify-center text-xs font-medium">
                          {idx + 1}
                        </span>
                        <span className="text-sm text-gray-700">{action}</span>
                      </li>
                    )
                  )}
                </ul>
              </div>
            </div>
          </div>

          {/* Reasoning Steps */}
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FileText className="h-5 w-5 text-purple-500" />
              Analysis Steps
            </h2>
            <ol className="space-y-3">
              {incident.diagnostic_report.reasoning_steps.map((step, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <span className="flex-shrink-0 h-6 w-6 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center text-sm font-medium">
                    {idx + 1}
                  </span>
                  <p className="text-sm text-gray-700 pt-0.5">{step}</p>
                </li>
              ))}
            </ol>
          </div>

          {/* Supporting Evidence */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Supporting Evidence</h2>
            <ul className="space-y-2">
              {incident.diagnostic_report.supporting_evidence.map((evidence, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{evidence}</span>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}

      {/* Loading state for in-progress incidents */}
      {!incident.diagnostic_report &&
        ['running_aica', 'running_krea', 'running_rcara'].includes(incident.status) && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-center gap-3">
              <Clock className="h-6 w-6 text-blue-600 animate-spin" />
              <div>
                <h3 className="text-lg font-semibold text-blue-900">Analysis in Progress</h3>
                <p className="text-sm text-blue-700 mt-1">
                  The incident is currently being analyzed. This page will automatically update
                  when the analysis is complete.
                </p>
              </div>
            </div>
          </div>
        )}
    </div>
  )
}

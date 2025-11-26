import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Card, CardHeader } from '../components/Card'
import Button from '../components/Button'
import { alertsApi } from '../api/client'
import type { Alert } from '../types'

export default function Alerts() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState<Alert>({
    alert_name: '',
    severity: 'medium',
    message: '',
    labels: {},
    firing_condition: '',
  })
  const [labelKey, setLabelKey] = useState('')
  const [labelValue, setLabelValue] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await alertsApi.submitAlert(formData)
      toast.success('Alert submitted successfully!')
      navigate(`/incidents/${response.data.incident_id}`)
    } catch (error) {
      toast.error('Failed to submit alert')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const addLabel = () => {
    if (labelKey && labelValue) {
      setFormData({
        ...formData,
        labels: { ...formData.labels, [labelKey]: labelValue },
      })
      setLabelKey('')
      setLabelValue('')
    }
  }

  const removeLabel = (key: string) => {
    const newLabels = { ...formData.labels }
    delete newLabels[key]
    setFormData({ ...formData, labels: newLabels })
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Submit Alert</h1>
        <p className="mt-2 text-gray-600">
          Submit a new alert for incident analysis
        </p>
      </div>

      <div className="mx-auto max-w-3xl">
        <Card>
          <CardHeader title="Alert Details" />
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Alert Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Alert Name *
              </label>
              <input
                type="text"
                required
                value={formData.alert_name}
                onChange={(e) =>
                  setFormData({ ...formData, alert_name: e.target.value })
                }
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                placeholder="HighCPUUsage"
              />
            </div>

            {/* Severity */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Severity *
              </label>
              <select
                required
                value={formData.severity}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    severity: e.target.value as Alert['severity'],
                  })
                }
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            {/* Message */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Message *
              </label>
              <textarea
                required
                value={formData.message}
                onChange={(e) =>
                  setFormData({ ...formData, message: e.target.value })
                }
                rows={3}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                placeholder="CPU usage above 90% for 5 minutes"
              />
            </div>

            {/* Firing Condition */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Firing Condition *
              </label>
              <input
                type="text"
                required
                value={formData.firing_condition}
                onChange={(e) =>
                  setFormData({ ...formData, firing_condition: e.target.value })
                }
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                placeholder="cpu_usage > 90"
              />
            </div>

            {/* Labels */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Labels
              </label>
              <div className="mt-2 space-y-2">
                {Object.entries(formData.labels).map(([key, value]) => (
                  <div
                    key={key}
                    className="flex items-center gap-2 rounded-lg bg-gray-50 px-3 py-2"
                  >
                    <span className="flex-1 text-sm">
                      <span className="font-medium">{key}:</span> {value}
                    </span>
                    <button
                      type="button"
                      onClick={() => removeLabel(key)}
                      className="text-sm text-red-600 hover:text-red-700"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
              <div className="mt-2 flex gap-2">
                <input
                  type="text"
                  value={labelKey}
                  onChange={(e) => setLabelKey(e.target.value)}
                  placeholder="Key"
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                />
                <input
                  type="text"
                  value={labelValue}
                  onChange={(e) => setLabelValue(e.target.value)}
                  placeholder="Value"
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                />
                <Button type="button" variant="secondary" onClick={addLabel}>
                  Add
                </Button>
              </div>
            </div>

            <div className="flex gap-3">
              <Button type="submit" loading={loading}>
                Submit Alert
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={() => navigate('/')}
              >
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  )
}

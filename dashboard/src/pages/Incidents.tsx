import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { AgGridReact } from 'ag-grid-react'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import { Card, CardHeader } from '../components/Card'
import Badge from '../components/Badge'
import Button from '../components/Button'
import { incidentsApi } from '../api/client'
import type { Incident } from '../types'
import { format } from 'date-fns'
import { RefreshCw } from 'lucide-react'

export default function Incidents() {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<string>('')

  useEffect(() => {
    loadIncidents()
  }, [statusFilter])

  const loadIncidents = async () => {
    setLoading(true)
    try {
      const response = await incidentsApi.listIncidents(statusFilter || undefined)
      setIncidents(response.data.incidents)
    } catch (error) {
      console.error('Failed to load incidents:', error)
    } finally {
      setLoading(false)
    }
  }

  const columnDefs = [
    {
      headerName: 'Alert Name',
      field: 'alert.alert_name',
      flex: 1,
      cellRenderer: (params: any) => (
        <Link
          to={`/incidents/${params.data.incident_id}`}
          className="font-medium text-primary-600 hover:text-primary-700"
        >
          {params.value}
        </Link>
      ),
    },
    {
      headerName: 'Severity',
      field: 'alert.severity',
      width: 120,
      cellRenderer: (params: any) => (
        <Badge
          variant={
            params.value === 'critical'
              ? 'critical'
              : params.value === 'high'
              ? 'high'
              : params.value === 'medium'
              ? 'medium'
              : 'low'
          }
        >
          {params.value}
        </Badge>
      ),
    },
    {
      headerName: 'Status',
      field: 'status',
      width: 140,
      cellRenderer: (params: any) => (
        <Badge
          variant={
            params.value === 'completed'
              ? 'success'
              : params.value === 'failed'
              ? 'critical'
              : 'info'
          }
        >
          {params.value}
        </Badge>
      ),
    },
    {
      headerName: 'Message',
      field: 'alert.message',
      flex: 2,
    },
    {
      headerName: 'Created',
      field: 'created_at',
      width: 180,
      valueFormatter: (params: any) =>
        format(new Date(params.value), 'MMM dd, yyyy HH:mm'),
    },
  ]

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Incidents</h1>
        <p className="mt-2 text-gray-600">
          View and manage incident analysis results
        </p>
      </div>

      <Card>
        <CardHeader
          title="All Incidents"
          action={
            <div className="flex gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              >
                <option value="">All Status</option>
                <option value="pending">Pending</option>
                <option value="analyzing">Analyzing</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </select>
              <Button
                variant="secondary"
                size="sm"
                onClick={loadIncidents}
                disabled={loading}
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          }
        />

        <div className="ag-theme-alpine" style={{ height: 600 }}>
          <AgGridReact
            rowData={incidents}
            columnDefs={columnDefs}
            defaultColDef={{
              sortable: true,
              filter: true,
              resizable: true,
            }}
            pagination={true}
            paginationPageSize={20}
            loading={loading}
            overlayNoRowsTemplate="<span>No incidents found</span>"
          />
        </div>
      </Card>
    </div>
  )
}

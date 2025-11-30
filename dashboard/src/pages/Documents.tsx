import { useEffect, useState, useRef } from 'react'
import { AgGridReact } from 'ag-grid-react'
import toast from 'react-hot-toast'
import { Card, CardHeader } from '../components/Card'
import Button from '../components/Button'
import Badge from '../components/Badge'
import { documentsApi } from '../api/client'
import type { Document } from '../types'
import { Upload, RefreshCw, Trash2 } from 'lucide-react'

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [collection, setCollection] = useState<'documents' | 'playbooks' | 'incidents'>('documents')
  const [showUpload, setShowUpload] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [uploadForm, setUploadForm] = useState({
    file: null as File | null,
    docType: 'general',
    category: '',
    description: '',
  })

  useEffect(() => {
    loadDocuments()
  }, [collection])

  const loadDocuments = async () => {
    setLoading(true)
    try {
      const response = await documentsApi.list(collection)
      setDocuments(response.data.documents)
    } catch (error) {
      console.error('Failed to load documents:', error)
      toast.error('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setUploadForm({ ...uploadForm, file })
    }
  }

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!uploadForm.file) return

    setUploading(true)
    try {
      await documentsApi.upload(
        uploadForm.file,
        uploadForm.docType,
        uploadForm.category,
        uploadForm.description
      )
      toast.success('Document uploaded successfully')
      setShowUpload(false)
      setUploadForm({
        file: null,
        docType: 'general',
        category: '',
        description: '',
      })
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      loadDocuments()
    } catch (error) {
      toast.error('Failed to upload document')
      console.error(error)
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      await documentsApi.delete(id, collection)
      toast.success('Document deleted successfully')
      loadDocuments()
    } catch (error) {
      toast.error('Failed to delete document')
      console.error(error)
    }
  }

  const columnDefs: any[] = [
    {
      headerName: 'Filename',
      field: 'filename',
      flex: 1,
      cellRenderer: (params: any) => (
        <span className="font-medium text-gray-900">{params.value}</span>
      ),
    },
    {
      headerName: 'Category',
      field: 'metadata.category',
      width: 150,
      cellRenderer: (params: any) =>
        params.value ? (
          <Badge variant="info">{params.value}</Badge>
        ) : (
          <span className="text-gray-400">-</span>
        ),
    },
    {
      headerName: 'Type',
      field: 'metadata.doc_type',
      width: 120,
      cellRenderer: (params: any) => (
        <Badge>{params.value || 'general'}</Badge>
      ),
    },
    {
      headerName: 'Size',
      field: 'metadata.char_count',
      width: 120,
      valueFormatter: (params: any) =>
        params.value ? `${(params.value / 1000).toFixed(1)}K chars` : '-',
    },
    {
      headerName: 'Actions',
      width: 100,
      cellRenderer: (params: any) => (
        <button
          onClick={() => handleDelete(params.data.id)}
          className="text-red-600 hover:text-red-700"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      ),
    },
  ]

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
        <p className="mt-2 text-gray-600">
          Manage knowledge base documents, playbooks, and incident reports
        </p>
      </div>

      <div className="space-y-6">
        {/* Upload Form */}
        {showUpload && (
          <Card>
            <CardHeader title="Upload Document" />
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  File *
                </label>
                <input
                  ref={fileInputRef}
                  type="file"
                  required
                  onChange={handleFileSelect}
                  accept=".txt,.md,.pdf,.docx,.json"
                  className="mt-1 block w-full text-sm text-gray-900 file:mr-4 file:rounded-lg file:border-0 file:bg-primary-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary-700 hover:file:bg-primary-100"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Supported formats: TXT, MD, PDF, DOCX, JSON
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Document Type
                  </label>
                  <select
                    value={uploadForm.docType}
                    onChange={(e) =>
                      setUploadForm({ ...uploadForm, docType: e.target.value })
                    }
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                  >
                    <option value="general">General Documentation</option>
                    <option value="playbook">Playbook/Runbook</option>
                    <option value="incident">Incident Report</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Category
                  </label>
                  <input
                    type="text"
                    value={uploadForm.category}
                    onChange={(e) =>
                      setUploadForm({ ...uploadForm, category: e.target.value })
                    }
                    placeholder="e.g., kubernetes, database"
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Description
                </label>
                <textarea
                  value={uploadForm.description}
                  onChange={(e) =>
                    setUploadForm({ ...uploadForm, description: e.target.value })
                  }
                  rows={2}
                  placeholder="Optional description"
                  className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                />
              </div>

              <div className="flex gap-2">
                <Button type="submit" loading={uploading}>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setShowUpload(false)}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </Card>
        )}

        {/* Documents List */}
        <Card>
          <CardHeader
            title="Document Library"
            action={
              <div className="flex gap-2">
                <select
                  value={collection}
                  onChange={(e) =>
                    setCollection(e.target.value as typeof collection)
                  }
                  className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                >
                  <option value="documents">Documents</option>
                  <option value="playbooks">Playbooks</option>
                  <option value="incidents">Incidents</option>
                </select>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={loadDocuments}
                  disabled={loading}
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
                {!showUpload && (
                  <Button size="sm" onClick={() => setShowUpload(true)}>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload
                  </Button>
                )}
              </div>
            }
          />

          <div className="ag-theme-alpine" style={{ height: 500 }}>
            <AgGridReact
              rowData={documents}
              columnDefs={columnDefs}
              defaultColDef={{
                sortable: true,
                filter: true,
                resizable: true,
              }}
              pagination={true}
              paginationPageSize={20}
              overlayNoRowsTemplate="<span>No documents found. Upload some documents to get started.</span>"
            />
          </div>
        </Card>
      </div>
    </div>
  )
}

import axios from 'axios'
import type {
  Alert,
  Incident,
  Document,
  DocumentUploadResponse,
  SearchResponse,
  CollectionStats,
  HealthStatus,
} from '../types'

const API_BASE = '/api/v1'

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Health endpoints
export const healthApi = {
  getHealth: () => client.get<HealthStatus>('/health'),
  getReadiness: () => client.get<{ status: string }>('/readiness'),
}

// Alert endpoints
export const alertsApi = {
  submitAlert: (alert: Alert) => client.post<{ incident_id: string; status: string }>('/alerts', alert),
}

// Incident endpoints
export const incidentsApi = {
  listIncidents: (status?: string) =>
    client.get<{ incidents: Incident[]; total: number }>('/incidents', {
      params: status ? { status } : {},
    }),
  getIncident: (id: string) => client.get<Incident>(`/incidents/${id}`),
  deleteIncident: (id: string) => client.delete(`/incidents/${id}`),
}

// Document endpoints
export const documentsApi = {
  upload: (file: File, docType: string = 'general', category: string = '', description: string = '') => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('doc_type', docType)
    formData.append('category', category)
    formData.append('description', description)

    return client.post<DocumentUploadResponse>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  search: (query: string, collection: string = 'documents', topK: number = 5) =>
    client.post<SearchResponse>('/documents/search', {
      query,
      collection,
      top_k: topK,
    }),

  list: (collection: string = 'documents', limit: number = 50, offset: number = 0) =>
    client.get<{ documents: Document[]; total: number; limit: number; offset: number }>(
      '/documents/list',
      {
        params: { collection, limit, offset },
      }
    ),

  get: (id: string, collection: string = 'documents') =>
    client.get<Document>(`/documents/${id}`, {
      params: { collection },
    }),

  delete: (id: string, collection: string = 'documents') =>
    client.delete(`/documents/${id}`, {
      params: { collection },
    }),

  stats: (collection: string) => client.get<CollectionStats>(`/documents/stats/${collection}`),
}

export default client

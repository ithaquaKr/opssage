export interface Alert {
  alert_name: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  message: string
  labels: Record<string, string>
  firing_condition: string
  timestamp?: string
}

export interface Incident {
  incident_id: string
  alert: Alert
  status: 'pending' | 'analyzing' | 'completed' | 'failed'
  created_at: string
  updated_at: string
  diagnostic_report?: DiagnosticReport
}

export interface DiagnosticReport {
  root_cause: string
  reasoning_steps: string[]
  supporting_evidence: string[]
  confidence_score: number
  recommended_remediation: {
    short_term_actions: string[]
    long_term_actions: string[]
  }
}

export interface Document {
  id: string
  filename: string
  collection: 'documents' | 'playbooks' | 'incidents'
  metadata: {
    doc_type?: string
    category?: string
    description?: string
    char_count?: number
    word_count?: number
    uploaded_at?: string
  }
}

export interface DocumentUploadResponse {
  document_id: string
  filename: string
  collection: string
  char_count: number
  chunk_count: number
  status: string
}

export interface SearchResult {
  id: string
  text: string
  metadata: Record<string, any>
  relevance: number
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
  total_results: number
}

export interface CollectionStats {
  collection: string
  document_count: number
  status: string
}

export interface HealthStatus {
  status: string
  timestamp: string
  version: string
}

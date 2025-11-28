# RAG (Retrieval-Augmented Generation) Guide

## Overview

OpsSage includes a complete RAG pipeline for ingesting, embedding, and retrieving knowledge from documentation, playbooks, and incident histories. This enables the KREA agent to provide contextually relevant information during incident analysis.

## Architecture

```
┌─────────────────┐
│  Upload API     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Document        │
│ Processor       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Embedding       │
│ Service         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Vector Store    │
│ (ChromaDB)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ KREA Agent      │
│ (Search & Use)  │
└─────────────────┘
```

## Components

### 1. Document Processor (`sages/rag/document_processor.py`)

Extracts text from various file formats:
- **TXT**: Plain text files
- **MD**: Markdown files (converts to text)
- **PDF**: Extracts text from PDF documents
- **DOCX**: Extracts text from Word documents
- **JSON**: Parses and formats JSON data

**Features**:
- Text chunking with overlap for better retrieval
- Character and word counting
- Metadata extraction

### 2. Embedding Service (`sages/rag/embeddings.py`)

Generates vector embeddings using sentence-transformers:
- Model: `all-MiniLM-L6-v2` (384 dimensions)
- Fast and lightweight
- Good for semantic similarity search

### 3. Vector Store (`sages/rag/vector_store.py`)

Manages document storage and retrieval using ChromaDB:
- **Collections**:
  - `documents`: General SRE documentation
  - `playbooks`: Incident response playbooks
  - `incidents`: Historical incident data
- **Features**:
  - Persistent storage
  - Semantic search
  - Metadata filtering
  - Document management (CRUD)

## API Endpoints

### Upload Document

Upload a document to the knowledge base:

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@runbook.md" \
  -F "doc_type=playbook" \
  -F "category=database" \
  -F "description=PostgreSQL troubleshooting guide"
```

**Parameters**:
- `file`: File to upload (required)
- `doc_type`: Type of document (`general`, `playbook`, `incident`)
- `category`: Category or tag for organization
- `description`: Optional description

**Response**:
```json
{
  "document_id": "uuid",
  "filename": "runbook.md",
  "collection": "playbooks",
  "char_count": 5000,
  "chunk_count": 3,
  "status": "success"
}
```

### Search Documents

Search for documents using semantic similarity:

```bash
curl -X POST http://localhost:8000/api/v1/documents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how to troubleshoot high CPU usage",
    "collection": "documents",
    "top_k": 5
  }'
```

**Request**:
```json
{
  "query": "search query",
  "collection": "documents",  // or "playbooks", "incidents"
  "top_k": 5,
  "filters": {"category": "database"}  // optional
}
```

**Response**:
```json
{
  "query": "how to troubleshoot high CPU usage",
  "results": [
    {
      "id": "doc-uuid",
      "text": "Document text...",
      "metadata": {
        "filename": "cpu-troubleshooting.md",
        "category": "performance"
      },
      "relevance": 0.85
    }
  ],
  "total_results": 5
}
```

### List Documents

List all documents in a collection:

```bash
curl http://localhost:8000/api/v1/documents/list?collection=documents&limit=10&offset=0
```

**Response**:
```json
{
  "documents": [
    {
      "id": "doc-uuid",
      "metadata": {
        "filename": "guide.md",
        "doc_type": "general"
      }
    }
  ],
  "total": 50,
  "limit": 10,
  "offset": 0
}
```

### Get Document

Retrieve a specific document:

```bash
curl http://localhost:8000/api/v1/documents/{document_id}?collection=documents
```

### Delete Document

Delete a document:

```bash
curl -X DELETE http://localhost:8000/api/v1/documents/{document_id}?collection=documents
```

### Collection Stats

Get statistics for a collection:

```bash
curl http://localhost:8000/api/v1/documents/stats/documents
```

**Response**:
```json
{
  "collection": "documents",
  "document_count": 42,
  "status": "active"
}
```

## Using with KREA Agent

The KREA agent automatically uses the RAG pipeline during incident analysis:

1. **Alert Triggered**: AICA analyzes the alert
2. **Context Needed**: KREA receives the primary context
3. **Knowledge Retrieval**: KREA searches the vector store for relevant documents
4. **Context Enrichment**: Retrieved knowledge is added to the enhanced context
5. **Root Cause Analysis**: RCARA uses the enriched context for diagnosis

### Example Flow

```
Alert: High CPU on api-server
  ↓
AICA: Collects metrics, logs, events
  ↓
KREA: Searches knowledge base for "high CPU" related docs
  → Finds: "CPU Troubleshooting Guide"
  → Finds: "Performance Optimization Playbook"
  ↓
RCARA: Uses retrieved knowledge + evidence
  → Root Cause: Memory leak
  → Remediation: Restart + fix memory leak
```

## Populating the Knowledge Base

### 1. Upload Runbooks

```bash
# Upload a runbook
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@high-cpu-runbook.md" \
  -F "doc_type=playbook" \
  -F "category=performance"
```

### 2. Upload Documentation

```bash
# Upload SRE documentation
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@kubernetes-guide.pdf" \
  -F "doc_type=general" \
  -F "category=kubernetes"
```

### 3. Upload Incident Reports

```bash
# Upload historical incident
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@incident-2024-01-15.md" \
  -F "doc_type=incident" \
  -F "category=database"
```

### 4. Batch Upload Script

```python
import requests
from pathlib import Path

API_URL = "http://localhost:8000/api/v1/documents/upload"

def upload_directory(directory: str, doc_type: str = "general"):
    """Upload all files in a directory."""
    for file_path in Path(directory).rglob("*.md"):
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            data = {
                "doc_type": doc_type,
                "category": file_path.parent.name,
            }
            response = requests.post(API_URL, files=files, data=data)
            print(f"Uploaded {file_path.name}: {response.status_code}")

# Upload all runbooks
upload_directory("./runbooks", doc_type="playbook")

# Upload all docs
upload_directory("./docs", doc_type="general")
```

## Configuration

### Environment Variables

```bash
# Enable/disable real knowledge adapter
USE_REAL_KNOWLEDGE_ADAPTER=true

# Vector store persistence path
CHROMADB_PATH=./data/chromadb
```

### Switching Between Mock and Real Data

For testing without a populated knowledge base:

```bash
# Use mock data
USE_REAL_KNOWLEDGE_ADAPTER=false

# Use real vector store
USE_REAL_KNOWLEDGE_ADAPTER=true
```

## Best Practices

### 1. Document Organization

- Use meaningful filenames
- Set appropriate `doc_type`:
  - `general`: Technical documentation, guides
  - `playbook`: Runbooks, SOPs, procedures
  - `incident`: Post-mortems, incident reports
- Use categories for easy filtering

### 2. Document Content

- Keep documents focused and well-structured
- Use clear headings and sections
- Include context and background
- Add troubleshooting steps
- Include examples and common scenarios

### 3. Search Optimization

- Use descriptive titles and headings
- Include keywords relevant to common issues
- Structure content logically
- Break long documents into focused sections

### 4. Maintenance

- Regularly update documents
- Remove outdated information
- Consolidate duplicate content
- Review search results for relevance

## Advanced Usage

### Custom Embedding Models

To use a different embedding model, update `embeddings.py`:

```python
service = EmbeddingService(model_name="all-mpnet-base-v2")
```

Popular alternatives:
- `all-mpnet-base-v2` (768 dim, higher quality)
- `multi-qa-mpnet-base-dot-v1` (768 dim, optimized for Q&A)
- `all-MiniLM-L12-v2` (384 dim, balanced)

### Metadata Filtering

Search with metadata filters:

```python
{
  "query": "database connection",
  "filters": {
    "category": "database",
    "doc_type": "playbook"
  }
}
```

### Chunking Configuration

Adjust chunking for your use case:

```python
processor = DocumentProcessor()
chunks = processor.chunk_text(
    text,
    chunk_size=1000,  # Characters per chunk
    overlap=200       # Overlap between chunks
)
```

## Troubleshooting

### Documents Not Found in Search

1. Check if documents were uploaded successfully
2. Verify the collection name
3. Try broader search queries
4. Check `USE_REAL_KNOWLEDGE_ADAPTER` is set to `true`

### Upload Failures

1. Verify file format is supported
2. Check file size limits
3. Ensure ChromaDB directory is writable
4. Check server logs for errors

### Low Relevance Scores

1. Ensure documents contain relevant content
2. Try different embedding models
3. Adjust chunking parameters
4. Add more contextual information to documents

## Performance Considerations

### Embedding Generation

- First embedding is slow (model download)
- Subsequent embeddings are fast (cached model)
- Batch processing is more efficient

### Vector Search

- Search scales well to 100K+ documents
- Use metadata filters for large collections
- Consider collection separation for different domains

### Storage

- ChromaDB stores data on disk
- Typical storage: ~1KB per document chunk
- Regular backups recommended

## Integration with Agents

The RAG pipeline integrates seamlessly with OpsSage agents:

```python
# In KREA agent prompt
"""
Use vector_search_tool() to find relevant documentation.
Use playbook_query_tool() to find incident response procedures.
Use document_lookup_tool() to retrieve specific documents.
"""
```

Tools are automatically available to KREA during analysis.

## Monitoring

Monitor RAG pipeline health:

```bash
# Check collection stats
curl http://localhost:8000/api/v1/documents/stats/documents
curl http://localhost:8000/api/v1/documents/stats/playbooks
curl http://localhost:8000/api/v1/documents/stats/incidents

# Test search functionality
curl -X POST http://localhost:8000/api/v1/documents/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 1}'
```

## Next Steps

1. **Populate Knowledge Base**: Upload your runbooks and documentation
2. **Test Search**: Verify search results are relevant
3. **Run Analysis**: Trigger an incident analysis to see KREA use the knowledge
4. **Iterate**: Refine documents based on agent usage

For more information, see:
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Architecture Overview](ARCHITECTURE.md)
- [API Reference](http://localhost:8000/docs)

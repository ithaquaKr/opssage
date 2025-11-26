# RAG Pipeline Implementation Summary

## ✅ Implementation Complete

A complete Retrieval-Augmented Generation (RAG) pipeline has been successfully implemented in OpsSage, enabling the KREA agent to retrieve and use real knowledge from uploaded documentation.

## 🎯 What Was Implemented

### 1. Core RAG Components

#### Document Processor (`sages/rag/document_processor.py`)
- Extracts text from multiple file formats:
  - **TXT**: Plain text files
  - **MD**: Markdown (converts to plain text)
  - **PDF**: PDF documents
  - **DOCX**: Word documents
  - **JSON**: JSON data files
- Text chunking with configurable overlap
- Metadata extraction (char count, word count)

#### Embedding Service (`sages/rag/embeddings.py`)
- Uses `sentence-transformers` library
- Model: `all-MiniLM-L6-v2` (384 dimensions)
- Fast, lightweight, good for semantic search
- Lazy loading for performance
- Batch embedding support

#### Vector Store (`sages/rag/vector_store.py`)
- Built on ChromaDB (persistent vector database)
- Three collections:
  - `documents`: General SRE documentation
  - `playbooks`: Incident response procedures
  - `incidents`: Historical incident data
- Features:
  - Semantic similarity search
  - Metadata filtering
  - CRUD operations
  - Persistent storage

### 2. API Endpoints

Complete REST API in `apis/documents.py`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/documents/upload` | POST | Upload documents to knowledge base |
| `/api/v1/documents/search` | POST | Semantic search across documents |
| `/api/v1/documents/list` | GET | List all documents with pagination |
| `/api/v1/documents/{id}` | GET | Retrieve specific document |
| `/api/v1/documents/{id}` | DELETE | Delete document |
| `/api/v1/documents/stats/{collection}` | GET | Collection statistics |

### 3. Real Knowledge Adapters

Implemented `RealKnowledgeAdapter` in `sages/tools.py`:
- Replaces mock implementations
- Uses actual vector store for search
- Three query methods:
  - `vector_search()`: Semantic search
  - `document_lookup()`: Get specific document
  - `playbook_query()`: Search playbooks
- Configurable via environment variable

### 4. Integration with Agents

- **KREA Agent**: Now uses real knowledge adapters by default
- Environment-based switching:
  - `USE_REAL_KNOWLEDGE_ADAPTER=true`: Use vector store
  - `USE_REAL_KNOWLEDGE_ADAPTER=false`: Use mock data
- Seamless integration with existing agent pipeline

## 📁 New Files Created

```
sages/rag/
├── __init__.py                 # Module exports
├── embeddings.py              # Embedding service
├── document_processor.py      # Document parsing and chunking
└── vector_store.py            # ChromaDB integration

apis/
└── documents.py               # Document management API

docs/
└── RAG_GUIDE.md              # Comprehensive RAG documentation
```

## 🔧 Files Modified

- `pyproject.toml`: Added RAG dependencies
- `apis/main.py`: Included document router
- `sages/tools.py`: Added RealKnowledgeAdapter
- `env.example`: Added RAG configuration
- `.gitignore`: Excluded vector store data
- `README.md`: Added RAG documentation

## 🚀 Usage Examples

### Upload a Document

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@kubernetes-troubleshooting.md" \
  -F "doc_type=playbook" \
  -F "category=kubernetes" \
  -F "description=K8s troubleshooting guide"
```

### Search Documents

```bash
curl -X POST http://localhost:8000/api/v1/documents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how to fix high CPU usage",
    "collection": "playbooks",
    "top_k": 5
  }'
```

### Python API Client

```python
import requests

# Upload document
with open("runbook.md", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/documents/upload",
        files={"file": ("runbook.md", f)},
        data={"doc_type": "playbook", "category": "database"}
    )
    doc_id = response.json()["document_id"]

# Search documents
response = requests.post(
    "http://localhost:8000/api/v1/documents/search",
    json={
        "query": "database connection timeout",
        "collection": "playbooks",
        "top_k": 3
    }
)
results = response.json()["results"]
```

## 🔄 Agent Integration Flow

```
1. Alert Triggered
   ↓
2. AICA: Analyzes alert, collects evidence
   ↓
3. KREA: Searches knowledge base
   - vector_search_tool("high CPU usage")
   - playbook_query_tool("performance, optimization")
   ↓
4. KREA: Enriches context with retrieved knowledge
   ↓
5. RCARA: Uses enriched context for diagnosis
   ↓
6. Returns: Root cause + remediation from knowledge base
```

## 📊 Dependencies Added

```toml
dependencies = [
    ...
    "chromadb>=0.4.22",              # Vector database
    "sentence-transformers>=2.3.1",  # Embeddings
    "python-multipart>=0.0.6",       # File uploads
    "pypdf>=3.17.4",                 # PDF processing
    "python-docx>=1.1.0",            # DOCX processing
    "markdown>=3.5.1",               # Markdown processing
]
```

## ⚙️ Configuration

### Environment Variables

```bash
# Enable real knowledge adapter (default: true)
USE_REAL_KNOWLEDGE_ADAPTER=true

# Vector store persistence path (default: ./data/chromadb)
CHROMADB_PATH=./data/chromadb
```

### Switching Modes

```bash
# For production (with uploaded documents)
USE_REAL_KNOWLEDGE_ADAPTER=true

# For testing (without documents)
USE_REAL_KNOWLEDGE_ADAPTER=false
```

## 🎯 Benefits

### 1. Real Knowledge Retrieval
- Agents now access actual documentation
- No more mock data placeholders
- Contextually relevant information

### 2. Flexible Content Management
- Upload any documentation format
- Organize by type and category
- Easy to update and maintain

### 3. Semantic Search
- Natural language queries
- Finds relevant info even with different wording
- Ranked by relevance

### 4. Scalable Architecture
- ChromaDB handles large document collections
- Efficient vector similarity search
- Persistent storage

### 5. Production Ready
- Full CRUD API
- Configurable and extensible
- Comprehensive documentation

## 📚 Documentation

- **[RAG_GUIDE.md](docs/RAG_GUIDE.md)**: Complete guide with examples
- **[API Documentation](http://localhost:8000/docs)**: Interactive API docs
- **[README.md](README.md)**: Updated with RAG section

## 🧪 Testing

### Manual Testing

1. Start the server:
```bash
make run
```

2. Upload a test document:
```bash
echo "# CPU Troubleshooting\nHigh CPU can be caused by memory leaks." > test.md
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@test.md" \
  -F "doc_type=playbook"
```

3. Search for it:
```bash
curl -X POST http://localhost:8000/api/v1/documents/search \
  -H "Content-Type: application/json" \
  -d '{"query": "CPU problems", "top_k": 1}'
```

### Integration Testing

Test with a real alert:
```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alert_name": "HighCPUUsage",
    "severity": "critical",
    "message": "CPU usage above 90%",
    "labels": {"service": "api"},
    "firing_condition": "cpu > 90"
  }'
```

The KREA agent will automatically search the knowledge base for relevant information.

## 🚀 Next Steps

### 1. Populate Knowledge Base

Upload your organization's:
- Runbooks and playbooks
- SRE documentation
- Post-mortem reports
- Troubleshooting guides

### 2. Optimize Search

- Upload more documents for better coverage
- Use descriptive filenames and categories
- Structure content with clear headings

### 3. Monitor Usage

- Check collection stats
- Review search results
- Iterate on document content

### 4. Advanced Features (Future)

- Multi-language support
- Image and diagram extraction
- Auto-tagging and categorization
- Knowledge graph integration
- Automatic document updates

## 🎉 Summary

The RAG pipeline is fully implemented and integrated with OpsSage:

✅ Document processing for multiple formats
✅ Vector embeddings with sentence-transformers
✅ ChromaDB vector store with persistence
✅ Complete REST API for document management
✅ Real knowledge adapters for agents
✅ Seamless KREA agent integration
✅ Environment-based configuration
✅ Comprehensive documentation

**The system is ready to use!** Start uploading your documentation and the agents will automatically leverage it during incident analysis.

For detailed usage instructions, see [RAG_GUIDE.md](docs/RAG_GUIDE.md).

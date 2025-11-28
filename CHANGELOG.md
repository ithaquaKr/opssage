# Changelog

All notable changes and implementations to this project are documented here.

---

## [v0.4.0] - Docker & Kubernetes Deployment

### Added

**Complete containerization and orchestration support**

- **Docker Compose Stack**
  - Multi-service orchestration (Backend, Dashboard, ChromaDB, Prometheus, Grafana)
  - Development environment with hot-reload
  - Mock services for testing without real infrastructure
  - Persistent volumes for data
  - Health checks for all services

- **Kubernetes Manifests**
  - Complete K8s deployment configurations
  - Helm charts for production deployment
  - ConfigMaps and Secrets management
  - Persistent storage with PV/PVC
  - NodePort and LoadBalancer services
  - Resource limits and requests

- **Kind (Kubernetes in Docker) Support**
  - Multi-node cluster configuration (1 control plane + 3 workers)
  - Local Kubernetes testing environment
  - Port mappings for easy access
  - Node labels for workload placement

- **Automation Scripts**
  - `dev-setup.sh` - Complete development setup
  - `kind-setup.sh` - Create Kind cluster
  - `kind-deploy.sh` - Deploy to Kind
  - `kind-teardown.sh` - Cleanup

- **Comprehensive Makefile**
  - 30+ automation targets
  - Development, Docker, and Kubernetes workflows
  - Database backup/restore
  - Status monitoring

- **Monitoring Stack**
  - Prometheus metrics collection
  - Grafana dashboards
  - Pre-configured datasources

### Documentation

- `docs/DOCKER_COMPOSE_GUIDE.md` - Complete Docker Compose guide
- `docs/KIND_GUIDE.md` - Kubernetes testing with Kind

### Files Created

- `docker-compose.yml`
- `kind-config.yaml`
- `docker/Dockerfile.backend`
- `docker/Dockerfile.dashboard`
- `docker/Dockerfile.mock-services`
- `docker/mock-services.py`
- `docker/prometheus/prometheus.yml`
- `docker/grafana/provisioning/`
- `deploy/kubernetes/*.yaml`
- `scripts/*.sh`

---

## [v0.3.0] - Web Dashboard

### Added

**Modern React-based web dashboard for OpsSage**

- **Dashboard Application**
  - React 18 with TypeScript
  - Vite for development and building
  - Tailwind CSS for styling
  - React Router for navigation

- **Pages Implemented**
  - **Dashboard**: Overview with statistics and recent incidents
  - **Alerts**: Form to submit new alerts
  - **Incidents**: List view with AG Grid table, detail view with full analysis
  - **Documents**: Upload and manage knowledge base documents
  - **Search**: Semantic search interface for documentation

- **Components**
  - Reusable UI components (Button, Card, Badge, Layout)
  - Sidebar navigation
  - Status indicators
  - Loading states

- **API Integration**
  - Complete TypeScript API client
  - Type-safe interfaces
  - All backend endpoints integrated

- **Features**
  - Real-time incident tracking
  - AG Grid for powerful data tables
  - File upload for documents (TXT, MD, PDF, DOCX, JSON)
  - Toast notifications
  - Responsive design

### Documentation

- `dashboard/README.md` - Dashboard-specific documentation
- Updated main README with dashboard usage

### Files Created

- `dashboard/` - Complete React application
  - `src/pages/` - Page components
  - `src/components/` - Reusable components
  - `src/api/client.ts` - API client
  - `src/types/` - TypeScript types
  - Configuration files (vite, tailwind, tsconfig)

---

## [v0.2.0] - RAG Pipeline

### Added

**Complete Retrieval-Augmented Generation system**

- **Document Processing**
  - Multi-format support: TXT, MD, PDF, DOCX, JSON
  - Text chunking with overlap
  - Metadata extraction

- **Vector Store**
  - ChromaDB integration
  - Three collections: documents, playbooks, incidents
  - Persistent storage
  - Semantic similarity search

- **Embedding Service**
  - sentence-transformers integration
  - Model: all-MiniLM-L6-v2 (384 dimensions)
  - Batch embedding support

- **Knowledge Adapters**
  - Real knowledge adapter using vector store
  - Mock adapter for testing
  - Environment-based switching

- **Document API**
  - Upload documents with metadata
  - Semantic search
  - CRUD operations
  - Collection statistics

- **KREA Integration**
  - Automatic knowledge retrieval during analysis
  - Relevance scoring
  - Context enrichment

### Dependencies Added

- `chromadb` - Vector database
- `sentence-transformers` - Embeddings
- `python-multipart` - File uploads
- `pypdf` - PDF processing
- `python-docx` - Word document processing
- `markdown` - Markdown processing

### Documentation

- `docs/RAG_GUIDE.md` - Comprehensive RAG documentation

### Files Created

- `sages/rag/embeddings.py`
- `sages/rag/document_processor.py`
- `sages/rag/vector_store.py`
- `apis/documents.py`

---

## [v0.1.1] - API Refactoring

### Changed

**Reorganized API code for better separation of concerns**

- Moved FastAPI application from `sages/api.py` to `apis/main.py`
- Created dedicated `apis/` package
- Maintained backward compatibility with shim in `sages/api.py`

### Fixed

- Fixed Google ADK tool imports in agents
- Changed `@tool` decorator to `@agent_tool`

### Documentation

- `docs/API_REFACTORING.md` - Refactoring details

### Files Modified

- `sages/api.py` - Now re-exports from apis.main
- `tests/test_api.py` - Updated imports
- `Makefile` - Updated run commands
- `Dockerfile` - Updated CMD
- All agent files - Fixed tool imports

### Files Created

- `apis/__init__.py`
- `apis/main.py`
- `scripts/verify_refactoring.py`

---

## [v0.1.0] - Initial Release

### Added

**Core multi-agent system implementation**

- **Three Specialized Agents**
  - **AICA** (Alert Ingestion & Context Agent)
    - Alert analysis and context building
    - Evidence collection from metrics, logs, events
    - Primary context package generation

  - **KREA** (Knowledge Retrieval & Enrichment Agent)
    - Knowledge retrieval and relevance scoring
    - Context enrichment
    - Enhanced context package generation

  - **RCARA** (Root Cause Analysis & Remediation Agent)
    - Root cause analysis
    - Remediation recommendations
    - Diagnostic report generation

- **Core Components**
  - `sages/models.py` - Pydantic models for all message contracts
  - `sages/tools.py` - Capability adapters (metrics, logs, events, knowledge)
  - `sages/context_store.py` - Thread-safe shared context storage
  - `sages/orchestrator.py` - Agent pipeline orchestration
  - `sages/configs.py` - Configuration management

- **API Server**
  - FastAPI application
  - Alert ingestion endpoint
  - Incident management endpoints
  - Health checks and readiness probes
  - Swagger/ReDoc documentation

- **Testing**
  - Unit tests for models
  - Integration tests for agents
  - API tests
  - Mock adapters for testing

- **Deployment**
  - Dockerfile for containerization
  - Kubernetes manifests
  - Helm charts
  - Environment configuration

- **Documentation**
  - README with overview and quick start
  - Architecture documentation
  - Developer guide
  - API documentation

### Technology Stack

- Python 3.13
- Google ADK (Agent Development Kit)
- Google Gemini (via Vertex AI)
- FastAPI
- Pydantic v2
- pytest

### Files Created

- `sages/subagents/aica.py`
- `sages/subagents/krea.py`
- `sages/subagents/rcara.py`
- `sages/models.py`
- `sages/tools.py`
- `sages/context_store.py`
- `sages/orchestrator.py`
- `sages/configs.py`
- `sages/api.py`
- `tests/` - Complete test suite
- `deploy/helm/` - Helm charts
- `docs/` - Documentation
- `pyproject.toml` - Project configuration
- `Dockerfile`
- `Makefile`

---

## Development Workflow

### Version Numbering

- **Major** (x.0.0): Breaking changes or major new features
- **Minor** (0.x.0): New features, backward compatible
- **Patch** (0.0.x): Bug fixes

### Recent Milestones

- ✅ v0.1.0 - Core multi-agent system
- ✅ v0.1.1 - API refactoring
- ✅ v0.2.0 - RAG pipeline
- ✅ v0.3.0 - Web dashboard
- ✅ v0.4.0 - Docker & Kubernetes

### Upcoming

- 🔄 v0.5.0 - Advanced monitoring and observability
- 🔄 v0.6.0 - Auto-remediation capabilities
- 🔄 v1.0.0 - Production-ready release

---

## Migration Notes

### Upgrading from v0.3.x to v0.4.x

**Docker Compose:**
```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d
```

**Kubernetes:**
```bash
# Update Helm chart
helm upgrade opssage ./deploy/helm
```

### Upgrading from v0.2.x to v0.3.x

**No breaking changes**

New web dashboard available:
```bash
cd dashboard
npm install
npm run dev
```

### Upgrading from v0.1.x to v0.2.x

**Environment variables added:**
```bash
CHROMADB_PATH=./data/chromadb
USE_REAL_KNOWLEDGE_ADAPTER=true
```

**New dependencies:**
```bash
uv sync
```

### Upgrading from v0.1.0 to v0.1.1

**Import changes:**
```python
# Old (still works)
from sages.api import app

# New (recommended)
from apis.main import app
```

**Tool decorator changes in agents:**
```python
# Old
from google.adk import tool

@tool
def my_tool():
    pass

# New
from google.adk import agent_tool

@agent_tool
def my_tool():
    pass
```

---

## Contributors

- Core system design and implementation
- Multi-agent architecture
- RAG pipeline
- Web dashboard
- DevOps and deployment

---

## Links

- **Repository**: https://github.com/ithaquaKr/opssage
- **Issues**: https://github.com/ithaquaKr/opssage/issues
- **Documentation**: https://github.com/ithaquaKr/opssage/docs

---

**Last Updated**: 2024

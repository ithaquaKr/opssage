# Knowledge Base Guide

OpsSage learns from your documentation to provide better incident analysis and remediation recommendations. This guide explains how to build and maintain your knowledge base.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Adding Documents](#adding-documents)
4. [Searching](#searching)
5. [Best Practices](#best-practices)
6. [How It Works](#how-it-works)

---

## Overview

### What is the Knowledge Base?

The knowledge base is your organization's collected wisdom:
- **Runbooks** - Step-by-step procedures
- **Playbooks** - Incident response guides
- **Documentation** - Architecture docs, troubleshooting guides
- **Post-mortems** - Past incident reports

### How OpsSage Uses It

When analyzing an alert, the KREA agent automatically:
1. Searches for relevant documentation
2. Finds similar past incidents
3. Retrieves applicable runbooks
4. Enriches the analysis with this knowledge

**Result:** Better root cause analysis and more accurate remediation recommendations.

---

## Quick Start

### Upload Your First Document

#### Using Dashboard

1. Go to http://localhost:3000
2. Click **"Documents"** in sidebar
3. Click **"Upload"** button
4. Select a file (TXT, MD, PDF, DOCX, or JSON)
5. Choose document type: `playbook`
6. Click **"Upload"**

#### Using API

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@kubernetes-runbook.md" \
  -F "doc_type=playbook" \
  -F "category=kubernetes"
```

#### Using Python

```python
import requests

with open("database-playbook.md", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/documents/upload",
        files={"file": f},
        data={
            "doc_type": "playbook",
            "category": "database"
        }
    )

print(f"Uploaded: {response.json()['document_id']}")
```

### Test the Knowledge Base

Search for content:

```bash
curl -X POST http://localhost:8000/api/v1/documents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how to handle high CPU",
    "collection": "playbooks",
    "top_k": 3
  }'
```

---

## Adding Documents

### Supported Formats

| Format | Extension | Use For |
|--------|-----------|---------|
| **Text** | `.txt` | Simple notes, logs |
| **Markdown** | `.md` | Documentation, runbooks |
| **PDF** | `.pdf` | Reports, presentations |
| **Word** | `.docx` | Official documents |
| **JSON** | `.json` | Structured data, configs |

### Document Types

Choose the right type for your content:

#### `playbook`
Incident response procedures and runbooks.

**Examples:**
- How to handle database outages
- Steps to debug high CPU usage
- Pod crash loop troubleshooting
- Network connectivity issues

#### `document`
General documentation and guides.

**Examples:**
- Architecture diagrams
- System documentation
- Troubleshooting guides
- Best practices

#### `incident`
Past incident reports and post-mortems.

**Examples:**
- Post-mortem reports
- Incident timelines
- Root cause analyses
- Lessons learned

### Categories

Organize documents with categories:

```
kubernetes        - K8s-related content
database          - Database issues
networking        - Network problems
security          - Security incidents
performance       - Performance optimization
storage           - Storage issues
application       - Application errors
infrastructure    - Infra management
```

### Metadata

Add optional metadata for better organization:

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@runbook.md" \
  -F "doc_type=playbook" \
  -F "category=kubernetes" \
  -F "description=Complete K8s troubleshooting guide"
```

---

## Searching

### Semantic Search

OpsSage uses semantic search - you can use natural language:

**Good queries:**
- ✅ "pod keeps crashing"
- ✅ "database connection timeout"
- ✅ "high memory usage troubleshooting"
- ✅ "how to scale deployment"

**Not necessary:**
- ❌ Exact phrases
- ❌ Boolean operators
- ❌ Keywords only

### Search via Dashboard

1. Click **"Search"** in sidebar
2. Enter your question in plain language
3. Select collection (Documents, Playbooks, or Incidents)
4. View ranked results with relevance scores

### Search via API

```bash
curl -X POST http://localhost:8000/api/v1/documents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how to debug memory leak",
    "collection": "playbooks",
    "top_k": 5
  }'
```

**Response:**
```json
{
  "results": [
    {
      "document_id": "doc-abc123",
      "content": "Memory leak troubleshooting steps: 1. Check heap...",
      "metadata": {
        "category": "performance",
        "doc_type": "playbook"
      },
      "score": 0.89
    }
  ]
}
```

### Understanding Scores

Relevance scores range from 0 to 1:
- **0.8 - 1.0**: Highly relevant
- **0.6 - 0.8**: Relevant
- **0.4 - 0.6**: Somewhat relevant
- **< 0.4**: Likely not relevant

---

## Best Practices

### Content Organization

#### 1. Structure Your Documents

**Good structure:**
```markdown
# Database Connection Timeout

## Problem
Database queries timing out after 30 seconds

## Symptoms
- Application errors showing connection timeout
- Database logs show idle connections
- Connection pool exhausted

## Diagnosis Steps
1. Check connection pool settings
2. Review database logs
3. Examine slow queries

## Solutions
### Immediate
- Restart connection pool
- Increase timeout temporarily

### Long-term
- Optimize queries
- Adjust pool size
- Add connection monitoring
```

**Why:** Clear sections make it easy to extract relevant information.

#### 2. Use Descriptive Titles

**Good:**
- ✅ "Kubernetes Pod Crash Loop Troubleshooting"
- ✅ "PostgreSQL Connection Pool Tuning Guide"
- ✅ "High CPU Usage Investigation Runbook"

**Poor:**
- ❌ "Runbook 1"
- ❌ "Notes"
- ❌ "Fix"

#### 3. Include Examples

Always include:
- Command examples
- Log samples
- Error messages
- Configuration snippets

```markdown
## Check pod status

Command:
```bash
kubectl get pod api-server-xyz -o yaml
```

Expected output:
```
status:
  phase: Running
```
```

### Content Quality

#### What to Include

**Essential information:**
- Problem description
- Symptoms and signs
- Diagnostic steps
- Solutions (immediate and long-term)
- Examples and commands
- Related issues

**Context:**
- When does this happen?
- What services are affected?
- Impact level
- Prerequisites

#### What to Avoid

- ❌ Outdated information
- ❌ Incomplete procedures
- ❌ Vague instructions
- ❌ Missing context
- ❌ Dead links
- ❌ Undocumented commands

### Maintenance

#### Regular Updates

**Weekly:**
- Add new incident learnings
- Update runbooks used recently
- Review recent search queries

**Monthly:**
- Audit document relevance
- Remove outdated content
- Consolidate duplicate information
- Update categories

**After Each Incident:**
1. Document what happened
2. Update related runbooks
3. Add to post-mortem collection

#### Batch Upload

Upload multiple documents:

```bash
#!/bin/bash
for file in runbooks/*.md; do
  curl -X POST http://localhost:8000/api/v1/documents/upload \
    -F "file=@$file" \
    -F "doc_type=playbook" \
    -F "category=kubernetes"
  echo "Uploaded: $file"
done
```

---

## How It Works

### The RAG Pipeline

**RAG** = Retrieval-Augmented Generation

```
Document → Split into chunks → Generate embeddings → Store in vector DB

When searching:
Query → Generate embedding → Find similar chunks → Return results
```

### Technical Details

**Embedding Model:** `all-MiniLM-L6-v2`
- Dimensions: 384
- Fast and lightweight
- Good semantic understanding

**Vector Database:** ChromaDB
- Persistent storage
- Efficient similarity search
- Three collections: documents, playbooks, incidents

**Chunking:**
- Chunk size: 500 tokens
- Overlap: 50 tokens
- Preserves context across chunks

### Collections

| Collection | Contains | Auto-Used By |
|------------|----------|--------------|
| `documents` | General docs | KREA agent |
| `playbooks` | Runbooks, procedures | KREA agent |
| `incidents` | Past incidents | KREA agent |

### Integration with Agents

```
Alert Received
    ↓
AICA: Analyzes alert, collects evidence
    ↓
KREA: Searches knowledge base
    - vector_search("high CPU usage")
    - playbook_query("performance, troubleshooting")
    - Retrieves relevant content
    ↓
KREA: Enriches context with findings
    ↓
RCARA: Uses enriched context for analysis
    ↓
Better diagnosis + recommendations
```

---

## Management

### View Statistics

```bash
# Get collection stats
curl http://localhost:8000/api/v1/documents/stats/playbooks
```

**Response:**
```json
{
  "collection": "playbooks",
  "document_count": 42,
  "total_chunks": 387
}
```

### List Documents

```bash
# List all in collection
curl "http://localhost:8000/api/v1/documents/list?collection=playbooks"

# With pagination
curl "http://localhost:8000/api/v1/documents/list?collection=playbooks&limit=10&offset=0"
```

### Delete Documents

```bash
# Delete by ID
curl -X DELETE http://localhost:8000/api/v1/documents/{document_id}
```

### Backup

```bash
# Backup ChromaDB data
tar -czf chromadb-backup.tar.gz data/chromadb/

# Restore
tar -xzf chromadb-backup.tar.gz
```

---

## Examples

### Example Playbook

Create `high-cpu-playbook.md`:

```markdown
# High CPU Usage Playbook

## Alert Trigger
CPU usage > 90% for 5 minutes

## Immediate Actions

### 1. Identify Process
```bash
kubectl top pods -n production
kubectl exec -it <pod> -- top
```

### 2. Check for Known Issues
- Memory leak causing thrashing
- Runaway goroutines
- Inefficient queries

### 3. Quick Mitigation
```bash
# Scale up
kubectl scale deployment api-server --replicas=5

# Or restart
kubectl rollout restart deployment api-server
```

## Investigation

### Check Logs
```bash
kubectl logs <pod> --tail=100 | grep ERROR
```

### Check Metrics
- CPU usage trend
- Memory usage
- Request rate
- Database query time

## Root Causes

### Common Causes
1. Memory leak → GC thrashing
2. Too many requests → Need scaling
3. Slow queries → Database optimization needed
4. Infinite loop → Code bug

## Long-Term Solutions

### Memory Leak
1. Enable profiling
2. Identify leak source
3. Fix code
4. Add memory monitoring

### High Load
1. Implement autoscaling
2. Add caching
3. Optimize hot paths

## Prevention
- Set up autoscaling
- Add memory alerts
- Regular performance testing
- Code review for efficiency
```

Upload it:

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@high-cpu-playbook.md" \
  -F "doc_type=playbook" \
  -F "category=performance" \
  -F "description=Runbook for high CPU incidents"
```

Now when a high CPU alert comes in, KREA will find this playbook and use it to enrich the analysis.

---

## Troubleshooting

### No Search Results

**Problem:** Search returns empty results

**Solutions:**
1. Verify documents were uploaded:
   ```bash
   curl http://localhost:8000/api/v1/documents/list
   ```

2. Check ChromaDB is running:
   ```bash
   curl http://localhost:8001/api/v1/heartbeat
   ```

3. Try broader query terms

### Low Relevance Scores

**Problem:** Search results have low scores (< 0.5)

**Solutions:**
1. Upload more relevant documentation
2. Use more specific queries
3. Check document content quality
4. Ensure documents have clear structure

### Upload Failures

**Problem:** Document upload fails

**Solutions:**
1. Check file format is supported
2. Verify file is not corrupted
3. Check file size (< 10MB recommended)
4. Ensure backend is running

---

## Next Steps

- **[USER_GUIDE.md](../USER_GUIDE.md)** - Learn to use all features
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Understand the system design
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation

---

**Start building your knowledge base today!** 📚

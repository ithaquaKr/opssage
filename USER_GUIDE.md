# OpsSage User Guide

This guide explains how to use OpsSage for incident analysis and remediation. Whether you're using the web dashboard or the API, you'll find everything you need here.

---

## Table of Contents

1. [Overview](#overview)
2. [Web Dashboard](#web-dashboard)
3. [Managing Alerts](#managing-alerts)
4. [Working with Incidents](#working-with-incidents)
5. [Knowledge Base](#knowledge-base)
6. [API Usage](#api-usage)
7. [Integration Examples](#integration-examples)
8. [Best Practices](#best-practices)

---

## Overview

### What OpsSage Does

OpsSage automatically:

1. **Receives alerts** from your monitoring system
2. **Investigates** by querying logs, metrics, and events
3. **Searches** your documentation for similar issues
4. **Analyzes** the root cause using AI reasoning
5. **Recommends** both immediate fixes and long-term solutions

### The Three-Agent System

```
Alert → AICA → KREA → RCARA → Solution
```

- **AICA** collects evidence (logs, metrics, events)
- **KREA** finds relevant knowledge (runbooks, playbooks)
- **RCARA** determines root cause and suggests fixes

You don't interact with agents directly - just submit alerts and review results.

---

## Web Dashboard

The dashboard is the easiest way to use OpsSage.

### Accessing the Dashboard

```bash
cd dashboard
npm run dev
```

Visit: http://localhost:3000

### Dashboard Overview

#### Home Page

Shows at-a-glance statistics:
- Total incidents
- Active incidents
- Documents in knowledge base
- Playbooks available

Plus recent incidents with quick access.

#### Navigation

- **Dashboard** - Statistics and recent activity
- **Alerts** - Submit new alerts
- **Incidents** - View all incidents and analysis
- **Documents** - Manage knowledge base
- **Search** - Query your documentation

---

## Managing Alerts

### Submitting Alerts via Dashboard

1. **Click "Alerts"** in sidebar

2. **Fill in alert details:**
   - **Alert Name**: Short identifier (e.g., "HighCPUUsage")
   - **Severity**: critical, warning, or info
   - **Message**: Description of what's happening
   - **Firing Condition**: The threshold that was breached

3. **Add labels** (optional but recommended):
   - service: Which service is affected
   - namespace: Kubernetes namespace
   - pod: Specific pod name
   - node: Node name

4. **Click "Submit Alert"**

5. **View results** - Auto-redirects to incident detail page

### Example Alert Submission

**Alert Name:** `PodCrashLoop`
**Severity:** `critical`
**Message:** `Pod api-server-xyz is crash looping`
**Labels:**
- service: `api-server`
- namespace: `production`
- pod: `api-server-xyz`

**Firing Condition:** `pod_restart_count > 5`

### Submitting Alerts via API

```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alert_name": "PodCrashLoop",
    "severity": "critical",
    "message": "Pod api-server-xyz is crash looping",
    "labels": {
      "service": "api-server",
      "namespace": "production",
      "pod": "api-server-xyz"
    },
    "firing_condition": "pod_restart_count > 5"
  }'
```

---

## Working with Incidents

### Viewing Incidents

#### In Dashboard

1. **Click "Incidents"** in sidebar
2. **Browse the table** with sortable columns:
   - Incident ID
   - Alert Name
   - Severity
   - Status
   - Created Time

3. **Filter by status:**
   - All
   - Pending
   - Analyzing
   - Completed
   - Failed

4. **Click a row** to view full details

#### Via API

```bash
# List all incidents
curl http://localhost:8000/api/v1/incidents

# Filter by status
curl http://localhost:8000/api/v1/incidents?status=completed

# Get specific incident
curl http://localhost:8000/api/v1/incidents/{incident_id}
```

### Understanding the Analysis

Each incident includes:

#### 1. Alert Details
- Original alert name, severity, message
- Labels and metadata
- When it was triggered

#### 2. Evidence Collected
- **Metrics**: Time-series data (CPU, memory, etc.)
- **Logs**: Relevant log entries
- **Events**: Kubernetes events or system events

#### 3. Root Cause Analysis
- **Root Cause**: The determined underlying issue
- **Confidence Score**: How confident the analysis is (0-1)
- **Reasoning Steps**: How the conclusion was reached
- **Supporting Evidence**: Specific data points used

#### 4. Remediation Recommendations

**Short-Term Actions** (immediate fixes):
- Restart affected services
- Scale resources
- Apply quick patches

**Long-Term Actions** (prevent recurrence):
- Code fixes
- Architecture changes
- Process improvements

### Deleting Incidents

#### In Dashboard

1. Open incident detail page
2. Click "Delete Incident" button
3. Confirm deletion

#### Via API

```bash
curl -X DELETE http://localhost:8000/api/v1/incidents/{incident_id}
```

---

## Knowledge Base

The knowledge base is how OpsSage learns from your documentation.

### Uploading Documents

#### Via Dashboard

1. **Click "Documents"** in sidebar
2. **Click "Upload"** button
3. **Select file** (TXT, MD, PDF, DOCX, JSON)
4. **Fill in metadata:**
   - **Document Type**: document, playbook, or incident
   - **Category**: (optional) e.g., kubernetes, database, networking
   - **Description**: (optional) brief summary

5. **Click "Upload"**

#### Via API

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@kubernetes-troubleshooting.md" \
  -F "doc_type=playbook" \
  -F "category=kubernetes" \
  -F "description=K8s troubleshooting guide"
```

#### Via Python

```python
import requests

with open("runbook.md", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/documents/upload",
        files={"file": ("runbook.md", f)},
        data={
            "doc_type": "playbook",
            "category": "database",
            "description": "Database incident playbook"
        }
    )

print(f"Uploaded: {response.json()['document_id']}")
```

### Document Types

- **document**: General documentation, guides, wikis
- **playbook**: Incident response procedures, runbooks
- **incident**: Past incident reports, post-mortems

### Organizing Documents

Use **categories** to organize:
- `kubernetes` - K8s-related docs
- `database` - Database troubleshooting
- `networking` - Network issues
- `security` - Security incidents
- `performance` - Performance optimization

### Searching Documents

#### Via Dashboard

1. **Click "Search"** in sidebar
2. **Enter query** (natural language)
   - Example: "how to fix high CPU usage"
3. **Select collection** (Documents, Playbooks, or Incidents)
4. **View results** ranked by relevance

#### Via API

```bash
curl -X POST http://localhost:8000/api/v1/documents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "pod crash loop troubleshooting",
    "collection": "playbooks",
    "top_k": 5
  }'
```

**Response:**
```json
{
  "results": [
    {
      "document_id": "doc-123",
      "content": "When a pod is crash looping...",
      "metadata": {
        "category": "kubernetes",
        "doc_type": "playbook"
      },
      "score": 0.92
    }
  ]
}
```

### Managing Documents

#### Listing Documents

```bash
# List all documents
curl http://localhost:8000/api/v1/documents/list?collection=playbooks

# With pagination
curl http://localhost:8000/api/v1/documents/list?collection=playbooks&limit=10&offset=0
```

#### Viewing a Document

```bash
curl http://localhost:8000/api/v1/documents/{document_id}
```

#### Deleting Documents

```bash
curl -X DELETE http://localhost:8000/api/v1/documents/{document_id}
```

#### Collection Statistics

```bash
# Get stats for a collection
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

---

## API Usage

### Authentication

Currently, OpsSage doesn't require authentication for local development.

For production deployment, configure authentication in your Kubernetes Ingress or API Gateway.

### Base URL

```
http://localhost:8000
```

### Common Headers

```
Content-Type: application/json
```

### Response Format

All responses are JSON:

**Success:**
```json
{
  "status": "success",
  "data": { ... }
}
```

**Error:**
```json
{
  "detail": "Error message here"
}
```

### API Endpoints Reference

#### Health & Status

```bash
# Simple health check
GET /

# Detailed health status
GET /api/v1/health

# Readiness probe (for K8s)
GET /api/v1/readiness
```

#### Alerts

```bash
# Submit an alert
POST /api/v1/alerts
```

#### Incidents

```bash
# List incidents
GET /api/v1/incidents
GET /api/v1/incidents?status=completed

# Get incident
GET /api/v1/incidents/{id}

# Delete incident
DELETE /api/v1/incidents/{id}
```

#### Documents

```bash
# Upload document
POST /api/v1/documents/upload

# Search documents
POST /api/v1/documents/search

# List documents
GET /api/v1/documents/list

# Get document
GET /api/v1/documents/{id}

# Delete document
DELETE /api/v1/documents/{id}

# Collection stats
GET /api/v1/documents/stats/{collection}
```

### Interactive API Documentation

Visit http://localhost:8000/docs for Swagger UI with:
- All endpoints documented
- Request/response schemas
- "Try it out" functionality

---

## Integration Examples

### Prometheus AlertManager

Configure AlertManager to send alerts to OpsSage:

```yaml
# alertmanager.yml
receivers:
  - name: 'opssage'
    webhook_configs:
      - url: 'http://opssage:8000/api/v1/alerts'
        send_resolved: false
```

### Python Script

Automated monitoring script:

```python
import requests
import time

def monitor_service(service_name):
    # Check service health
    health = check_service_health(service_name)

    if not health['ok']:
        # Submit alert to OpsSage
        alert = {
            "alert_name": f"{service_name}Down",
            "severity": "critical",
            "message": f"{service_name} is not responding",
            "labels": {
                "service": service_name
            },
            "firing_condition": "health_check_failed"
        }

        response = requests.post(
            "http://opssage:8000/api/v1/alerts",
            json=alert
        )

        incident_id = response.json()['incident_id']
        print(f"Created incident: {incident_id}")

        # Get remediation recommendations
        incident = requests.get(
            f"http://opssage:8000/api/v1/incidents/{incident_id}"
        ).json()

        print("Recommendations:")
        for action in incident['diagnostic_report']['recommended_remediation']['short_term_actions']:
            print(f"  - {action}")

# Run every 60 seconds
while True:
    monitor_service("api-server")
    time.sleep(60)
```

### Kubernetes Operator

Custom Kubernetes controller:

```python
from kubernetes import client, watch
import requests

def watch_pods():
    v1 = client.CoreV1Api()
    w = watch.Watch()

    for event in w.stream(v1.list_pod_for_all_namespaces):
        pod = event['object']

        # Check for crash loop
        if pod.status.container_statuses:
            for container in pod.status.container_statuses:
                if container.restart_count > 5:
                    # Alert OpsSage
                    alert = {
                        "alert_name": "PodCrashLoop",
                        "severity": "critical",
                        "message": f"Pod {pod.metadata.name} is crash looping",
                        "labels": {
                            "pod": pod.metadata.name,
                            "namespace": pod.metadata.namespace
                        },
                        "firing_condition": f"restart_count > 5"
                    }

                    requests.post(
                        "http://opssage:8000/api/v1/alerts",
                        json=alert
                    )
```

---

## Best Practices

### 1. Alert Quality

**Good alerts include:**
- ✅ Clear, descriptive names
- ✅ Accurate severity levels
- ✅ Detailed messages
- ✅ Relevant labels (service, namespace, pod)
- ✅ Specific firing conditions

**Poor alerts:**
- ❌ Vague names like "Error" or "Problem"
- ❌ Always "critical" severity
- ❌ No context or labels
- ❌ Generic messages

### 2. Knowledge Base Management

**Upload:**
- Runbooks for common incidents
- Post-mortem reports
- Troubleshooting guides
- Architecture documentation
- Deployment procedures

**Organize:**
- Use consistent categories
- Add meaningful descriptions
- Keep documents up-to-date
- Remove outdated information

**Format:**
- Use clear headings
- Include step-by-step procedures
- Add examples and commands
- Link to related docs

### 3. Incident Review

After each incident:

1. **Review the analysis** - Was it accurate?
2. **Check recommendations** - Were they helpful?
3. **Update documentation** - Add new learnings
4. **Improve alerts** - Make them more specific

### 4. Integration

- **Start small** - Test with one service
- **Monitor results** - Track accuracy over time
- **Iterate** - Refine alerts and documentation
- **Expand gradually** - Add more services

### 5. Security

- **Protect credentials** - Never commit Google Cloud keys
- **Use service accounts** - With minimal required permissions
- **Enable authentication** - In production deployments
- **Audit logs** - Monitor API access

---

## Tips & Tricks

### Getting Better Results

**More context = better analysis:**
```json
{
  "alert_name": "HighCPU",
  "severity": "warning",
  "message": "CPU at 95% for 10 minutes on api-server-xyz",
  "labels": {
    "service": "api-server",
    "namespace": "production",
    "pod": "api-server-xyz",
    "node": "node-1",
    "deployment": "api-server",
    "cluster": "prod-us-east"
  }
}
```

### Bulk Operations

Upload multiple documents:

```bash
for file in docs/*.md; do
  curl -X POST http://localhost:8000/api/v1/documents/upload \
    -F "file=@$file" \
    -F "doc_type=playbook"
done
```

### Monitoring OpsSage

Check system health:

```bash
# Health endpoint
curl http://localhost:8000/api/v1/health

# Prometheus metrics (if enabled)
curl http://localhost:8000/metrics

# Document count
curl http://localhost:8000/api/v1/documents/stats/playbooks
```

---

## Common Workflows

### Daily Operations

```bash
# Morning: Check overnight incidents
curl http://localhost:8000/api/v1/incidents?status=completed

# Review any critical incidents
curl http://localhost:8000/api/v1/incidents/{id}

# Update knowledge base as needed
```

### Incident Response

1. Alert fires (automatic or manual)
2. OpsSage analyzes (seconds)
3. Review recommendations (dashboard or API)
4. Implement short-term fixes
5. Plan long-term solutions
6. Update documentation with learnings

### Knowledge Base Maintenance

**Weekly:**
- Review new incidents
- Update outdated playbooks
- Add new documentation

**Monthly:**
- Audit document relevance
- Remove obsolete information
- Organize categories

---

## Next Steps

Now that you know how to use OpsSage:

1. **[Deploy to Production](docs/DEPLOYMENT.md)** - Run in your environment
2. **[Architecture Guide](docs/ARCHITECTURE.md)** - Understand how it works
3. **[Development Guide](docs/DEVELOPMENT.md)** - Extend and customize
4. **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation

---

## Getting Help

- **Documentation**: Check docs/ directory
- **API Docs**: http://localhost:8000/docs
- **GitHub Issues**: https://github.com/ithaquaKr/opssage/issues
- **Logs**: Check application logs for errors

---

**Happy Incident Hunting! 🔍**

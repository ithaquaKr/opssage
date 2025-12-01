# Database Persistence

OpsSage now features full database persistence for incident data, ensuring all incident analysis results are stored durably and can survive container restarts.

## Overview

All incident data is now persisted to a PostgreSQL database (or SQLite for local development), providing:

- **Durability**: Incident data survives container restarts and system failures
- **Query Performance**: Indexed fields for fast lookups by alert name, severity, namespace, service
- **Complete History**: Full storage of alert input, analysis contexts, and diagnostic reports
- **Scalability**: Production-ready PostgreSQL with connection pooling

## Architecture

### Database Components

```
sages/db/
├── __init__.py          # Module exports
├── models.py            # SQLAlchemy ORM models
└── database.py          # Session management and initialization
```

### Database Schema

**Table: `incidents`**

| Column | Type | Description |
|--------|------|-------------|
| `incident_id` | UUID (PK) | Unique incident identifier |
| `status` | String (indexed) | Current status: pending, context_collected, context_enriched, completed, failed |
| `created_at` | Timestamptz | When the incident was created |
| `updated_at` | Timestamptz | Last update timestamp |
| `alert_input` | JSON | Original alert data |
| `primary_context` | JSON | AICA agent output (evidence, observations, hypotheses) |
| `enhanced_context` | JSON | KREA agent output (knowledge enrichment) |
| `diagnostic_report` | JSON | RCARA agent output (root cause analysis, remediation) |
| `alert_name` | String (indexed) | Denormalized for fast filtering |
| `severity` | String (indexed) | Denormalized for fast filtering |
| `namespace` | String (indexed) | Kubernetes namespace |
| `service` | String (indexed) | Service name |
| `root_cause` | Text | Extracted root cause for quick access |
| `confidence_score` | Float | Confidence score (0.0 - 1.0) |

### Indexes

- Primary key on `incident_id`
- Index on `status` for filtering
- Index on `created_at` for sorting
- Index on `alert_name`, `severity`, `namespace`, `service` for fast lookups

## Configuration

### Docker Compose (Production)

The PostgreSQL service is automatically configured in `docker-compose.yml`:

```yaml
postgres:
  image: postgres:16-alpine
  container_name: opssage-postgres
  ports:
    - "5432:5432"
  environment:
    - POSTGRES_USER=opssage
    - POSTGRES_PASSWORD=opssage_dev
    - POSTGRES_DB=opssage
  volumes:
    - postgres-data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U opssage"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### Configuration File

Add to `config.yaml`:

```yaml
database:
  url: ${DATABASE_URL}  # Set via environment variable
  echo: false  # Set to true for SQL query logging
```

### Environment Variables

**For Docker Compose:**
```bash
# Already configured in docker-compose.yml
DATABASE_URL=postgresql://opssage:opssage_dev@postgres:5432/opssage
```

**For Local Development (SQLite):**
```bash
# Leave DATABASE_URL unset, defaults to SQLite
# Or explicitly set:
DATABASE_URL=sqlite:///./data/opssage.db
```

**For Production:**
```bash
export DATABASE_URL=postgresql://user:password@hostname:5432/database
```

## Usage

### Starting the System

```bash
# Start all services including PostgreSQL
docker-compose up -d

# Check database is ready
docker exec opssage-postgres pg_isready -U opssage
```

### Database Operations

**View incidents in database:**
```bash
docker exec opssage-postgres psql -U opssage -d opssage -c \
  "SELECT incident_id, alert_name, status, created_at FROM incidents ORDER BY created_at DESC LIMIT 10;"
```

**Check incident count:**
```bash
docker exec opssage-postgres psql -U opssage -d opssage -c \
  "SELECT COUNT(*) as total_incidents FROM incidents;"
```

**View incidents by status:**
```bash
docker exec opssage-postgres psql -U opssage -d opssage -c \
  "SELECT status, COUNT(*) FROM incidents GROUP BY status;"
```

**Query specific incident:**
```bash
docker exec opssage-postgres psql -U opssage -d opssage -c \
  "SELECT incident_id, alert_name, root_cause, confidence_score FROM incidents WHERE incident_id = 'your-incident-id';"
```

### API Endpoints

**List all incidents:**
```bash
curl http://localhost:8000/api/v1/incidents
```

**Filter by status:**
```bash
curl http://localhost:8000/api/v1/incidents?status=completed
curl http://localhost:8000/api/v1/incidents?status=failed
```

**Get specific incident:**
```bash
curl http://localhost:8000/api/v1/incidents/{incident_id}
```

**Delete incident:**
```bash
curl -X DELETE http://localhost:8000/api/v1/incidents/{incident_id}
```

## Database Lifecycle

### Initialization

The database tables are automatically created when the backend starts:

1. Backend container starts
2. `init_db()` is called in `apis/main.py` lifespan
3. SQLAlchemy creates tables if they don't exist
4. Application is ready to accept requests

### Data Persistence

All incident operations are automatically persisted:

```python
# Creating an incident
incident_id = await context_store.create_incident(alert)
# → Stored to database immediately

# Updating contexts
await context_store.update_primary_context(incident_id, primary_context)
await context_store.update_enhanced_context(incident_id, enhanced_context)
await context_store.update_diagnostic_report(incident_id, diagnostic_report)
# → All updates persisted immediately

# Retrieving incidents
incidents = await context_store.list_incidents(status="completed")
# → Fetched from database
```

### Backup and Recovery

**Backup database:**
```bash
docker exec opssage-postgres pg_dump -U opssage opssage > opssage_backup.sql
```

**Restore database:**
```bash
cat opssage_backup.sql | docker exec -i opssage-postgres psql -U opssage opssage
```

**Export to JSON:**
```bash
docker exec opssage-postgres psql -U opssage -d opssage -t -A -F"," -c \
  "SELECT row_to_json(incidents) FROM incidents;" > incidents.json
```

## Development

### Local Development with SQLite

For local development without Docker:

```bash
# No DATABASE_URL env var needed, defaults to SQLite
python run.py
```

This creates `./data/opssage.db` automatically.

### Database Migrations (Future)

The project includes Alembic for future database migrations:

```bash
# Initialize Alembic (not yet configured)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Inspecting the Database

**Connect to PostgreSQL:**
```bash
docker exec -it opssage-postgres psql -U opssage -d opssage
```

**Useful SQL queries:**
```sql
-- List all tables
\dt

-- Describe incidents table
\d incidents

-- View recent incidents
SELECT incident_id, alert_name, status, created_at
FROM incidents
ORDER BY created_at DESC
LIMIT 5;

-- Count by severity
SELECT severity, COUNT(*)
FROM incidents
GROUP BY severity;

-- Average confidence score
SELECT AVG(confidence_score) as avg_confidence
FROM incidents
WHERE status = 'completed';
```

## Troubleshooting

### Database Connection Issues

**Problem:** Backend fails to start with database connection error

**Solution:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check health
docker exec opssage-postgres pg_isready -U opssage

# View PostgreSQL logs
docker logs opssage-postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Table Not Found

**Problem:** Error says `relation "incidents" does not exist`

**Solution:**
```bash
# Restart backend to trigger table creation
docker-compose restart backend

# Check backend logs for initialization
docker logs opssage-backend | grep -i database
```

### Database Lock Issues (SQLite)

**Problem:** `database is locked` errors with SQLite

**Solution:**
Use PostgreSQL for multi-user scenarios. SQLite is only for single-user development.

### Checking Database URL

```bash
# View current configuration
docker exec opssage-backend env | grep DATABASE_URL

# Expected output (Docker):
# DATABASE_URL=postgresql://opssage:opssage_dev@postgres:5432/opssage
```

### Data Not Persisting

**Problem:** Incidents disappear after container restart

**Check:**
```bash
# Verify volume exists
docker volume ls | grep opssage

# Inspect volume
docker volume inspect opssage_postgres-data

# Check if data persists in volume
docker exec opssage-postgres du -sh /var/lib/postgresql/data
```

## Performance Considerations

### Connection Pooling

PostgreSQL uses connection pooling configured in `sages/db/database.py`:

```python
# PostgreSQL with connection pooling
pool_size=10,          # Normal pool size
max_overflow=20,       # Additional connections under load
pool_pre_ping=True,    # Verify connections before use
```

### Query Optimization

Denormalized fields (`alert_name`, `severity`, `namespace`, `service`) enable fast filtering without JSON queries:

```sql
-- Fast (uses index)
SELECT * FROM incidents WHERE severity = 'critical';

-- Slower (JSON query)
SELECT * FROM incidents WHERE alert_input->>'severity' = 'critical';
```

### Large Datasets

For deployments with >10,000 incidents:

1. **Implement pagination** in API endpoints
2. **Archive old incidents** to separate tables
3. **Add composite indexes** for common query patterns
4. **Enable query caching** at application level

## Security

### Production Deployment

For production, ensure:

1. **Change default password:**
   ```yaml
   environment:
     - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}  # Use secure password
   ```

2. **Restrict network access:**
   ```yaml
   postgres:
     ports: []  # Don't expose port externally
   ```

3. **Use SSL/TLS:**
   ```python
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   ```

4. **Enable authentication:**
   - Configure `pg_hba.conf` for proper auth
   - Use certificate-based auth for production

5. **Regular backups:**
   - Automated daily backups
   - Test restore procedures

## Files Modified

- `docker-compose.yml` - Added PostgreSQL service and volume
- `config.yaml` & `config.example.yaml` - Database configuration
- `pyproject.toml` & `uv.lock` - Added psycopg2-binary, alembic
- `apis/main.py` - Database initialization on startup
- `sages/context_store.py` - Database persistence layer
- `sages/db/__init__.py` - New database module
- `sages/db/models.py` - SQLAlchemy ORM models
- `sages/db/database.py` - Session management

## Summary

Database persistence provides:

✅ **Durable storage** of all incident analysis data
✅ **Production-ready** PostgreSQL with connection pooling
✅ **Fast queries** with indexed fields
✅ **Complete history** of all incidents and analysis
✅ **Backup & recovery** capabilities
✅ **Scalable** architecture for large deployments

All incidents now persist across container restarts, enabling reliable incident tracking and historical analysis.

# OpsSage Alert Testing

This directory contains test scripts and sample alerts for testing the OpsSage incident analysis system.

## Quick Start

### 1. Test Single Alert

```bash
# Make script executable
chmod +x test_alerts.sh

# Send a single alert
./test_alerts.sh 1
```

### 2. Test All Scenarios

```bash
# Send all test scenarios
./test_alerts.sh all
```

### 3. Manual curl Test

```bash
# Send alert using curl directly
curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/01_crashloop.json
```

## Available Test Scenarios

| # | Name | Severity | Description |
|---|------|----------|-------------|
| 1 | Pod CrashLoopBackOff | Critical | Payment service pod crash looping |
| 2 | Node CPU Exhaustion | Critical | Node CPU at 98%, pods throttled |
| 3 | OOM Kill | Critical | Analytics worker killed by OOM |
| 4 | Disk Pressure | Warning | Node disk usage at 92% |
| 5 | Network Latency | Warning | High latency between services (2500ms) |
| 6 | DB Connection Pool | Critical | PostgreSQL connections exhausted (95/100) |
| 7 | Service Down | Critical | Notification service unavailable |
| 8 | Failed Deployment | Critical | Deployment failed - ImagePullBackOff |

## Usage Examples

### Run Specific Scenario

```bash
# By number
./test_alerts.sh 1
./test_alerts.sh 2

# By name
./test_alerts.sh crashloop
./test_alerts.sh cpu
./test_alerts.sh oom
./test_alerts.sh disk
./test_alerts.sh network
./test_alerts.sh database
./test_alerts.sh service
./test_alerts.sh deployment
```

### Run All Scenarios

```bash
./test_alerts.sh all
```

### Custom API URL

```bash
# Test against different environment
API_URL=http://staging.example.com ./test_alerts.sh 1
```

## Test Alerts Structure

All alert files are in `alerts/` directory:

```
hacks/
├── test_alerts.sh          # Main test script
├── curl_examples.sh        # Quick curl examples
├── README.md               # This file
└── alerts/
    ├── 01_crashloop.json
    ├── 02_cpu_exhaustion.json
    ├── 03_oom_kill.json
    ├── 04_disk_pressure.json
    ├── 05_network_latency.json
    ├── 06_db_connections.json
    ├── 07_service_down.json
    └── 08_failed_deployment.json
```

## Alert JSON Format

Each alert follows this structure:

```json
{
  "alert_name": "AlertName",
  "severity": "critical|warning|info",
  "message": "Human-readable alert message",
  "labels": {
    "namespace": "production",
    "service": "service-name",
    "pod": "pod-name",
    "node": "node-name"
  },
  "annotations": {
    "summary": "Short summary",
    "description": "Detailed description",
    "runbook_url": "Link to runbook"
  },
  "firing_condition": "PromQL query that triggered alert",
  "timestamp": "2025-12-01T00:00:00Z"
}
```

## Expected Behavior

When you send an alert, you should:

1. **See console output:**
   ```
   ✓ Alert sent successfully (HTTP 200)
   ℹ Incident ID: abc123-def456-...
   ```

2. **Receive Telegram notification** (if configured):
   - 🚨 **Start notification** when analysis begins
   - ✅ **Completion notification** with root cause and remediation
   - ❌ **Error notification** if analysis fails

3. **Get API response:**
   ```json
   {
     "incident_id": "abc123-def456-...",
     "status": "completed",
     "diagnostic_report": {
       "root_cause": "...",
       "confidence_score": 0.85,
       "reasoning_steps": [...],
       "supporting_evidence": [...],
       "recommended_remediation": {
         "short_term_actions": [...],
         "long_term_actions": [...]
       }
     }
   }
   ```

## Telegram Configuration

To receive notifications, ensure Telegram is configured:

```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"
export GEMINI_API_KEY="your-gemini-key"

# Restart backend
docker-compose restart backend
```

See `docs/TELEGRAM_NOTIFICATION_FIX.md` for detailed setup instructions.

## Viewing Results

### 1. Check Backend Logs

```bash
# View recent logs
docker logs opssage-backend --tail 50

# Follow logs
docker logs opssage-backend -f

# Filter for specific incident
docker logs opssage-backend | grep "incident-id"
```

### 2. Query Incident API

```bash
# Get incident by ID
curl http://localhost:8000/api/v1/incidents/{incident_id}

# List all incidents
curl http://localhost:8000/api/v1/incidents

# List only failed incidents
curl http://localhost:8000/api/v1/incidents?status=failed
```

### 3. Check Telegram

Open your Telegram app and check the configured chat for notifications.

## Troubleshooting

### Backend Not Responding

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check container status
docker-compose ps

# Restart backend
docker-compose restart backend
```

### Alerts Not Sending

```bash
# Verify endpoint is correct
echo $API_URL

# Test with verbose curl
curl -v -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/01_crashloop.json
```

### Telegram Not Working

```bash
# Check Telegram configuration
docker exec opssage-backend python -c "
from sages.notifications import get_notifier
notifier = get_notifier()
print(f'Enabled: {notifier.enabled}')
print(f'Token: {bool(notifier.bot_token)}')
print(f'Chat ID: {bool(notifier.chat_id)}')
"
```

## Creating Custom Alerts

To create your own test alert:

1. Copy an existing alert file:
   ```bash
   cp alerts/01_crashloop.json alerts/99_custom.json
   ```

2. Edit the JSON:
   ```json
   {
     "alert_name": "YourCustomAlert",
     "severity": "warning",
     "message": "Your alert message",
     "labels": {...},
     "annotations": {...},
     "firing_condition": "your_metric > threshold",
     "timestamp": "2025-12-01T00:00:00Z"
   }
   ```

3. Send it:
   ```bash
   curl -X POST http://localhost:8000/api/v1/alerts \
     -H 'Content-Type: application/json' \
     -d @alerts/99_custom.json
   ```

## Performance Testing

To test system performance under load:

```bash
# Send multiple alerts rapidly
for i in {1..10}; do
  ./test_alerts.sh crashloop
  sleep 1
done

# Or use parallel execution
for i in {1..5}; do
  ./test_alerts.sh crashloop &
done
wait
```

**Note:** Be mindful of Gemini API rate limits when testing at scale.

## Integration Testing

The test scenarios are designed to cover different incident types:

- **Resource Issues**: CPU, Memory, Disk
- **Application Issues**: CrashLoop, OOM, Service Down
- **Network Issues**: Latency, Connection Pools
- **Deployment Issues**: Failed Rollouts, Image Pull Errors

Use these to validate that OpsSage correctly identifies root causes across different incident categories.

## Next Steps

1. ✅ Ensure backend is running: `make start`
2. ✅ Configure Telegram (optional): Set env vars
3. ✅ Run a test: `./test_alerts.sh 1`
4. ✅ Check Telegram for notifications
5. ✅ View diagnostic report in API response

Happy testing! 🚀

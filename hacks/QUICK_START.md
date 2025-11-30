# Quick Start - Testing OpsSage Alerts

## TL;DR

```bash
# Make scripts executable
chmod +x test_alerts.sh

# Send a test alert
./test_alerts.sh crashloop

# Check your Telegram for notifications! 📱
```

## What You Get

This directory contains **8 realistic Kubernetes incident scenarios** ready to test:

| Scenario | Type | Severity | Description |
|----------|------|----------|-------------|
| 🔄 CrashLoop | Application | 🔴 Critical | Pod restarting continuously |
| 🔥 CPU Exhaustion | Resource | 🔴 Critical | Node CPU at 98% |
| 💥 OOM Kill | Memory | 🔴 Critical | Container killed by OOM |
| 💾 Disk Pressure | Storage | 🟡 Warning | Disk at 92% |
| 🌐 Network Latency | Network | 🟡 Warning | 2500ms latency |
| 🗄️ DB Connections | Database | 🔴 Critical | Connection pool exhausted |
| ⚠️ Service Down | Availability | 🔴 Critical | All replicas down |
| 🚀 Failed Deployment | Deployment | 🔴 Critical | ImagePullBackOff |

## One-Line Test

```bash
# Test a specific scenario
./test_alerts.sh crashloop
./test_alerts.sh cpu
./test_alerts.sh oom

# Or test everything
./test_alerts.sh all
```

## Using curl Directly

```bash
# Simple test
curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/01_crashloop.json

# Pretty output
curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d @alerts/01_crashloop.json | jq .
```

## What Happens?

When you send an alert:

1. **🟢 Console Output:**
   ```
   ✓ Alert sent successfully (HTTP 200)
   ℹ Incident ID: abc123-def456-...
   ```

2. **📱 Telegram (if configured):**
   - 🚨 "Incident Analysis Started"
   - ⏳ Analysis runs (15-30 seconds)
   - ✅ "Incident Analysis Complete" with root cause

3. **📊 API Response:**
   ```json
   {
     "incident_id": "...",
     "status": "completed",
     "diagnostic_report": {
       "root_cause": "...",
       "confidence_score": 0.85,
       "recommended_remediation": {...}
     }
   }
   ```

## File Structure

```
hacks/
├── test_alerts.sh          # 🚀 Main test script (use this!)
├── curl_examples.sh        # 📝 curl reference examples
├── README.md               # 📖 Full documentation
├── QUICK_START.md          # ⚡ This file
└── alerts/
    ├── 01_crashloop.json          # Pod crash looping
    ├── 02_cpu_exhaustion.json     # High CPU usage
    ├── 03_oom_kill.json           # Out of memory
    ├── 04_disk_pressure.json      # Disk space low
    ├── 05_network_latency.json    # Network issues
    ├── 06_db_connections.json     # DB pool exhausted
    ├── 07_service_down.json       # Service unavailable
    └── 08_failed_deployment.json  # Deployment failure
```

## Telegram Setup (Optional)

To receive notifications:

```bash
# 1. Set environment variables
export TELEGRAM_BOT_TOKEN="your-token"
export TELEGRAM_CHAT_ID="your-chat-id"

# 2. Restart backend
docker-compose restart backend

# 3. Test!
./test_alerts.sh crashloop
```

See `docs/TELEGRAM_NOTIFICATION_FIX.md` for detailed setup.

## Troubleshooting

**Backend not responding?**
```bash
curl http://localhost:8000/api/v1/health
docker-compose ps
docker-compose restart backend
```

**No Telegram notifications?**
```bash
# Check if enabled
docker exec opssage-backend python -c "
from sages.notifications import get_notifier
print(f'Enabled: {get_notifier().enabled}')
"
```

## Examples

### Test a specific scenario
```bash
./test_alerts.sh crashloop
```

### Test all scenarios
```bash
./test_alerts.sh all
```

### Use different API URL
```bash
API_URL=http://staging.example.com ./test_alerts.sh crashloop
```

### View curl examples
```bash
./curl_examples.sh
```

## What's Next?

1. ✅ Run a test: `./test_alerts.sh crashloop`
2. ✅ Check Telegram (if configured)
3. ✅ Review diagnostic report
4. ✅ Try different scenarios
5. ✅ Create your own custom alerts (see README.md)

## Need Help?

- **Full docs**: See `README.md` in this directory
- **Telegram setup**: See `../docs/TELEGRAM_NOTIFICATION_FIX.md`
- **API docs**: Check `../docs/` for system documentation

Happy testing! 🚀

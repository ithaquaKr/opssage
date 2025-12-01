# Telegram Notification Integration Fix

## Problem

When triggering alerts via the API (e.g., `POST /api/v1/alerts`), Telegram notifications were not being sent. The system would process incidents successfully, but users would not receive any notifications in their Telegram channels.

## Root Cause

The **orchestrator** (`sages/orchestrator.py`) was not integrated with the Telegram notification system. While the E2E tests manually sent notifications, the production code path (API → Orchestrator → Analysis) had no notification calls.

### Code Analysis

**Before the fix:**

1. **API Endpoint** (`apis/main.py:65-92`):
   ```python
   @app.post("/api/v1/alerts", response_model=dict)
   async def ingest_alert(alert: AlertInput):
       # Run analysis
       incident_id, diagnostic_report = await app.state.orchestrator.analyze_incident(alert)
       return {...}  # No notification sent
   ```

2. **Orchestrator** (`sages/orchestrator.py:73-122`):
   ```python
   async def analyze_incident(self, alert: AlertInput) -> tuple[str, IncidentDiagnosticReport]:
       incident_id = await self.context_store.create_incident(alert)
       # Run AICA → KREA → RCARA pipeline
       # No notifications sent anywhere
       return incident_id, diagnostic_report
   ```

3. **Tests** (`tests/test_e2e_scenarios.py:195-218`):
   ```python
   # Tests manually sent notifications
   await notifier.send_incident_start(incident_id, alert)
   incident_id, diagnostic_report = await orchestrator.analyze_incident(alert)
   await notifier.send_incident_complete(incident_id, alert, diagnostic_report, duration)
   ```

The notification system existed and worked (proven by tests), but it wasn't integrated into the production code path.

## Solution

Integrated Telegram notifications directly into the orchestrator's `analyze_incident` method to ensure every incident triggers appropriate notifications.

### Changes Made

#### 1. Import Telegram Notifier (sages/orchestrator.py:35)

```python
from sages.notifications import get_notifier
```

#### 2. Initialize Notifier in Orchestrator (sages/orchestrator.py:55)

```python
def __init__(self) -> None:
    """Initialize the orchestrator with agent instances."""
    self.aica: Agent = create_aica_agent()
    self.krea: Agent = create_krea_agent()
    self.rcara: Agent = create_rcara_agent()
    self.context_store = get_context_store()
    self.notifier = get_notifier()  # ← Added
    # ... setup runners
```

#### 3. Send Notifications in Analysis Pipeline (sages/orchestrator.py:75-143)

```python
async def analyze_incident(
    self, alert: AlertInput
) -> tuple[str, IncidentDiagnosticReport]:
    import time

    incident_id = await self.context_store.create_incident(alert)

    # Send start notification ← NEW
    start_time = time.time()
    await self.notifier.send_incident_start(incident_id, alert)

    try:
        # Run AICA → KREA → RCARA pipeline
        primary_context = await self._run_aica(alert)
        enhanced_context = await self._run_krea(primary_context)
        diagnostic_report = await self._run_rcara(primary_context, enhanced_context)

        # Send completion notification ← NEW
        duration = time.time() - start_time
        await self.notifier.send_incident_complete(
            incident_id, alert, diagnostic_report, duration
        )

        return incident_id, diagnostic_report

    except Exception as e:
        logger.error(f"Error analyzing incident {incident_id}: {e}")

        # Send error notification ← NEW
        duration = time.time() - start_time
        await self.notifier.send_incident_error(
            incident_id, alert, str(e), duration
        )

        raise
```

## Files Modified

1. **sages/orchestrator.py** (4 changes):
   - Added `get_notifier` import
   - Added `self.notifier = get_notifier()` in `__init__`
   - Added `send_incident_start()` call at start of analysis
   - Added `send_incident_complete()` call on success
   - Added `send_incident_error()` call on failure

## Notification Flow

### Success Flow

```
User sends alert via API
  ↓
API calls orchestrator.analyze_incident(alert)
  ↓
🟢 START: send_incident_start() → Telegram
  ↓
AICA analyzes alert
  ↓
KREA enriches context
  ↓
RCARA performs root cause analysis
  ↓
✅ COMPLETE: send_incident_complete() → Telegram
  ↓
Return diagnostic report to user
```

### Error Flow

```
User sends alert via API
  ↓
API calls orchestrator.analyze_incident(alert)
  ↓
🟢 START: send_incident_start() → Telegram
  ↓
Error occurs during analysis
  ↓
❌ ERROR: send_incident_error() → Telegram
  ↓
Exception propagated to API
```

## Telegram Configuration

For notifications to work, you must configure Telegram credentials:

### 1. Set Environment Variables

```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"
export GEMINI_API_KEY="your-gemini-key"
```

### 2. Update docker-compose.yml (if using Docker)

Ensure environment variables are passed to the container:

```yaml
services:
  backend:
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
```

### 3. Verify Configuration

```bash
# Check if Telegram is enabled
docker exec opssage-backend python -c "
from sages.notifications import get_notifier
notifier = get_notifier()
print(f'Telegram enabled: {notifier.enabled}')
print(f'Bot token set: {bool(notifier.bot_token)}')
print(f'Chat ID set: {bool(notifier.chat_id)}')
"
```

**Expected output (when properly configured):**
```
Telegram enabled: True
Bot token set: True
Chat ID set: True
```

**Current output (missing CHAT_ID):**
```
Telegram enabled: False
Bot token set: True
Chat ID set: False
Telegram notifications disabled: Check config.yaml telegram settings
```

### 4. Get Telegram Credentials

If you don't have Telegram credentials yet:

1. **Create Bot:**
   - Open Telegram → Search @BotFather
   - Send `/newbot` → Follow prompts
   - Copy the bot token

2. **Get Chat ID:**
   - Start a chat with your bot
   - Send any message
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find `chat_id` in the JSON response

3. **Set Environment Variables:**
   ```bash
   export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
   export TELEGRAM_CHAT_ID="123456789"
   ```

4. **Restart Backend:**
   ```bash
   docker-compose restart backend
   ```

## Testing

### 1. Test with Simple Alert

```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d '{
    "alert_name": "TestAlert",
    "severity": "warning",
    "message": "Testing Telegram notifications",
    "labels": {"namespace": "test", "service": "test"},
    "annotations": {},
    "firing_condition": "test > 0",
    "timestamp": "2025-11-30T18:00:00Z"
  }'
```

### 2. Expected Telegram Messages

**Start Notification:**
```
🚨 Incident Analysis Started

Incident ID: abc123-def456
Alert: TestAlert
Severity: WARNING
Namespace: test
Service: test

Message: Testing Telegram notifications

⏳ Analysis in progress...
```

**Completion Notification (if successful):**
```
✅ Incident Analysis Complete

Incident ID: abc123-def456
Alert: TestAlert
Duration: 25.3s

🎯 Root Cause (Confidence: 85%):
[Root cause identified by RCARA]

🔧 Immediate Actions:
  • [Action 1]
  • [Action 2]
  • [Action 3]

📊 Analysis Steps: 5
📝 Evidence Items: 8
```

**Error Notification (if failed):**
```
❌ Incident Analysis Failed

Incident ID: abc123-def456
Alert: TestAlert
Duration: 5.2s

⚠️ Error:
```
[Error message]
```

Please check the logs for more details.
```

### 3. Check Backend Logs

```bash
docker logs opssage-backend --tail 50 | grep -i telegram
```

**Expected (when enabled):**
```
INFO: Telegram notification sent successfully to chat 123456789
```

**Expected (when disabled):**
```
WARNING: Telegram notifications disabled: Check config.yaml telegram settings
DEBUG: Telegram not enabled, skipping notification
```

## Verification Checklist

- ✅ **Code Fix**: Orchestrator now calls Telegram notifier
- ✅ **Start Notification**: Sent when analysis begins
- ✅ **Complete Notification**: Sent when analysis succeeds
- ✅ **Error Notification**: Sent when analysis fails
- ⚠️ **Configuration Required**: Set `TELEGRAM_CHAT_ID` environment variable

## Impact

### Before Fix
- ✅ Tests sent notifications (manual integration in test code)
- ❌ API alerts sent NO notifications
- ❌ Production incidents invisible to operators

### After Fix
- ✅ Tests send notifications (existing behavior preserved)
- ✅ API alerts send notifications automatically
- ✅ Production incidents visible in Telegram
- ✅ Error cases handled with error notifications

## Configuration Status

**Current Issue:** `TELEGRAM_CHAT_ID` environment variable is not set.

**To Enable Notifications:**

```bash
# Set the missing environment variable
export TELEGRAM_CHAT_ID="your-chat-id"

# Restart the backend
docker-compose restart backend

# Verify it's enabled
docker exec opssage-backend python -c "
from sages.notifications import get_notifier
print(f'Enabled: {get_notifier().enabled}')
"
```

## Summary

✅ **Fixed**: Orchestrator now integrates with Telegram notification system
✅ **Added**: Start, completion, and error notifications for all incidents
✅ **Verified**: Backend is healthy and code is in place
⚠️ **Action Required**: Set `TELEGRAM_CHAT_ID` environment variable to enable notifications

The notification infrastructure is now fully integrated. Once `TELEGRAM_CHAT_ID` is configured, all alerts sent via the API will trigger Telegram notifications automatically.

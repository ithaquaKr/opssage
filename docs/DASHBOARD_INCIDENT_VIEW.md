# Dashboard Incident View Upgrade

## Overview

The OpsSage dashboard has been upgraded to provide comprehensive incident management capabilities, including:

1. **Incident List View** - Browse all incidents with filtering and real-time updates
2. **Incident Detail View** - View complete incident analysis with all diagnostic information
3. **Telegram Link Integration** - Click through from Telegram notifications to full incident reports

## New Features

### 1. Incident List Page (`/incidents`)

**Features:**
- 📋 List all incidents with real-time updates (polls every 10 seconds)
- 🔍 Filter by status: All, Completed, Failed
- 🎨 Color-coded severity badges (Critical, Warning, Info)
- ⚡ Status indicators with icons (Running, Completed, Failed)
- 📊 Preview of root cause and confidence score
- 🔗 Click any incident to view full details

**Status Indicators:**
- ✅ **Completed** - Green checkmark
- ❌ **Failed** - Red X
- ⏳ **Running (AICA)** - Blue, spinning clock
- ⏳ **Running (KREA)** - Purple, spinning clock
- ⏳ **Running (RCARA)** - Indigo, spinning clock
- ⚪ **Pending** - Yellow clock

**Information Displayed:**
- Alert name and severity
- Incident status
- Alert message (truncated if long)
- Incident ID (first 8 chars)
- Namespace and Service (from labels)
- Creation timestamp
- Root cause preview (if completed)
- Confidence score (if completed)

### 2. Incident Detail Page (`/incidents/:id`)

**Sections:**

#### Alert Information
- Incident ID (full)
- Creation timestamp
- Alert message (full text)
- Firing condition (in code block)

#### Affected Components
- Namespace
- Service
- Pod name
- Node name

#### Root Cause Analysis
- Confidence score with visual progress bar
- Full root cause description
- Highlighted in red box for visibility

#### Recommended Remediation
- **Immediate Actions** (numbered list)
  - Short-term fixes to resolve the incident
- **Long-term Improvements** (numbered list)
  - Preventive measures to avoid recurrence

#### Analysis Steps
- Step-by-step reasoning process
- Numbered sequence showing how conclusion was reached

#### Supporting Evidence
- Bullet points of evidence that supports the root cause
- Green checkmarks for each evidence item

#### Real-time Updates
- Auto-refreshes every 5 seconds for in-progress incidents
- Shows loading indicator with message during analysis
- Automatically displays report when complete

### 3. Navigation Updates

The sidebar navigation now includes:
- 🚨 **Incidents** (default home page)
- 📁 **Documents**
- 🔍 **Search**

The Incidents page is now the default landing page for the dashboard.

## Telegram Notification Improvements

### Problem Solved
Telegram messages have a **4096 character limit**. Long incident reports were getting truncated or failed to send.

### Solution
All Telegram notifications now include:
1. **Shortened message** with key information only
2. **Clickable link** to view full details in dashboard

### Updated Notification Formats

#### Start Notification
```
🚨 Incident Analysis Started

Alert: PodCrashLoopBackOff
Severity: CRITICAL
Namespace: production
Service: payment-service

Message: Pod payment-service-7d8f9b5c-xyz...

⏳ Analysis in progress...

[View Full Details](http://localhost:3000/incidents/abc-123...)
```

**Improvements:**
- Removed incident ID from main message (clickable link includes it)
- Truncated long messages to 150 characters

#### Completion Notification
```
✅ Incident Analysis Complete

Alert: PodCrashLoopBackOff
Duration: 25.3s

🎯 Root Cause (85%):
Database connection pool exhausted due to...

🔧 Top Actions:
  • Increase database connection pool size
  • Add connection timeout configuration
  • +3 more actions

[📊 View Full Report](http://localhost:3000/incidents/abc-123...)
```

**Improvements:**
- Shows only top 2 immediate actions
- Indicates number of additional actions available
- Truncated root cause to 150 characters
- Removed incident ID, reasoning steps count, and evidence count
- **All details available via clickable link**

#### Error Notification
```
❌ Incident Analysis Failed

Alert: PodCrashLoopBackOff
Duration: 5.2s

⚠️ Error:
```
Validation error: Missing required field...
```

[View Incident Details](http://localhost:3000/incidents/abc-123...)
```

**Improvements:**
- Removed incident ID from main message
- Truncated error to 200 characters
- Link to view incident for more context

## Configuration

### Dashboard URL Configuration

Added to `config.yaml` and `config.example.yaml`:

```yaml
telegram:
  enabled: true
  bot_token: ${TELEGRAM_BOT_TOKEN}
  chat_id: ${TELEGRAM_CHAT_ID}
  dashboard_url: http://localhost:3000  # Dashboard URL for incident links
```

**For production deployment:**
```yaml
telegram:
  dashboard_url: https://opssage.yourdomain.com
```

Or set via environment variable:
```bash
export DASHBOARD_URL=https://opssage.yourdomain.com
```

## Files Created/Modified

### New Files Created

1. **dashboard/src/pages/Incidents.tsx** (235 lines)
   - Incident list page component
   - Filtering, auto-refresh, status badges

2. **dashboard/src/pages/IncidentDetail.tsx** (436 lines)
   - Incident detail page component
   - Full diagnostic report display
   - Real-time updates for in-progress incidents

### Modified Files

1. **dashboard/src/App.tsx**
   - Added incident routes
   - Set incidents as default home page

2. **dashboard/src/components/Layout.tsx**
   - Added Incidents to navigation
   - Updated active state logic for incident routes

3. **sages/notifications.py**
   - Added `dashboard_url` configuration
   - Shortened all notification messages
   - Added clickable links to all notifications
   - Improved message truncation

4. **config.yaml** & **config.example.yaml**
   - Added `telegram.dashboard_url` configuration

## Usage

### Viewing Incidents

1. **Open Dashboard:**
   ```
   http://localhost:3000
   ```
   You'll see the Incidents list page.

2. **Filter Incidents:**
   Click "All", "Completed", or "Failed" buttons.

3. **View Details:**
   Click on any incident to view full analysis.

4. **Return to List:**
   Click "← Back to Incidents" at the top.

### From Telegram

1. **Receive Notification:**
   When an incident is created, you'll get a Telegram message.

2. **Click Link:**
   Click "View Full Details" or "View Full Report" link.

3. **Dashboard Opens:**
   Browser opens directly to the incident detail page.

## Testing

### Test the Dashboard

```bash
# Ensure services are running
docker-compose ps

# Open dashboard
open http://localhost:3000

# Or manually navigate
# http://localhost:3000/incidents
```

### Test Telegram Links

```bash
# Send a test alert
cd hacks
./test_alerts.sh crashloop

# Check Telegram for notification
# Click the "View Full Details" link
# Verify it opens the incident in the dashboard
```

### Test with Multiple Incidents

```bash
# Send multiple alerts
./test_alerts.sh all

# Go to dashboard
open http://localhost:3000

# Verify:
# - All incidents appear in the list
# - Each incident is clickable
# - Filtering works (All, Completed, Failed)
# - Real-time updates work (status changes)
```

## API Endpoints Used

The dashboard uses these backend API endpoints:

- `GET /api/v1/incidents` - List all incidents
- `GET /api/v1/incidents?status=completed` - Filter by status
- `GET /api/v1/incidents/:id` - Get incident details

All endpoints return JSON with full incident context including:
- Alert input
- Primary context (from AICA)
- Enhanced context (from KREA)
- Diagnostic report (from RCARA)

## Responsive Design

The dashboard is fully responsive:
- **Desktop**: Full sidebar, optimal layout
- **Tablet**: Sidebar visible, compact spacing
- **Mobile**: Responsive text, mobile-friendly buttons

## Real-time Features

### Auto-refresh

1. **Incident List:**
   - Polls every **10 seconds**
   - Updates incident statuses automatically
   - Shows new incidents as they're created

2. **Incident Detail:**
   - Polls every **5 seconds** for in-progress incidents
   - Stops polling when incident is completed/failed
   - Automatically shows diagnostic report when ready

### Loading States

- Spinner while fetching data
- "Analysis in Progress" message for running incidents
- Smooth transitions between states

## Troubleshooting

### Dashboard Not Loading

```bash
# Check dashboard is running
docker-compose ps

# Restart dashboard
docker-compose restart dashboard

# Check logs
docker logs opssage-dashboard
```

### Incidents Not Showing

```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Check incidents endpoint
curl http://localhost:8000/api/v1/incidents

# Restart backend
docker-compose restart backend
```

### Telegram Links Not Working

1. **Check configuration:**
   ```bash
   # Verify dashboard_url is set
   docker exec opssage-backend cat /app/config.yaml | grep dashboard_url
   ```

2. **Expected output:**
   ```yaml
   dashboard_url: http://localhost:3000
   ```

3. **If missing, add to config.yaml:**
   ```yaml
   telegram:
     dashboard_url: http://localhost:3000
   ```

4. **Restart backend:**
   ```bash
   docker-compose restart backend
   ```

### 404 on Incident Detail Page

- Ensure the incident ID is correct
- Check if incident exists: `curl http://localhost:8000/api/v1/incidents/{id}`
- Verify routing is set up correctly in App.tsx

## Performance Considerations

### Polling Impact

- Incidents list polls every 10 seconds
- Detail page polls every 5 seconds (only for in-progress incidents)
- Both use lightweight API calls
- No significant performance impact for <100 concurrent incidents

### Optimization Tips

For large deployments with many incidents:

1. **Add Pagination:**
   Modify `Incidents.tsx` to add pagination support

2. **Implement WebSockets:**
   Replace polling with real-time WebSocket updates

3. **Add Caching:**
   Cache completed incidents (they don't change)

4. **Lazy Loading:**
   Load diagnostic reports on-demand

## Future Enhancements

Potential improvements:

1. **Search & Filter:**
   - Search by alert name, service, namespace
   - Date range filtering
   - Severity filtering

2. **Bulk Actions:**
   - Mark multiple incidents as reviewed
   - Export multiple reports

3. **Notifications:**
   - Browser push notifications
   - Email notifications
   - Slack integration

4. **Analytics:**
   - Incident trends dashboard
   - Mean time to resolution (MTTR)
   - Common failure patterns

5. **Comments:**
   - Add notes to incidents
   - Collaborate on resolution

## Summary

✅ **Implemented:**
- Incident list view with filtering
- Incident detail view with full diagnostic information
- Telegram notification links to dashboard
- Message truncation to avoid Telegram limits
- Real-time updates and auto-refresh
- Responsive design

✅ **Benefits:**
- No more truncated Telegram messages
- Full incident details always accessible
- Better incident management workflow
- Improved user experience

✅ **Ready to Use:**
Open http://localhost:3000 and start managing incidents!

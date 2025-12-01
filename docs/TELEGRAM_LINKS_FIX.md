# Telegram Links Not Clickable - Fixed

## Root Cause

**Telegram Bot API does not support `localhost` URLs in clickable links.**

When you send a message with `<a href="http://localhost:3000">link</a>`:
- The HTML is parsed correctly
- The bold text works
- But the link is **stripped out** and becomes plain text

### Test Results

```
✅ https://google.com      → Clickable link
✅ http://example.com      → Clickable link
❌ http://localhost:3000   → Plain text (not clickable)
```

This happens because `localhost` refers to the local device. When you click it on your phone's Telegram app, it would try to connect to your phone's localhost, not your server.

## Solutions

### Option 1: Use ngrok (Quickest for Testing)

```bash
# Install ngrok (if not installed)
# brew install ngrok  # macOS
# Or download from https://ngrok.com/download

# Start ngrok tunnel to your dashboard
ngrok http 3000
```

This will give you a public URL like `https://abc123.ngrok.io`

Then set the environment variable:
```bash
export DASHBOARD_URL="https://abc123.ngrok.io"

# Restart backend
docker-compose restart backend
```

### Option 2: Use Your Server's Public IP/Domain

If your server has a public IP or domain:

```bash
# Using public IP
export DASHBOARD_URL="http://YOUR_SERVER_IP:3000"

# Or using domain name
export DASHBOARD_URL="https://yourdomain.com"

# Restart backend
docker-compose restart backend
```

### Option 3: Update docker-compose.yml

Add the environment variable to your docker-compose.yml:

```yaml
services:
  backend:
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
      - DASHBOARD_URL=${DASHBOARD_URL:-http://localhost:3000}  # Add this
```

Then:
```bash
export DASHBOARD_URL="https://your-public-url.com"
docker-compose up -d
```

### Option 4: Deploy Dashboard Publicly

Deploy your dashboard on a cloud platform:
- Vercel
- Netlify
- AWS
- Google Cloud
- etc.

Then use that public URL.

## Testing

After setting the public URL, test with:

```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d '{
    "alert_name": "TestClickableLink",
    "severity": "warning",
    "message": "Testing with public URL",
    "labels": {"namespace": "test", "service": "test"},
    "annotations": {},
    "firing_condition": "test > 0",
    "timestamp": "2025-12-01T00:00:00Z"
  }'
```

Check your Telegram - the link should now be clickable!

## Verification

You can verify the link is working by checking the Telegram API response:

```bash
docker exec opssage-backend python -c "
import os
from sages.notifications import get_notifier

notifier = get_notifier()
print(f'Dashboard URL: {notifier.dashboard_url}')
print(f'Is localhost: {\"localhost\" in notifier.dashboard_url}')
"
```

If it still shows `localhost`, the environment variable isn't set correctly.

## Why This Happens

Telegram's security model doesn't allow bots to link to:
- `localhost` URLs (refers to user's device)
- `127.0.0.1` (same as localhost)
- Private IP ranges (192.168.x.x, 10.x.x.x)
- `file://` URLs

Only publicly accessible HTTP/HTTPS URLs are converted to clickable links.

## Changes Made

1. **sages/notifications.py**: Changed parse mode from Markdown to HTML (more reliable)
2. **config.yaml**: Added `DASHBOARD_URL` environment variable support
3. Updated all message formats to use HTML syntax: `<a href="url">text</a>`

The code is correct - you just need to use a public URL instead of localhost!

# OpsSage Setup Guide

Complete setup instructions for OpsSage - Multi-Agent Incident Response System.

---

## 📋 Prerequisites

### Required

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Python** 3.10 or higher
- **Node.js** 18+ and **npm** or **pnpm**

### API Keys

You'll need:

1. **Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Telegram Bot** - Create with [@BotFather](https://t.me/botfather)

---

## 🚀 Quick Setup (5 Minutes)

### 1. Clone Repository

```bash
git clone <repository-url>
cd opssage
```

### 2. Create Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow prompts to create your bot
4. Copy the **Bot Token** (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
5. Get your **Chat ID**:
    - Message your bot
    - Visit: `https://api.telegram.org/bot<YourBotToken>/getUpdates`
    - Look for `"chat":{"id":<YourChatID>}` in the response

### 3. Set Environment Variables

```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
export TELEGRAM_CHAT_ID="your-chat-id-here"
```

**Tip**: Add these to your `~/.bashrc` or `~/.zshrc` to make them permanent:

```bash
echo 'export GEMINI_API_KEY="your-key"' >> ~/.bashrc
echo 'export TELEGRAM_BOT_TOKEN="your-token"' >> ~/.bashrc
echo 'export TELEGRAM_CHAT_ID="your-chat-id"' >> ~/.bashrc
source ~/.bashrc
```

### 4. Install Dependencies

```bash
make install
```

This installs:

- Python dependencies via `uv`
- Node.js dependencies for dashboard

### 5. Start the System

```bash
make start
```

The system will start:

- **Backend API**: <http://localhost:8000>
- **Dashboard**: <http://localhost:3000>
- **ChromaDB**: <http://localhost:8001>

### 6. Verify Setup

Open <http://localhost:3000> in your browser. You should see the OpsSage dashboard.

Send a test notification:

```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alert_name": "SetupTest",
    "severity": "info",
    "message": "OpsSage setup complete!",
    "labels": {"source": "setup"},
    "annotations": {"description": "Testing the system"},
    "firing_condition": "test"
  }'
```

Check your Telegram - you should receive a notification! 📱

---

## 📚 Upload Knowledge Base Documents

For OpsSage to provide intelligent analysis, upload your runbooks and documentation.

### Via Dashboard (Recommended)

1. Open <http://localhost:3000>
2. Click "Upload Document"
3. Select PDF, Markdown, DOCX, or TXT files
4. Click "Upload"

### Via Command Line

```bash
make upload-doc DOC=path/to/runbook.pdf
```

### Via cURL

```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@runbook.pdf" \
  -F "metadata={\"type\":\"runbook\",\"team\":\"platform\"}"
```

### Supported Formats

- **PDF** (.pdf)
- **Markdown** (.md)
- **Word** (.docx)
- **Text** (.txt)

---

## 🧪 Run E2E Tests

Test the complete system with realistic Kubernetes incident scenarios:

```bash
make test
```

This runs 3 scenarios:

1. Pod CrashLoopBackOff
2. Node CPU Exhaustion
3. Multi-Service Dependency Failure

**Check your Telegram** during tests - you'll receive notifications for each scenario!

---

## ⚙️ Configuration

### config.yaml

The main configuration file. Default values work for most cases.

```yaml
system:
    name: OpsSage
    log_level: INFO # Change to DEBUG for verbose logs
    host: 0.0.0.0
    port: 8000

models:
    worker_model: gemini-1.5-flash # Fast model for most tasks
    critic_model: gemini-1.5-pro # Powerful model for analysis
    gemini_api_key: ${GEMINI_API_KEY}

telegram:
    enabled: true
    bot_token: ${TELEGRAM_BOT_TOKEN}
    chat_id: ${TELEGRAM_CHAT_ID}

rag:
    enabled: true
    chromadb_path: ./data/chromadb
    knowledge_base_path: ./knowledge_base
    embedding_model: all-MiniLM-L6-v2
    chunk_size: 1000
    chunk_overlap: 200
    max_search_results: 5

api:
    cors_origins:
        - http://localhost:3000
        - http://localhost:5173
    max_upload_size_mb: 10
```

### Environment Variables (Secrets)

Never put secrets in `config.yaml`! Always use environment variables:

- `GEMINI_API_KEY` - Your Google Gemini API key
- `TELEGRAM_BOT_TOKEN` - Telegram bot token from BotFather
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID

---

## 🔧 Development Setup

### Local Development (No Docker)

```bash
# Start backend
python run.py

# In another terminal, start dashboard
cd dashboard
npm run dev
```

### Development Mode with Hot Reload

```bash
make dev
```

This starts:

- Backend with auto-reload on code changes
- Dashboard with Vite hot module replacement

---

## 📊 Verify Installation

### Check System Status

```bash
make status
```

Should show all services running and healthy.

### Check API Health

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:

```json
{
    "status": "healthy",
    "components": {
        "orchestrator": "ok",
        "context_store": "ok"
    }
}
```

### Test Document Search

```bash
make search-docs QUERY="kubernetes pod"
```

### View Logs

```bash
make logs
```

---

## 🐛 Troubleshooting

### Port Already in Use

If ports 8000, 3000, or 8001 are in use:

```bash
# Stop all services
make stop

# Check what's using the ports
lsof -i :8000
lsof -i :3000
lsof -i :8001

# Kill the processes or change ports in docker-compose.yml
```

### Docker Compose Not Found

Install Docker Compose:

```bash
# macOS
brew install docker-compose

# Linux
sudo apt-get install docker-compose

# Or use Docker Compose V2
docker compose version
```

### Telegram Bot Not Responding

1. Make sure you've sent `/start` to your bot in Telegram
2. Verify bot token and chat ID are correct
3. Check bot token is active:

    ```bash
    curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
    ```

### ChromaDB Issues

Reset the database:

```bash
make clean-data  # WARNING: Deletes all documents!
make start
```

### Python Dependencies Issues

```bash
# Reinstall dependencies
pip install uv
uv pip install -e .
```

---

## 🛑 Uninstall / Cleanup

### Stop Services

```bash
make stop
```

### Clean Cache

```bash
make clean
```

### Remove All Data

```bash
make clean-data  # WARNING: Deletes knowledge base!
```

### Complete Removal

```bash
make stop
make clean-data
docker-compose down -v --rmi all
rm -rf data/
```

---

## 📚 Next Steps

1. **Upload Documents**: Add your runbooks and documentation
2. **Configure Alerts**: Set up alert sources to send to OpsSage API
3. **Run Tests**: Verify everything works with `make test`
4. **Monitor**: Check Telegram for incident notifications
5. **Iterate**: Refine knowledge base and alert routing

---

## 🆘 Getting Help

- Check logs: `make logs`
- Check status: `make status`
- Test individual components
- Review test output: `make test`

---

## ✅ Setup Checklist

- [ ] Docker and Docker Compose installed
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Gemini API key obtained
- [ ] Telegram bot created
- [ ] Telegram chat ID obtained
- [ ] Environment variables set
- [ ] Dependencies installed (`make install`)
- [ ] System started (`make start`)
- [ ] Dashboard accessible (<http://localhost:3000>)
- [ ] API accessible (<http://localhost:8000/docs>)
- [ ] Test alert sent and received on Telegram
- [ ] Documents uploaded to knowledge base
- [ ] E2E tests passed (`make test`)

**You're all set! 🎉**

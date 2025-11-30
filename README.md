# OpsSage

**Multi-Agent Incident Response System with RAG Knowledge Base**

OpsSage is an AI-powered incident response system that analyzes alerts, retrieves relevant knowledge, and provides root cause analysis with remediation suggestions. It uses a multi-agent architecture (AICA → KREA → RCARA) and sends Telegram notifications.

---

## 🚀 Quick Start

### 1. Set Environment Variables

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
export TELEGRAM_CHAT_ID="your-telegram-chat-id"
```

### 2. Start the System

```bash
make start
```

### 3. Access the System

- **Dashboard**: <http://localhost:3000> (Upload & search documents)
- **API Docs**: <http://localhost:8000/docs>
- **ChromaDB**: <http://localhost:8001>

---

## 📦 What's Included

- **Multi-Agent System**: AICA (Alert Ingestion) → KREA (Knowledge Retrieval) → RCARA (Root Cause Analysis)
- **RAG Knowledge Base**: Upload and search runbooks, documentation, and playbooks
- **Document Management**: Web UI for uploading PDFs, Markdown, DOCX, and TXT files
- **Telegram Notifications**: Real-time incident alerts and analysis results
- **E2E Testing**: Complete test scenarios with Telegram integration

---

## 📋 Use Cases

### Use Case 1: Production System

Run OpsSage to analyze incidents and send Telegram notifications:

```bash
# Start system
make start

# Upload runbooks via dashboard
# Visit http://localhost:3000

# System automatically:
# 1. Receives alerts via API
# 2. Retrieves relevant knowledge
# 3. Analyzes root cause
# 4. Sends Telegram notification
```

### Use Case 2: E2E Testing

Test the complete pipeline with realistic scenarios:

```bash
# Run all test scenarios
make test

# Run specific scenario
make test-scenario SCENARIO=scenario_1

# Check Telegram for test notifications! 📱
```

Test scenarios include:

- **Scenario 1**: Pod CrashLoopBackOff (misconfigured env var)
- **Scenario 2**: Node CPU Exhaustion (resource saturation)
- **Scenario 3**: Multi-Service Dependency Failure (cascading outage)

---

## 🛠️ Installation

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Node.js 18+ (for dashboard)

### Install Dependencies

```bash
make install
```

See [SETUP.md](SETUP.md) for detailed setup instructions.

---

## 📚 Configuration

All configuration is in `config.yaml`:

```yaml
system:
    log_level: INFO

models:
    worker_model: gemini-1.5-flash
    critic_model: gemini-1.5-pro
    gemini_api_key: ${GEMINI_API_KEY}

telegram:
    enabled: true
    bot_token: ${TELEGRAM_BOT_TOKEN}
    chat_id: ${TELEGRAM_CHAT_ID}

rag:
    chromadb_path: ./data/chromadb
    max_search_results: 5
```

Secrets are read from environment variables for security.

---

## 🎯 Common Tasks

### Upload Documents to Knowledge Base

**Via Dashboard:**

```bash
# Visit http://localhost:3000
# Click "Upload Document" and select files
```

**Via API:**

```bash
make upload-doc DOC=runbook.pdf
```

**Via Command Line:**

```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@runbook.pdf"
```

### Search Documents

**Via Dashboard:**

```bash
# Visit http://localhost:3000/search
# Enter your search query
```

**Via Command Line:**

```bash
make search-docs QUERY="pod crash loop"
```

### Send Test Alert

```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alert_name": "TestAlert",
    "severity": "warning",
    "message": "Test incident",
    "labels": {},
    "annotations": {},
    "firing_condition": "test"
  }'
```

Check Telegram for the analysis result!

---

## 📖 Architecture

```
┌─────────────────────────────────────────────────┐
│  Alert Ingestion (AICA)                         │
│  - Parse alert data                             │
│  - Extract context                              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Knowledge Retrieval (KREA)                     │
│  - Search RAG knowledge base                    │
│  - Retrieve relevant runbooks                   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Root Cause Analysis (RCARA)                    │
│  - Analyze evidence                             │
│  - Identify root cause                          │
│  - Suggest remediation                          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Telegram Notification                          │
│  - Send diagnostic report                       │
│  - Include remediation steps                    │
└─────────────────────────────────────────────────┘
```

---

## 🧪 Testing

### Run All E2E Tests

```bash
make test
```

### Run Specific Scenario

```bash
make test-scenario SCENARIO=scenario_1
```

Tests verify:

- ✅ Alert ingestion and parsing
- ✅ Knowledge base retrieval
- ✅ Root cause identification
- ✅ Remediation suggestions
- ✅ Telegram notifications sent

See [tests/README.md](tests/README.md) for detailed testing documentation.

---

## 🐛 Troubleshooting

**Services not starting?**

```bash
make logs  # Check service logs
make status  # Check service status
```

**Telegram notifications not working?**

- Check `config.yaml` telegram settings
- Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set
- Test bot with: `/start` message in Telegram

**Knowledge base empty?**

- Upload documents via dashboard (<http://localhost:3000>)
- Or use: `make upload-doc DOC=your-file.pdf`

**Tests failing?**

- Ensure all environment variables are set
- Upload relevant documents first
- Check logs: `make logs`

---

## 🛑 Stop & Cleanup

```bash
# Stop services
make stop

# Clean cache
make clean

# Clean all data (WARNING: Deletes knowledge base!)
make clean-data
```

---

## 📊 System Status

```bash
make status
```

Shows:

- Running services
- Health check status
- API availability

---

## 🔧 Development

### Start in Development Mode

```bash
make dev
```

Runs backend with hot reload and dashboard in dev mode.

### Run Locally (without Docker)

```bash
python run.py
```

### Code Quality

```bash
make lint    # Run linters
make format  # Format code
```

---

## 📝 Project Structure

```
opssage/
├── config.yaml              # Main configuration
├── run.py                   # Entry point
├── docker-compose.yml       # Docker services
├── Makefile                 # Common commands
│
├── sages/                   # Core agent system
│   ├── orchestrator.py      # Multi-agent coordinator
│   ├── subagents/           # AICA, KREA, RCARA
│   ├── rag/                 # Knowledge base system
│   ├── notifications.py     # Telegram integration
│   └── config.py            # Configuration loader
│
├── apis/                    # FastAPI server
│   ├── main.py              # API endpoints
│   └── documents.py         # Document management
│
├── dashboard/               # React web UI
│   └── src/
│       ├── pages/
│       │   ├── Documents.tsx    # Document management
│       │   └── Search.tsx       # Document search
│       └── components/
│
├── tests/                   # E2E test scenarios
│   ├── test_scenarios.py    # Scenario definitions
│   └── test_e2e_scenarios.py # Test implementation
│
└── scripts/                 # Utility scripts
    └── run_e2e_tests.py     # Test runner
```

---

## 🤝 Contributing

This is a simplified, production-ready version focused on two use cases:

1. Production incident response with Telegram notifications
2. E2E testing with realistic scenarios

Keep it simple!

---

## 📄 License

MIT License - See LICENSE file for details

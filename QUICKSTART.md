# Quick Start

**This guide has moved!**

Please see **[GETTING_STARTED.md](GETTING_STARTED.md)** for complete setup instructions.

---

## TL;DR

```bash
# Install dependencies
uv sync

# Configure
cp env.example .env
# Edit .env with your Google Cloud credentials

# Start backend
source .venv/bin/activate
uvicorn apis.main:app --reload

# Start dashboard (separate terminal)
cd dashboard
npm install && npm run dev
```

**Full guide:** [GETTING_STARTED.md](GETTING_STARTED.md)

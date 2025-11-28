# Documentation Guide

## Overview

The OpsSage documentation has been completely reorganized for clarity and ease of use. This guide explains the new structure and how to find what you need.

---

## New Documentation Structure

### Main Entry Points

Start here based on what you want to do:

```
📘 README.md
   └─ What is OpsSage? Quick overview and links

📗 GETTING_STARTED.md
   └─ How do I install and run it? Step-by-step setup

📙 USER_GUIDE.md
   └─ How do I use it? Complete usage guide

📕 CHANGELOG.md
   └─ What's changed? Version history
```

### Technical Documentation (docs/)

```
docs/
├── 📄 README.md              Navigation guide
├── 📄 ARCHITECTURE.md        System design
├── 📄 DEPLOYMENT.md          All deployment options
├── 📄 DEVELOPER_GUIDE.md     Contributing & extending
├── 📄 KNOWLEDGE_BASE.md      Knowledge base management
└── 📁 archive/               Historical docs
```

---

## What Changed?

### ✨ New Documents

| Document | Purpose |
|----------|---------|
| `GETTING_STARTED.md` | Comprehensive setup guide (replaces old QUICKSTART.md) |
| `USER_GUIDE.md` | Complete usage guide for all features |
| `CHANGELOG.md` | Version history and feature implementations |
| `docs/DEPLOYMENT.md` | Unified deployment guide (consolidates Docker Compose + Kubernetes) |
| `docs/KNOWLEDGE_BASE.md` | Knowledge base guide (cleaner than old RAG_GUIDE.md) |
| `docs/README.md` | Documentation navigation |

### ♻️ Reorganized Documents

| Old Location | New Location | Changes |
|--------------|--------------|---------|
| `README.md` | `README.md` | Completely rewritten - cleaner, easier to understand |
| `QUICKSTART.md` | `GETTING_STARTED.md` | Expanded with more details and troubleshooting |
| `docs/DOCKER_COMPOSE_GUIDE.md` | `docs/DEPLOYMENT.md` | Consolidated into unified deployment guide |
| `docs/KIND_GUIDE.md` | `docs/DEPLOYMENT.md` | Consolidated into unified deployment guide |
| `docs/RAG_GUIDE.md` | `docs/KNOWLEDGE_BASE.md` | Rewritten with better structure |

### 🗄️ Archived Documents

Moved to `docs/archive/` for reference:

- `DASHBOARD_IMPLEMENTATION.md` → Consolidated into CHANGELOG.md
- `DOCKER_KIND_IMPLEMENTATION.md` → Consolidated into CHANGELOG.md
- `MIGRATION_SUMMARY.md` → Consolidated into CHANGELOG.md
- `RAG_IMPLEMENTATION.md` → Consolidated into CHANGELOG.md
- `docs/API_REFACTORING.md` → Historical info
- `docs/DOCKER_COMPOSE_GUIDE.md` → Superseded by DEPLOYMENT.md
- `docs/KIND_GUIDE.md` → Superseded by DEPLOYMENT.md
- `docs/RAG_GUIDE.md` → Superseded by KNOWLEDGE_BASE.md

---

## How to Navigate

### I'm New to OpsSage

**Start here:**
1. Read [README.md](README.md) - 5 minutes
2. Follow [GETTING_STARTED.md](GETTING_STARTED.md) - 15 minutes
3. Try [USER_GUIDE.md](USER_GUIDE.md) examples - 30 minutes

**You'll be up and running in under an hour!**

### I Want to Use OpsSage

**Primary guide:** [USER_GUIDE.md](USER_GUIDE.md)

Quick links:
- [Submit an alert](USER_GUIDE.md#managing-alerts)
- [View incidents](USER_GUIDE.md#working-with-incidents)
- [Upload documentation](USER_GUIDE.md#knowledge-base)
- [Search knowledge base](USER_GUIDE.md#searching)
- [API usage](USER_GUIDE.md#api-usage)

### I Want to Deploy OpsSage

**Primary guide:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

Choose your deployment:
- [Local development](docs/DEPLOYMENT.md#local-development) - 2 min
- [Docker Compose](docs/DEPLOYMENT.md#docker-compose) - 5 min
- [Kubernetes (Kind)](docs/DEPLOYMENT.md#kubernetes-with-kind) - 10 min
- [Production Kubernetes](docs/DEPLOYMENT.md#production-kubernetes) - 30 min

### I Want to Understand How It Works

**Primary guide:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

Learn about:
- Multi-agent system
- Message contracts
- Tool adapters
- RAG pipeline
- API design

### I Want to Contribute

**Primary guide:** [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)

Topics:
- Development setup
- Running tests
- Adding agents
- Adding tools
- Code style

### I Want to Build a Knowledge Base

**Primary guide:** [docs/KNOWLEDGE_BASE.md](docs/KNOWLEDGE_BASE.md)

Learn:
- Upload documents
- Organize content
- Search semantically
- Best practices
- Maintenance

---

## Quick Reference

### Common Questions

**Q: How do I get started?**
A: [GETTING_STARTED.md](GETTING_STARTED.md)

**Q: How do I submit an alert?**
A: [USER_GUIDE.md - Managing Alerts](USER_GUIDE.md#managing-alerts)

**Q: How do I deploy to Kubernetes?**
A: [docs/DEPLOYMENT.md - Kubernetes](docs/DEPLOYMENT.md#production-kubernetes)

**Q: How does the system work?**
A: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

**Q: How do I add documentation?**
A: [docs/KNOWLEDGE_BASE.md - Adding Documents](docs/KNOWLEDGE_BASE.md#adding-documents)

**Q: Where are the API docs?**
A: http://localhost:8000/docs (when running) or [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

### By Role

**User / SRE:**
1. [GETTING_STARTED.md](GETTING_STARTED.md)
2. [USER_GUIDE.md](USER_GUIDE.md)
3. [docs/KNOWLEDGE_BASE.md](docs/KNOWLEDGE_BASE.md)

**DevOps / Platform Engineer:**
1. [GETTING_STARTED.md](GETTING_STARTED.md)
2. [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
3. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

**Developer:**
1. [GETTING_STARTED.md](GETTING_STARTED.md)
2. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)

---

## Documentation Principles

The new documentation follows these principles:

### 1. **Progressive Disclosure**
Start simple, add detail progressively. README → Getting Started → User Guide → Technical Docs

### 2. **Task-Oriented**
Organized by what you want to accomplish, not by component.

### 3. **Clear Examples**
Every concept has a working example.

### 4. **No Redundancy**
Information appears once, in the most logical place.

### 5. **Easy Navigation**
Clear table of contents, cross-references, and quick links.

---

## File Organization

```
opssage/
│
├── 📘 README.md                    # Project overview (start here!)
├── 📗 GETTING_STARTED.md          # Installation & setup
├── 📙 USER_GUIDE.md               # How to use OpsSage
├── 📕 CHANGELOG.md                # Version history
├── 📄 QUICKSTART.md               # Quick redirect to GETTING_STARTED
├── 📄 DOCUMENTATION_GUIDE.md      # This file
│
├── 📁 docs/                       # Technical documentation
│   ├── 📄 README.md              # Docs navigation
│   ├── 📄 ARCHITECTURE.md        # System design
│   ├── 📄 DEPLOYMENT.md          # Deployment guide
│   ├── 📄 DEVELOPER_GUIDE.md     # Development guide
│   ├── 📄 KNOWLEDGE_BASE.md      # Knowledge base guide
│   │
│   └── 📁 archive/               # Historical docs
│       ├── DASHBOARD_IMPLEMENTATION.md
│       ├── DOCKER_KIND_IMPLEMENTATION.md
│       ├── MIGRATION_SUMMARY.md
│       ├── RAG_IMPLEMENTATION.md
│       ├── API_REFACTORING.md
│       ├── DOCKER_COMPOSE_GUIDE.md
│       ├── KIND_GUIDE.md
│       └── RAG_GUIDE.md
│
├── 📁 sages/                      # Source code
├── 📁 apis/                       # API code
├── 📁 dashboard/                  # React UI
├── 📁 deploy/                     # Deployment configs
└── 📁 tests/                      # Tests
```

---

## What's in Each Document?

### README.md
- What is OpsSage?
- Quick example
- How it works
- 5-minute setup
- Key features
- Deployment options
- Project structure

### GETTING_STARTED.md
- Detailed prerequisites
- Step-by-step installation
- Configuration guide
- Starting the system (3 options)
- First alert walkthrough
- Troubleshooting
- Testing guide

### USER_GUIDE.md
- Web dashboard usage
- Managing alerts
- Working with incidents
- Knowledge base operations
- API usage
- Integration examples
- Best practices

### CHANGELOG.md
- Version history
- Features added by version
- Migration guides
- Breaking changes

### docs/ARCHITECTURE.md
- System design
- Agent architecture
- Message contracts
- Tool adapters
- RAG pipeline
- Data flow

### docs/DEPLOYMENT.md
- Local development
- Docker Compose
- Kubernetes (Kind)
- Production Kubernetes
- Configuration
- Monitoring
- Troubleshooting

### docs/DEVELOPER_GUIDE.md
- Development setup
- Code organization
- Testing
- Adding agents
- Adding tools
- Contributing guidelines

### docs/KNOWLEDGE_BASE.md
- What is the knowledge base?
- Adding documents
- Searching
- Best practices
- Maintenance
- How it works

---

## Tips for Reading

### First Time Users

**Day 1:**
1. Read README.md (5 min)
2. Follow GETTING_STARTED.md (30 min)
3. Submit your first alert (5 min)

**Day 2:**
1. Read USER_GUIDE.md (1 hour)
2. Upload some documentation (15 min)
3. Experiment with features (1 hour)

**Week 1:**
1. Read docs/ARCHITECTURE.md (understand the system)
2. Read docs/DEPLOYMENT.md (prepare for deployment)
3. Set up in your environment

### Experienced Users

Jump directly to what you need:
- **USER_GUIDE.md** for feature details
- **docs/DEPLOYMENT.md** for deployment
- **docs/KNOWLEDGE_BASE.md** for knowledge base
- **docs/DEVELOPER_GUIDE.md** for extending

### Contributors

Read in this order:
1. README.md
2. docs/ARCHITECTURE.md
3. docs/DEVELOPER_GUIDE.md
4. Source code

---

## Finding Information

### Use the Search Function

Most text editors and GitHub have search:
- **VS Code**: Cmd+Shift+F (search in all files)
- **GitHub**: Use the search bar
- **grep**: `grep -r "keyword" docs/`

### Follow the Links

All documents are cross-referenced with links. Click through to related topics.

### Check the Index

Each major document has a table of contents at the top.

### Still Can't Find It?

1. Check [docs/README.md](docs/README.md)
2. Search GitHub issues
3. Ask in GitHub Discussions
4. Open a new issue to improve docs

---

## Feedback Welcome!

Found the documentation helpful? Have suggestions?

- **Typos/errors**: Open a pull request
- **Missing info**: Open an issue
- **Unclear sections**: Let us know
- **Ideas**: Share in Discussions

---

**Happy reading! 📖**

The documentation is here to help you succeed with OpsSage. If something isn't clear, that's a bug in the docs - please let us know!

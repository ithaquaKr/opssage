# OpsSage Documentation

Welcome to the OpsSage documentation! This directory contains technical guides and reference materials.

---

## Documentation Structure

### Getting Started

Start here if you're new to OpsSage:

1. **[Main README](../README.md)** - Project overview
2. **[GETTING_STARTED.md](../GETTING_STARTED.md)** - Installation and setup
3. **[USER_GUIDE.md](../USER_GUIDE.md)** - How to use OpsSage

### Technical Guides

Deep dives into specific topics:

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and components
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Contributing and extending
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - All deployment options
- **[KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md)** - Managing the knowledge base

### Reference

- **[CHANGELOG.md](../CHANGELOG.md)** - Version history and changes
- **[API Documentation](http://localhost:8000/docs)** - Interactive API reference (when running)

---

## Quick Links

### For Users

- **[How do I get started?](../GETTING_STARTED.md)**
- **[How do I submit an alert?](../USER_GUIDE.md#managing-alerts)**
- **[How do I upload documentation?](KNOWLEDGE_BASE.md#adding-documents)**
- **[How do I search the knowledge base?](KNOWLEDGE_BASE.md#searching)**

### For Operators

- **[How do I deploy with Docker Compose?](DEPLOYMENT.md#docker-compose)**
- **[How do I deploy to Kubernetes?](DEPLOYMENT.md#production-kubernetes)**
- **[How do I configure monitoring?](DEPLOYMENT.md#monitoring)**
- **[How do I troubleshoot issues?](DEPLOYMENT.md#troubleshooting)**

### For Developers

- **[How does the system work?](ARCHITECTURE.md)**
- **[How do I add a new agent?](DEVELOPER_GUIDE.md)**
- **[How do I add a new tool?](DEVELOPER_GUIDE.md)**
- **[How do I run tests?](DEVELOPER_GUIDE.md)**

---

## Documentation Map

```
opssage/
├── README.md                    # Start here!
├── GETTING_STARTED.md          # Setup guide
├── USER_GUIDE.md               # Usage guide
├── CHANGELOG.md                # Version history
│
└── docs/
    ├── README.md               # This file
    ├── ARCHITECTURE.md         # System design
    ├── DEVELOPER_GUIDE.md      # Development guide
    ├── DEPLOYMENT.md           # Deployment options
    └── KNOWLEDGE_BASE.md       # Knowledge base guide
```

---

## By Use Case

### I want to...

#### Learn About OpsSage
→ Start with [Main README](../README.md)

#### Install and Run It
→ Follow [GETTING_STARTED.md](../GETTING_STARTED.md)

#### Use the System
→ Read [USER_GUIDE.md](../USER_GUIDE.md)

#### Deploy to Production
→ See [DEPLOYMENT.md](DEPLOYMENT.md)

#### Understand How It Works
→ Read [ARCHITECTURE.md](ARCHITECTURE.md)

#### Contribute Code
→ Check [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

#### Build a Knowledge Base
→ Follow [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md)

---

## Additional Resources

### External Links

- **[Google ADK Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-builder)** - Agent Development Kit docs
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** - API framework
- **[ChromaDB Documentation](https://docs.trychroma.com/)** - Vector database
- **[React Documentation](https://react.dev/)** - UI framework

### Community

- **GitHub Issues**: [Report bugs or request features](https://github.com/ithaquaKr/opssage/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/ithaquaKr/opssage/discussions)

---

## Document Versioning

All documentation is versioned with the codebase. The docs you're reading correspond to the version checked out in git.

To see documentation for a specific version:

```bash
# Checkout a specific version
git checkout v0.4.0

# View docs for that version
cat docs/README.md
```

---

## Contributing to Documentation

Found a typo? Want to improve a guide?

1. Edit the markdown file
2. Submit a pull request
3. Follow the documentation style guide (see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md))

---

## Archived Documentation

Historical implementation summaries and old guides are in `docs/archive/`:

- Migration summaries
- Implementation details
- Superseded guides

These are kept for reference but aren't actively maintained.

---

**Happy Learning! 📚**

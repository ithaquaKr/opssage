.PHONY: help setup dev build test clean docker-up docker-down kind-setup kind-deploy kind-teardown lint format

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo '$(BLUE)OpsSage - Multi-Agent Incident Analysis System$(NC)'
	@echo ''
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

setup: ## Initial project setup
	@echo '$(BLUE)Setting up development environment...$(NC)'
	@./scripts/dev-setup.sh

dev: ## Start local development servers
	@echo '$(BLUE)Starting local development servers...$(NC)'
	@echo 'Backend: http://localhost:8000'
	@echo 'Dashboard: http://localhost:3000'
	@trap 'kill 0' SIGINT; \
	(cd dashboard && npm run dev) & \
	uvicorn apis.main:app --reload

build: ## Build Docker images
	@echo '$(BLUE)Building Docker images...$(NC)'
	docker-compose build

test: ## Run tests
	@echo '$(BLUE)Running tests...$(NC)'
	@source .venv/bin/activate && pytest tests/ -v

test-rag: ## Test RAG pipeline
	@echo '$(BLUE)Testing RAG pipeline...$(NC)'
	@python scripts/test_rag.py

lint: ## Run linters
	@echo '$(BLUE)Running linters...$(NC)'
	@source .venv/bin/activate && \
	ruff check sages apis tests && \
	mypy sages

format: ## Format code
	@echo '$(BLUE)Formatting code...$(NC)'
	@source .venv/bin/activate && \
	ruff format sages apis tests

clean: ## Clean up build artifacts
	@echo '$(BLUE)Cleaning up...$(NC)'
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/
	@echo '$(GREEN)Clean complete$(NC)'

# Docker Compose targets
docker-up: ## Start services with Docker Compose
	@echo '$(BLUE)Starting Docker Compose services...$(NC)'
	docker-compose up -d
	@echo '$(GREEN)Services started$(NC)'
	@echo 'Backend:   http://localhost:8000'
	@echo 'Dashboard: http://localhost:3000'
	@echo 'Grafana:   http://localhost:3001'
	@echo ''
	@echo 'View logs: make docker-logs'

docker-down: ## Stop Docker Compose services
	@echo '$(BLUE)Stopping Docker Compose services...$(NC)'
	docker-compose down

docker-logs: ## View Docker Compose logs
	docker-compose logs -f

docker-restart: ## Restart Docker Compose services
	@echo '$(BLUE)Restarting services...$(NC)'
	docker-compose restart

docker-clean: ## Stop services and remove volumes
	@echo '$(YELLOW)Warning: This will delete all data$(NC)'
	@read -p "Continue? [y/N]: " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo '$(GREEN)Services stopped and volumes removed$(NC)'; \
	fi

# Kind (Kubernetes) targets
kind-setup: ## Create Kind cluster
	@echo '$(BLUE)Setting up Kind cluster...$(NC)'
	@./scripts/kind-setup.sh

kind-deploy: ## Deploy to Kind cluster
	@echo '$(BLUE)Deploying to Kind cluster...$(NC)'
	@./scripts/kind-deploy.sh

kind-teardown: ## Delete Kind cluster
	@echo '$(BLUE)Tearing down Kind cluster...$(NC)'
	@./scripts/kind-teardown.sh

kind-logs: ## View Kubernetes logs
	kubectl logs -f -n opssage -l app=opssage-backend

kind-status: ## Show Kind cluster status
	@echo '$(BLUE)Cluster Status:$(NC)'
	@kind get clusters
	@echo ''
	@kubectl get nodes
	@echo ''
	@kubectl get all -n opssage

# Database targets
db-backup: ## Backup ChromaDB data
	@echo '$(BLUE)Backing up ChromaDB...$(NC)'
	@mkdir -p backups
	@docker run --rm \
		-v opssage_chromadb-data:/data \
		-v $(PWD)/backups:/backup \
		alpine tar czf /backup/chromadb-$(shell date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@echo '$(GREEN)Backup complete$(NC)'

db-restore: ## Restore ChromaDB data (specify BACKUP=filename)
	@if [ -z "$(BACKUP)" ]; then \
		echo '$(RED)Error: Please specify BACKUP=filename$(NC)'; \
		echo 'Example: make db-restore BACKUP=chromadb-20240115-120000.tar.gz'; \
		exit 1; \
	fi
	@echo '$(BLUE)Restoring ChromaDB from $(BACKUP)...$(NC)'
	@docker run --rm \
		-v opssage_chromadb-data:/data \
		-v $(PWD)/backups:/backup \
		alpine tar xzf /backup/$(BACKUP) -C /data
	@echo '$(GREEN)Restore complete$(NC)'

# Documentation
docs-serve: ## Serve documentation locally
	@echo '$(BLUE)Starting documentation server...$(NC)'
	@echo 'Available at: http://localhost:8080'
	@python -m http.server 8080 --directory docs

# Install targets
install-deps: ## Install all dependencies
	@echo '$(BLUE)Installing Python dependencies...$(NC)'
	@uv pip install -r pyproject.toml
	@echo '$(BLUE)Installing Dashboard dependencies...$(NC)'
	@cd dashboard && npm install
	@echo '$(GREEN)Dependencies installed$(NC)'

install-dev: ## Install development tools
	@echo '$(BLUE)Installing development tools...$(NC)'
	@pip install uv ruff mypy pytest pytest-cov
	@echo '$(GREEN)Development tools installed$(NC)'

# Quick actions
run: docker-up ## Quick start with Docker Compose

stop: docker-down ## Quick stop Docker Compose

restart: docker-restart ## Quick restart Docker Compose

status: ## Show system status
	@echo '$(BLUE)=== System Status ===$(NC)'
	@echo ''
	@echo '$(BLUE)Docker Compose Services:$(NC)'
	@docker-compose ps 2>/dev/null || echo 'Not running'
	@echo ''
	@echo '$(BLUE)Kind Clusters:$(NC)'
	@kind get clusters 2>/dev/null || echo 'No clusters'
	@echo ''
	@if kind get clusters 2>/dev/null | grep -q opssage-cluster; then \
		echo '$(BLUE)Kubernetes Pods:$(NC)'; \
		kubectl get pods -n opssage 2>/dev/null || echo 'Namespace not found'; \
	fi

# Version info
version: ## Show version information
	@echo 'OpsSage v0.1.0'
	@echo ''
	@echo 'Tool versions:'
	@echo -n 'Python: ' && python --version 2>&1
	@echo -n 'Docker: ' && docker --version 2>&1
	@echo -n 'Docker Compose: ' && (docker-compose --version 2>&1 || docker compose version 2>&1)
	@if command -v kind >/dev/null 2>&1; then echo -n 'Kind: ' && kind version 2>&1; fi
	@if command -v kubectl >/dev/null 2>&1; then echo -n 'kubectl: ' && kubectl version --client --short 2>&1 || kubectl version --client 2>&1; fi
	@if command -v node >/dev/null 2>&1; then echo -n 'Node: ' && node --version 2>&1; fi

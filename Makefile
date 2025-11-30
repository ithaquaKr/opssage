.PHONY: help install start stop logs test clean

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@printf '$(BLUE)OpsSage - Multi-Agent Incident Response System$(NC)\n'
	@printf '\n'
	@printf '$(GREEN)Quick Start:$(NC)\n'
	@printf '  1. Set environment variables:\n'
	@printf '     export GEMINI_API_KEY="your-key"\n'
	@printf '     export TELEGRAM_BOT_TOKEN="your-token"\n'
	@printf '     export TELEGRAM_CHAT_ID="your-chat-id"\n'
	@printf '  2. Run: make start\n'
	@printf '  3. Access dashboard: http://localhost:3000\n'
	@printf '\n'
	@printf '$(GREEN)Available Commands:$(NC)\n'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Install dependencies
	@printf '$(BLUE)Installing dependencies...$(NC)\n'
	@if ! command -v uv >/dev/null 2>&1; then \
		printf '$(YELLOW)Installing uv...$(NC)\n'; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	@uv pip install -e .
	@cd dashboard && pnpm install
	@printf '$(GREEN)✓ Dependencies installed$(NC)\n'

start: ## Start the system with Docker Compose
	@printf '$(BLUE)Starting OpsSage...$(NC)\n'
	@if [ ! -f config.yaml ]; then \
		printf '$(YELLOW)Creating config.yaml from example...$(NC)\n'; \
		cp config.example.yaml config.yaml; \
	fi
	@docker-compose up -d
	@printf '\n'
	@printf '$(GREEN)✓ OpsSage is running!$(NC)\n'
	@printf '\n'
	@printf '  📊 Dashboard:  http://localhost:3000\n'
	@printf '  📚 API Docs:   http://localhost:8000/docs\n'
	@printf '  🗄️  ChromaDB:   http://localhost:8001\n'
	@printf '\n'
	@printf 'View logs: make logs\n'
	@printf 'Stop system: make stop\n'

start-local: ## Start backend locally (for development)
	@printf '$(BLUE)Starting OpsSage locally...$(NC)\n'
	@if [ ! -f config.yaml ]; then \
		printf '$(RED)Error: config.yaml not found$(NC)\n'; \
		printf 'Run: cp config.example.yaml config.yaml\n'; \
		exit 1; \
	fi
	@python run.py

stop: ## Stop all services
	@printf '$(BLUE)Stopping OpsSage...$(NC)\n'
	@docker-compose down
	@printf '$(GREEN)✓ Services stopped$(NC)\n'

logs: ## View service logs
	@docker-compose logs -f

restart: ## Restart all services
	@printf '$(BLUE)Restarting OpsSage...$(NC)\n'
	@docker-compose restart
	@printf '$(GREEN)✓ Services restarted$(NC)\n'

test: ## Run E2E tests
	@printf '$(BLUE)Running E2E tests...$(NC)\n'
	@printf '\n'
	@printf '$(YELLOW)📱 Check your Telegram for test notifications!$(NC)\n'
	@printf '\n'
	@pytest tests/test_e2e_scenarios.py -v -s
	@printf '\n'
	@printf '$(GREEN)✓ Tests complete$(NC)\n'

test-scenario: ## Run specific test scenario (use SCENARIO=scenario_1)
	@if [ -z "$(SCENARIO)" ]; then \
		printf '$(RED)Error: Please specify SCENARIO$(NC)\n'; \
		printf 'Example: make test-scenario SCENARIO=scenario_1\n'; \
		exit 1; \
	fi
	@printf '$(BLUE)Running scenario: $(SCENARIO)$(NC)\n'
	@python scripts/run_e2e_tests.py --scenario $(SCENARIO) --verbose

upload-doc: ## Upload document to knowledge base (use DOC=path/to/file)
	@if [ -z "$(DOC)" ]; then \
		printf '$(RED)Error: Please specify DOC=path/to/file$(NC)\n'; \
		printf 'Example: make upload-doc DOC=runbook.pdf\n'; \
		exit 1; \
	fi
	@printf '$(BLUE)Uploading document: $(DOC)$(NC)\n'
	@curl -X POST http://localhost:8000/api/v1/documents \
		-F "file=@$(DOC)" \
		-H "Accept: application/json"
	@printf '\n'
	@printf '$(GREEN)✓ Document uploaded$(NC)\n'

search-docs: ## Search knowledge base (use QUERY="your search")
	@if [ -z "$(QUERY)" ]; then \
		printf '$(RED)Error: Please specify QUERY$(NC)\n'; \
		printf 'Example: make search-docs QUERY="pod crash loop"\n'; \
		exit 1; \
	fi
	@printf '$(BLUE)Searching for: $(QUERY)$(NC)\n'
	@curl -X GET "http://localhost:8000/api/v1/documents/search?q=$(QUERY)&limit=5" \
		-H "Accept: application/json" | python -m json.tool
	@printf '\n'

clean: ## Clean up cache and temporary files
	@printf '$(BLUE)Cleaning up...$(NC)\n'
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -path "*/dashboard/node_modules" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/
	@printf '$(GREEN)✓ Cleanup complete$(NC)\n'

clean-data: ## Clean up data and volumes (WARNING: Deletes all knowledge base data!)
	@printf '$(RED)⚠️  WARNING: This will delete all data!$(NC)\n'
	@read -p "Continue? [y/N]: " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		rm -rf data/chromadb; \
		printf '$(GREEN)✓ Data cleaned$(NC)\n'; \
	else \
		echo 'Cancelled'; \
	fi

status: ## Show system status
	@printf '$(BLUE)=== OpsSage System Status ===$(NC)\n'
	@printf '\n'
	@printf '$(BLUE)Services:$(NC)\n'
	@docker-compose ps 2>/dev/null || echo '  Not running (use: make start)'
	@printf '\n'
	@printf '$(BLUE)Health:$(NC)\n'
	@curl -s http://localhost:8000/api/v1/health 2>/dev/null | python -m json.tool 2>/dev/null || echo '  Backend: Offline'
	@printf '\n'

build: ## Build Docker images
	@printf '$(BLUE)Building Docker images...$(NC)\n'
	@docker-compose build
	@printf '$(GREEN)✓ Build complete$(NC)\n'

lint: ## Run code linters
	@printf '$(BLUE)Running linters...$(NC)\n'
	@ruff check sages apis tests
	@mypy sages

format: ## Format code
	@printf '$(BLUE)Formatting code...$(NC)\n'
	@ruff format sages apis tests
	@printf '$(GREEN)✓ Code formatted$(NC)\n'

dev: ## Start development environment
	@printf '$(BLUE)Starting development environment...$(NC)\n'
	@printf 'Backend: http://localhost:8000\n'
	@printf 'Dashboard: http://localhost:3000\n'
	@trap 'kill 0' SIGINT; \
	(cd dashboard && pnpm run dev) & \
	python run.py

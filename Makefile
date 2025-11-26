.PHONY: help install test lint format clean run docker-build docker-run deploy

help:  ## Show this help message
	@echo "OpsSage - Multi-Agent Incident Analysis & Remediation System"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync --all-extras

install-dev:  ## Install development dependencies
	uv sync --all-extras
	uv run pre-commit install

test:  ## Run tests
	uv run pytest tests/ -v

test-cov:  ## Run tests with coverage
	uv run pytest tests/ -v --cov=sages --cov-report=html --cov-report=term

lint:  ## Run linters
	uv run ruff check sages tests
	uv run mypy sages
	uv run codespell

format:  ## Format code
	uv run ruff format sages tests
	uv run ruff check --fix sages tests

clean:  ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

run:  ## Run the API server locally
	uv run uvicorn sages.api:app --reload --log-level info

run-prod:  ## Run the API server in production mode
	uv run uvicorn sages.api:app --host 0.0.0.0 --port 8000 --workers 4

docker-build:  ## Build Docker image
	docker build -t opssage:latest .

docker-build-dev:  ## Build development Docker image
	docker build -f docker/Dockerfile.dev -t opssage:dev .

docker-run:  ## Run Docker container
	docker run -p 8000:8000 --env-file .env opssage:latest

docker-run-dev:  ## Run development Docker container
	docker run -p 8000:8000 -v $(PWD):/app --env-file .env opssage:dev

# Kubernetes and Helm targets
helm-install:  ## Install with Helm
	helm install opssage ./deploy/helm

helm-upgrade:  ## Upgrade Helm release
	helm upgrade opssage ./deploy/helm

helm-uninstall:  ## Uninstall Helm release
	helm uninstall opssage

helm-template:  ## Generate Helm templates
	helm template opssage ./deploy/helm

# CI targets
ci-lint:  ## Run CI linting checks
	uv run ruff check sages tests
	uv run ruff format --check sages tests
	uv run mypy sages
	uv run codespell

ci-test:  ## Run CI tests
	uv run pytest tests/ -v --cov=sages --cov-report=xml --cov-report=term

ci-build:  ## Build for CI
	docker build -t opssage:test .

# Development utilities
dev-reset:  ## Reset development environment
	rm -rf .venv uv.lock
	uv sync --all-extras

dev-shell:  ## Start development shell
	uv run python

docs-serve:  ## Serve documentation locally
	@echo "Documentation is in docs/ directory"
	@echo "README: cat README.md"

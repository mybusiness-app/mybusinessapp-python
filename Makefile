.PHONY: check-prereqs setup dev test build deploy clean help create-sp

SHELL := /bin/bash

help: ## Show this help message
	@echo 'Usage:'
	@echo '  make <target>'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-prereqs: ## Check prerequisites
	@chmod +x scripts/check_prerequisites.sh
	@./scripts/check_prerequisites.sh

create-sp: ## Create Azure service principal and update environment variables
	@chmod +x scripts/create_service_principal.sh
	@./scripts/create_service_principal.sh

setup: check-prereqs ## Setup development environment
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

dev: ## Start development environment
	docker compose -f docker/compose/dev.yml up

dev-build: ## Start development environment with rebuild
	docker compose -f docker/compose/dev.yml up --build

test: ## Run all tests
	pytest tests/

test-unit: ## Run unit tests only
	pytest tests/unit/

test-integration: ## Run integration tests only
	pytest tests/integration/

deploy: ## Deploy to Azure
	@chmod +x scripts/deploy.sh
	@./scripts/deploy.sh

clean: ## Clean up development environment
	docker compose -f docker/compose/dev.yml down -v
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/

format: ## Format code using black
	black .

lint: ## Run linting
	flake8 .
	mypy .

update-deps: ## Update dependencies
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements-dev.in
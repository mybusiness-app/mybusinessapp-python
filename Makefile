.PHONY: check-prereqs setup compose-up compose-build chainlit-build chainlit-tag chainlit-push test test-unit test-integration deploy clean format lint update-deps

SHELL := /bin/bash
REGISTRY := crmppsharedsouthafricanorth.azurecr.io

help: ## Show this help message
	@echo 'Usage:'
	@echo '  make <target>'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-prereqs: ## Check prerequisites
	@chmod +x scripts/check_prerequisites.sh
	@./scripts/check_prerequisites.sh

create-service-principal: ## Create a service principal
	@chmod +x scripts/create_service_principal.sh
	@./scripts/create_service_principal.sh

setup: check-prereqs ## Setup development environment
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

setup-prod: check-prereqs ## Setup production environment
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh --environment production

compose-up: ## Run the docker compose (development)
	docker compose -f docker/compose/dev.yml up

compose-build: ## Build docker compose (development)
	docker compose -f docker/compose/dev.yml build

chainlit-build: ## Build the chainlit app using docker
	docker build --no-cache -f docker/chainlit/Dockerfile -t mybusiness-app-chainlit .

chainlit-run: ## Run the chainlit app
	docker run --env-file .env.development -it mybusiness-app-chainlit

chainlit-tag: ## Tag the chainlit app to Azure Container Registry
	# Prompt for a version string
	@read -p "Enter version tag: " TAG; \
	docker image tag mybusiness-app-chainlit $(REGISTRY)/web-apps/mpp-chainlit:$$TAG

chainlit-push: ## Push the chainlit app to Azure Container Registry
	# Prompt for a version string
	@read -p "Enter version tag: " TAG; \
	docker image push $(REGISTRY)/web-apps/mpp-chainlit:$$TAG

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
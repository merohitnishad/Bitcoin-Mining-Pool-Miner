# Variables
PYTHON := python3
PIP := pip3
VENV := venv
IMAGE_NAME := block_miner
CONTAINER_NAME := block_miner
DOCKER_COMPOSE_FILE := docker-compose.yml

# Default target
.DEFAULT_GOAL := help

# Install dependencies and set up virtual environment
install: ## Create virtual environment and install dependencies
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/$(PIP) install --upgrade pip
	$(VENV)/bin/$(PIP) install -r requirements.txt

# Run the Python application
run: ## Run the Python application
	$(VENV)/bin/$(PYTHON) main.py

# Format code using black
format: ## Format code using black
	$(VENV)/bin/$(PIP) install black
	$(VENV)/bin/black .

# Remove virtual environment and temporary files
clean: ## Clean the project (remove venv, __pycache__ etc.)
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +

# Show available commands
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Build Docker image
docker-build: ## Build the Docker image
	docker build -t $(IMAGE_NAME) .

# Run the Docker container
docker-run: ## Run the Docker container
	docker run --rm -it -v ${PWD}/.env:/app/.env --name $(CONTAINER_NAME) $(IMAGE_NAME)

# Start services using Docker Compose
docker-compose-up: ## Start services using Docker Compose
	docker-compose -f $(DOCKER_COMPOSE_FILE) up --build -d

# Stop services using Docker Compose
docker-compose-down: ## Stop services using Docker Compose
	docker-compose -f $(DOCKER_COMPOSE_FILE) down

# Freeze dependencies into requirements.txt
freeze: ## Freeze installed dependencies to requirements.txt
	$(VENV)/bin/$(PIP) freeze > requirements.txt
DOCKER_COMPOSE_FILE := docker-compose.yml


# Start services using Docker Compose
run: ## Start services using Docker Compose
	docker-compose -f $(DOCKER_COMPOSE_FILE) up  --build -d

# Stop services using Docker Compose
stop: ## Stop services using Docker Compose
	docker-compose -f $(DOCKER_COMPOSE_FILE) down --volumes
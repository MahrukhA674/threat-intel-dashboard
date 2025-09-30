# Makefile for Threat Intelligence Dashboard

# Default environment file
ENV_FILE=.env

# Build all services
build:
	docker-compose --env-file $(ENV_FILE) up --build -d

# Stop all services
stop:
	docker-compose down

# Run tests inside backend container
test:
	docker-compose exec backend pytest

# Run specific test file
test-file:
	docker-compose exec backend pytest tests/test_db.py

# View logs
logs:
	docker-compose logs -f backend

# Rebuild backend only
rebuild-backend:
	docker-compose build backend

# Restart backend container
restart-backend:
	docker-compose restart backend

# Shell into backend container
shell:
	docker-compose exec backend /bin/sh

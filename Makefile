.PHONY: setup up down test lint migrate shell logs seed clean

# ------------------------------------------------------------------
# Privacyops-Platform  —  developer commands
# ------------------------------------------------------------------
# Non-standard ports (won't clash with your main projects):
#   API       → 8700
#   Postgres  → 5700
#   Redis     → 6700
#   Grafana   → 3702
#   Prometheus→ 9700
#   Tempo     → 4700/3700
#   Loki      → 3701
#   Flower    → 5701
#   Ollama    → 11700
# ------------------------------------------------------------------

# Full project build from scratch after git clone
setup:
	@echo ">>> Copying env file..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo ">>> Building Docker images..."
	docker compose build
	@echo ">>> Starting infrastructure..."
	docker compose up -d postgres redis
	@echo ">>> Waiting for Postgres to become healthy..."
	@sleep 10
	@echo ">>> Running Alembic migrations..."
	docker compose run --rm api alembic upgrade head
	@echo ">>> Starting all services..."
	docker compose up -d
	@echo ""
	@echo "=== Setup complete ==="
	@echo "API:        http://localhost:8700/docs"
	@echo "Grafana:    http://localhost:3702"
	@echo "Flower:     http://localhost:5701"
	@echo "Prometheus: http://localhost:9700"

# Run full test suite
test:
	docker compose run --rm -e APP_ENV=test api python -m pytest tests/ -v --tb=short

# Start all containers
up:
	docker compose up -d
	@echo ""
	@echo "API:        http://localhost:8700/docs"
	@echo "Grafana:    http://localhost:3702"
	@echo "Flower:     http://localhost:5701"

# Stop all containers
down:
	docker compose down

# Run linter
lint:
	docker compose run --rm api python -m ruff check src/ tests/
	docker compose run --rm api python -m ruff format --check src/ tests/
	docker compose run --rm api python -m mypy src/

# Run Alembic migration
migrate:
	docker compose run --rm api alembic upgrade head

# Open shell inside api container
shell:
	docker compose run --rm api sh

# Tail application logs
logs:
	docker compose logs -f api worker

# Tear down everything including volumes
clean:
	docker compose down -v --remove-orphans
	@echo "Volumes and containers removed."

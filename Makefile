include .env
export

DC = docker-compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env

.PHONY: start db-start db-down db-logs db-connect db-shell

# TODO: Удалить - это лишнее
run:
	uv run uvicorn src.main:app --reload --host $(HOST) --port $(PORT)

db-start:
	@echo "Создание контейнера $(DB_CONTAINER)..."
	$(DC) -f $(STORAGES_FILE) $(ENV) up -d --build

db-down:
	@echo "Отключение контейнера $(DB_CONTAINER)..."
	$(DC) -f $(STORAGES_FILE) $(ENV) down

db-logs:
	$(LOGS) -f $(DB_CONTAINER) -f

db-connect:
	@echo "Подключение к БД как $(DB_USER)..."
	$(EXEC) $(DB_CONTAINER) psql -U $(DB_USER)

db-shell:
	$(EXEC) $(DB_CONTAINER) sh

.PHONY: dev-up dev-down dev-logs dev-migrate prod-up prod-down prod-logs prod-migrate

# --- Разработка (hot-reload, код монтируется с хоста) ---
dev-up:
	$(DC) -f docker-compose.dev.yml $(ENV) up -d --build

dev-down:
	$(DC) -f docker-compose.dev.yml $(ENV) down

dev-logs:
	$(DC) -f docker-compose.dev.yml logs -f app

dev-migrate:
	$(DC) -f docker-compose.dev.yml $(ENV) run --rm migrate

# --- Продакшен ---
prod-up:
	$(DC) -f docker-compose.yml $(ENV) up -d --build

prod-down:
	$(DC) -f docker-compose.yml $(ENV) down

prod-logs:
	$(DC) -f docker-compose.yml logs -f app

prod-migrate:
	$(DC) -f docker-compose.yml $(ENV) run --rm migrate

include .env
export

DC = docker-compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env


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


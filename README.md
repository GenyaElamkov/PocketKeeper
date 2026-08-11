# PocketKeeper API

Backend-сервис семейного финансового трекера **PocketKeeper**: учёт счетов, категорий и транзакций, аналитика по расходам/доходам и JWT-аутентификация с восстановлением пароля по email.

Построен на **FastAPI** + **PostgreSQL**, полностью контейнеризован и готов к продакшен-развёртыванию через Docker.

> Frontend (Vue.js SPA) разрабатывается в отдельном репозитории https://github.com/GenyaElamkov/finance-frontend и обращается к этому API по адресу, указанному в `CORS_ALLOW_ORIGINS`.

> Production в отдельном репозитории https://github.com/GenyaElamkov/finance-infra

---

## Содержание

- [Возможности](#возможности)
- [Стек технологий](#стек-технологий)
- [Структура проекта](#структура-проекта)
- [Быстрый старт](#быстрый-старт)
- [Переменные окружения](#переменные-окружения)
- [Миграции базы данных](#миграции-базы-данных)
- [API и документация](#api-и-документация)
- [Полезные команды](#полезные-команды)
- [Разработка](#разработка)

---

## Возможности

- 🔐 **Аутентификация** — регистрация, вход по логину/паролю, JWT access/refresh токены, восстановление пароля по email
- 👤 **Пользователи** — профиль, смена пароля, список пользователей (для администрирования)
- 💳 **Счета** — создание, редактирование, удаление счетов с балансом и валютой
- 🏷 **Категории** — древовидные категории доходов/расходов (с вложенностью)
- 💸 **Транзакции** — учёт доходов/расходов с привязкой к счёту и категории
- 📊 **Аналитика** — отчёты по месяцам и годам
- 🛡 **Безопасность** — security-заголовки, rate limiting, строгий CORS, хэширование паролей (Argon2/bcrypt)
- 📝 **Логирование** — структурированные логи через loguru с ротацией и хранением в volume
- 🩺 **Health-check** — эндпоинт для Docker healthcheck / балансировщика

## Стек технологий

| Категория      | Технология                                   |
|-----------------|-----------------------------------------------|
| Язык / рантайм  | Python 3.14                                   |
| Фреймворк       | FastAPI                                       |
| База данных     | PostgreSQL 17 + SQLAlchemy 2.0 (async, asyncpg) |
| Миграции        | Alembic                                       |
| Аутентификация  | JWT (PyJWT), pwdlib (Argon2), bcrypt          |
| Rate limiting   | slowapi                                       |
| Логирование     | loguru                                        |
| Почта           | aiosmtplib                                    |
| Пакетный менеджер | uv                                           |
| Контейнеризация | Docker, Docker Compose (multi-stage build)    |
| Веб-сервер      | Uvicorn                                       |

## Структура проекта

```
PocketKeeper/
├── src/
│   ├── api/v1/           # HTTP-роутеры (auth, users, accounts, categories, transactions, analytics, health)
│   ├── application/      # Фабрика FastAPI-приложения, middleware
│   ├── core/              # Конфиг, подключение к БД, security (JWT, пароли), зависимости
│   ├── infrastructure/    # Логирование, rate limiter, security headers, email
│   ├── models/            # SQLAlchemy-модели
│   ├── repositories/      # Слой доступа к данным
│   ├── schemas/           # Pydantic-схемы (DTO)
│   ├── services/          # Бизнес-логика
│   └── main.py            # Точка входа приложения
├── alembic/                # Миграции базы данных
├── logs/                   # Логи приложения (bind mount)
├── Dockerfile              # Multi-stage: development / production
├── docker-compose.yml      # Продакшен-стек
├── docker-compose.dev.yml  # Dev-стек с hot-reload
├── Makefile                # Команды для dev-окружения
├── .env.example             # Шаблон переменных окружения
└── pyproject.toml
```

## Быстрый старт

### Docker

**Требования:** Docker и Docker Compose.

1. Клонируйте репозиторий:

   ```bash
   git clone git@github.com:GenyaElamkov/PocketKeeper.git
   cd PocketKeeper
   ```

2. Создайте `.env` из шаблона и заполните значения (см. [переменные окружения](#переменные-окружения)):

   ```bash
   cp .env.example .env
   ```

3. **Для разработки**:

   ```bash
   make dev-up
   ```

   Применить миграции в dev-режиме:

   ```bash
   make dev-migrate
   ```

   Посмотреть логи:

   ```bash
   make dev-logs
   ```

   Остановить:

   ```bash
   make dev-down
   ```


После старта API будет доступен на `http://localhost:8000`.


## Переменные окружения

Полный шаблон — в `.env.example`. Ниже основные параметры:

| Переменная            | Описание                                              | Пример / значение по умолчанию   |
|------------------------|--------------------------------------------------------|-----------------------------------|
| `ENVIRONMENT`          | Окружение (`development` / `production`)                | `development`                     |
| `HOST`, `PORT`         | Адрес и порт сервера приложения                         | `127.0.0.1`, `8000`                |
| `DB_HOST`, `DB_PORT`   | Хост и порт PostgreSQL                                   | `localhost`, `5432`                |
| `DB_USER`, `DB_PASSWORD` | Учётные данные БД                                     | —                                  |
| `POSTGRES_DB`          | Имя базы данных                                         | —                                  |
| `SECRET_KEY`           | Секрет для подписи JWT                                   | — (обязательно задать)            |
| `SMTP_HOST`, `SMTP_PORT` | Настройки SMTP для отправки писем (сброс пароля)       | `smtp.gmail.com`, `587`            |
| `SMTP_USERNAME`, `SMTP_PASSWORD` | Учётные данные почтового ящика                  | —                                  |
| `SMTP_FROM_EMAIL`, `SMTP_FROM_NAME` | Отправитель писем                             | —                                  |
| `CORS_ALLOW_ORIGINS`   | Список разрешённых источников (JSON-массив)              | `["http://localhost:5173"]`        |
| `LOG_LEVEL`            | Уровень логирования                                      | `INFO`                             |
| `DB_ECHO`              | Логировать SQL-запросы SQLAlchemy                        | `False`                            |


## Миграции базы данных

Миграции описаны в `alembic/migrations` и управляются через Alembic.

```bash
# Создать новую миграцию (локально)
uv run alembic revision --autogenerate -m "описание изменений"

# Применить миграции
uv run alembic upgrade head

# Откатить последнюю миграцию
uv run alembic downgrade -1
```

В Docker-окружении для этого есть `make dev-migrate`
## API и документация

После запуска в режиме `development` доступна интерактивная документация:

- Swagger UI — `http://localhost:8000/docs`
- ReDoc — `http://localhost:8000/redoc`
- OpenAPI-схема — `http://localhost:8000/openapi.json`

> В режиме `production` документация отключена (`docs_url=None`).

Основные группы эндпоинтов (префикс `/api/v1`):

| Группа | Эндпоинты |
|--------|-----------|
| Auth | `POST /auth/register`, `POST /auth/token`, `POST /auth/refresh-token`, `POST /auth/refresh-access-token`, `POST /auth/forgot-password`, `POST /auth/reset-password` |
| Users | `GET /users/`, `GET /users/me`, `PATCH /users/me`, `PATCH /users/change-password`, `DELETE /users/{user_id}` |
| Accounts | `GET /accounts/`, `POST /accounts/`, `PUT /accounts/{id}`, `DELETE /accounts/{id}` |
| Categories | `GET /categories/`, `POST /categories/`, `PUT /categories/{id}`, `DELETE /categories/{id}` |
| Transactions | `GET /transactions/`, `POST /transactions/`, `PUT /transactions/{id}`, `DELETE /transactions/{id}` |
| Health | `GET /health/` |

## Полезные команды

| Команда | Описание |
|---------|----------|
| `make dev-up` | Поднять dev-стек (с пересборкой) |
| `make dev-down` | Остановить dev-стек |
| `make dev-logs` | Логи контейнера приложения (dev) |
| `make dev-migrate` | Применить миграции в dev-окружении |

## Разработка

Проект использует `pre-commit` и `flake8` для проверки качества кода. Перед коммитом установите хуки:

```bash
uv sync --extra dev
uv run pre-commit install
```

Архитектура следует слоистому подходу: **API (роутеры) → Services (бизнес-логика) → Repositories (доступ к данным) → Models (SQLAlchemy)**, с отдельным слоем **Schemas** для входных/выходных Pydantic-моделей.

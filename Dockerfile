############################
# Base — общий слой с uv
############################
FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /uvx /usr/local/bin/

############################
# Builder — компиляция зависимостей (build-essential нужен
# только здесь, в финальный production-образ он не попадает)
############################
FROM base AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

############################
# Development
############################
FROM builder AS development

# Ставим и dev-зависимости (pre-commit и т.д.)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --extra dev --no-install-project

COPY . .

EXPOSE 8000

# Код монтируется volume'ом из docker-compose.dev.yml, поэтому --reload
# подхватывает изменения без пересборки образа
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

############################
# Production
############################
FROM python:3.14-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --system --create-home --home-dir /home/app --shell /usr/sbin/nologin app

# Готовое виртуальное окружение из builder-стадии — без компиляторов
COPY --from=builder /app/.venv /app/.venv
COPY --chown=app:app . .

RUN mkdir -p logs && chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl --fail http://127.0.0.1:8000/api/v1/health/ || exit 1

# uv в production-образе нет — venv уже собран, uvicorn запускается напрямую
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

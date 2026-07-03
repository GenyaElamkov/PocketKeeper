from time import perf_counter

from fastapi import Request
from loguru import logger

logger.remove()
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    retention="30 days",
    rotation="1 day",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
    serialize=True,
    level="INFO",
    encoding="utf-8",
)


async def log_requests_middleware(request: Request, call_next):
    """Middleware для логирования запросов."""
    start_time = perf_counter()
    response = await call_next(request)
    duration_ms = (perf_counter() - start_time) * 1000

    logger.info({
        "event": "request",
        "request_path": str(request.url.path),
        "method": request.method,
        "status_code": response.status_code,
        "duration_ms": f"{duration_ms:.2f}",
    })
    return response

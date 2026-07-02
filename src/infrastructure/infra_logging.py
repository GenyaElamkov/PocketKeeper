from time import perf_counter, time

from fastapi import Request
from loguru import logger

logger.remove()
logger.add(
    f"logs/file{time()}.log",
    retention="10 days",
    compression="zip",
    format="{message}",
    serialize=True,
    level="INFO",
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

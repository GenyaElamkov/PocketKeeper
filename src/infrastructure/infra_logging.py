from time import perf_counter

from fastapi import Request
from loguru import logger

from src.core.config import settings

logger.remove()
logger.add(
    f"{settings.log.path}/{settings.log.name}",
    retention=settings.log.retention,
    rotation=settings.log.rotation,
    compression=settings.log.compression,
    format=settings.log.log_format,
    serialize=settings.log.serialization,
    level=settings.log.level,
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

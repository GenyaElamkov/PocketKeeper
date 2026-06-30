from time import perf_counter

from fastapi import Request
from loguru import logger


async def log_requests_middleware(request: Request, call_next):
    """Middleware для логирования запросов."""
    start_time = perf_counter()
    response = await call_next(request)
    duration_ms = (perf_counter() - start_time) * 1000

    logger.info(
        f"request_path={request.url.path} "
        f"method={request.method} "
        f"status_code={response.status_code} "
        f"process_time_ms={duration_ms:.2f}",
    )
    return response

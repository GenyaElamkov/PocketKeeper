from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Здоровье приложения"],
)


@router.get(
        "/",
        name="Проверка работоспособности сервера",
        summary="Проверка сервера",
        description="Базовая проверка работоспособности приложения",
        response_description="Работоспособность сервера",
)
async def health_check():
    """
    Базовая проверка здоровья приложения.
    Используется для Docker healthcheck и load balancer checks.
    """
    return {
        "status": "healthy",
        "service": "pocketkeeper-api",
        "version": "1.0.0",
    }

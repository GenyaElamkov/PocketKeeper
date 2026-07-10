from src.schemas.error import ErrorResponse

UNAUTHORIZED = {
    401: {
        "description": "Не авторизован",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "detail": "Could not validate credentials",
                },
            },
        },
    },
}

RATE_LIMIT = {
    429: {
        "description": "Слишком много запросов",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "detail": "Too many requests. Please try again later.",
                },
            },
        },
    },
}

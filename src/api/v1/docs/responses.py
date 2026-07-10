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

INVAIID_REFRESH_TOKEN_RESPONSES = {
    401: {
        "description": "Невалидный или просроченный refresh-токен",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "Неверный токен или срок истёк"},
            },
        },
    },
}

CONFLICT = {
    409: {
        "description": "Пользователь с таким email уже существует",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "User with this email already exists"},
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

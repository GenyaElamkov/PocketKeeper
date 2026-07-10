from src.schemas.error import ErrorResponse


def bad_request_response(detail: str = "Invalid request data") -> dict:
    return {
        400: {
            "description": "Некорректный запрос.",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": detail},
                },
            },
        },
    }


def unauthorized_response(detail: str = "Could not validate credentials") -> dict:
    return {
        401: {
            "description": "Не авторизован. Отсутствует или невалидный токен.",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": detail},
                },
            },
        },
    }


def forbidden_response(detail: str = "You don't have enough permissions") -> dict:
    return {
        403: {
            "description": "Недостаточно прав для выполнения операции.",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": detail},
                },
            },
        },
    }


def not_found_response(resource: str = "Resource") -> dict:
    detail = f"{resource} not found"
    return {
        404: {
            "description": f"{resource} не найден.",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": detail},
                },
            },
        },
    }


def conflict_response(detail: str = "Conflict occurred") -> dict:
    return {
        409: {
            "description": "Конфликт данных.",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": detail},
                },
            },
        },
    }


def too_many_requests_response(detail: str = "Too many requests. Please try again later.") -> dict:
    return {
        429: {
            "description": "Слишком много запросов.",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": detail},
                },
            },
        },
    }

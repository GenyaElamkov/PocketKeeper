from src.api.v1.docs.responses import (CONFLICT,
                                       INVAIID_REFRESH_TOKEN_RESPONSES,
                                       RATE_LIMIT, UNAUTHORIZED)
from src.schemas.error import ErrorResponse

CREATE_USER_RESPONSES = {
    **CONFLICT,
    **RATE_LIMIT,
}

LOGIN_RESPONSES = {
    **UNAUTHORIZED,
    **RATE_LIMIT,
}

REFRESH_TOKEN_RESPONSES = {
    **RATE_LIMIT,
    **INVAIID_REFRESH_TOKEN_RESPONSES,
}

REFRESH_ACCESS_TOKEN_RESPONSES = {
    **RATE_LIMIT,
    **INVAIID_REFRESH_TOKEN_RESPONSES,
}

FORGOT_PASSWORD_RESPONSES = {
    **RATE_LIMIT,
}

RESET_PASSWORD_RESPONSES = {
    **RATE_LIMIT,
    401: {
        "description": "Невалидный или просроченный reset-токен",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "Неверный токен или срок истёк"},
            },
        },
    },
}

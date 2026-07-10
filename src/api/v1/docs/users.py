from src.api.v1.docs.responses import CONFLICT, RATE_LIMIT, UNAUTHORIZED
from src.schemas.error import ErrorResponse

GET_ALL_USERS_RESPONSES = {
    **RATE_LIMIT,
    403: {
        "description": "Недостаточно прав (требуется роль admin)",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "You don't have enough permissions"},
            },
        },
    },
}


GET_CURRENT_USER_RESPONSES = {
    **UNAUTHORIZED,
    **RATE_LIMIT,
}


UPDATE_PROFILE_USER_RESPONSE = {
    **UNAUTHORIZED,
    **CONFLICT,
    **RATE_LIMIT,
}

UPDATE_PASSWORD_USER_RESPONSES = {
    **UNAUTHORIZED,
    **RATE_LIMIT,
    400: {
        "description": "Старый пароль указан неверно",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "Old password is incorrect"},
            },
        },
    },
}


DELETE_USER_RESPONSES = {
    **UNAUTHORIZED,
    **RATE_LIMIT,
    403: {
        "description": "Нет прав на удаление другого пользователя (если не админ)",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "You can't delete another user"},
            },
        },
    },
    404: {
        "description": "Пользователь не найден",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "User not found"},
            },
        },
    },
}

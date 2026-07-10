from src.api.v1.docs.responses import (conflict_response,
                                       too_many_requests_response,
                                       unauthorized_response)

CREATE_USER_RESPONSES = {
    **conflict_response("User with this email already exists"),
    **too_many_requests_response(),
}

LOGIN_RESPONSES = {
    **unauthorized_response(),
    **too_many_requests_response(),
}

REFRESH_TOKEN_RESPONSES = {
    **unauthorized_response("Invalid or expired refresh-token"),
    **too_many_requests_response(),
}

REFRESH_ACCESS_TOKEN_RESPONSES = {
    **unauthorized_response("Invalid or expired refresh-token"),
    **too_many_requests_response(),
}

FORGOT_PASSWORD_RESPONSES = {
    **too_many_requests_response(),
}

RESET_PASSWORD_RESPONSES = {
    **unauthorized_response("Invalid or expired reset-token"),
    **too_many_requests_response(),
}

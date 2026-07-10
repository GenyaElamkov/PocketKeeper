from src.api.v1.docs.responses import (bad_request_response, conflict_response,
                                       forbidden_response, not_found_response,
                                       too_many_requests_response,
                                       unauthorized_response)

GET_ALL_USERS_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response("You do not have sufficient permissions.The 'admin' role is required."),
    **too_many_requests_response(),
}

GET_CURRENT_USER_RESPONSES = {
    **unauthorized_response(),
    **too_many_requests_response(),
}

UPDATE_PROFILE_USER_RESPONSE = {
    **unauthorized_response(),
    **conflict_response("User with this email already exists"),
    **too_many_requests_response(),
}

UPDATE_PASSWORD_USER_RESPONSES = {
    **unauthorized_response(),
    **too_many_requests_response(),
    **bad_request_response("Old password is incorrect"),
}

DELETE_USER_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response("You can't delete another user"),
    **too_many_requests_response(),
    **not_found_response("User"),
}

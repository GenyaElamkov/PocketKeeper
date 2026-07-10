from src.api.v1.docs.responses import (bad_request_response, conflict_response,
                                       forbidden_response, not_found_response,
                                       too_many_requests_response,
                                       unauthorized_response)

GET_ALL_ACCOUNTS_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response(),
    **too_many_requests_response(),
}

CREATE_ACCOUNT_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response(),
    **conflict_response("Account with this name already exists"),
    **too_many_requests_response(),
}

UPDATE_ACCOUNT_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response("You can't update an account for another user"),
    **not_found_response("Account"),
    **bad_request_response("You can't update an account with transactions"),
    **too_many_requests_response(),
}

DELETE_ACCOUNT_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response("You can't update an account for another user"),
    **not_found_response("Account"),
    **bad_request_response("You can't update an account with transactions"),
    **too_many_requests_response(),
}

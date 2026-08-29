from src.api.v1.docs.responses import (bad_request_response,
                                       forbidden_response, not_found_response,
                                       too_many_requests_response,
                                       unauthorized_response)

GET_ALL_TRANSFER_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response(),
    **too_many_requests_response(),
}

CREATE_TRANSFER_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response(),
    **not_found_response("Account"),
    **bad_request_response("You cannot send money between the same accounts."),
    **too_many_requests_response(),
}

DELETE_TRANSFER_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response("You can't delete a transfer for another user"),
    **not_found_response("Transfer"),
    **too_many_requests_response(),
}

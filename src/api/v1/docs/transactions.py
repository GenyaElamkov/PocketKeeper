from src.api.v1.docs.responses import (forbidden_response, not_found_response,
                                       too_many_requests_response,
                                       unauthorized_response)

GET_ALL_TRANSACTIONS_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response(),
    **too_many_requests_response(),
}

CREATE_TRANSACTION_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response(),
    **not_found_response("Account"),
    **not_found_response("Category"),
    **too_many_requests_response(),
}

UPDATE_TRANSACTIONS_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response("You can't update a transaction for another user"),
    **not_found_response("Transaction"),
    **too_many_requests_response(),
}

DELETE_TRANSACTION_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response("You can't delete a transaction for another user"),
    **not_found_response("Transaction"),
    **too_many_requests_response(),
}

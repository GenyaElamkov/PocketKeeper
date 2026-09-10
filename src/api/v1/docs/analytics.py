from src.api.v1.docs.responses import (too_many_requests_response,
                                       unauthorized_response)

GET_CURRENT_USER_RESPONSES = {
    **unauthorized_response(),
    **too_many_requests_response(),
}

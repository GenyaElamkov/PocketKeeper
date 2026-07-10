from src.api.v1.docs.responses import (conflict_response, forbidden_response,
                                       not_found_response,
                                       too_many_requests_response,
                                       unauthorized_response)

READ_CATEGORIES_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response(),
    **too_many_requests_response(),
}

CREATE_CATEGORY_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response("You can't create a category for another user"),
    **not_found_response("Parent category"),
    **conflict_response("Category with this name already exists"),
    **too_many_requests_response(),
}

UPDATE_CATEGORIES_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response("You can't update a category for another user"),
    **not_found_response("Category"),
    **too_many_requests_response(),
}

DELETE_CATEGORIES_RESPONSES = {
    **unauthorized_response(),
    **forbidden_response("You can't delete a category for another user"),
    **not_found_response("Category"),
    **too_many_requests_response(),
}

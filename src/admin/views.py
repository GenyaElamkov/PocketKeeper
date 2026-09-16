from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqladmin import ModelView
from sqladmin.filters import BooleanFilter, StaticValuesFilter
from starlette.requests import Request
from wtforms import SelectField

from src.core.database import async_session_maker
from src.models.users import User
from src.repositories.users import UserRepository
from src.schemas.users import UserRole
from src.services.users import UserService


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    # Просмотр
    column_list = [
        User.id,
        User.email,
        User.full_name,
        User.role,
        User.is_active,
        User.created_at,
    ]
    column_searchable_list = [User.email, User.full_name]
    column_sortable_list = [User.email, User.role, User.is_active, User.created_at]
    column_filters = [
        StaticValuesFilter(User.role, values=[(role.value, role.value) for role in UserRole], title="Role"),
        BooleanFilter(User.is_active, title="Active"),
    ]
    column_default_sort = [("created_at", True)]

    can_create = False
    can_view_details = True

    # Редактирование: доступна только роль.
    can_edit = True
    form_columns = [User.role]
    form_overrides = {"role": SelectField}
    form_args = {
        "role": {
            "choices": [(role.value, role.value) for role in UserRole],
        },
    }

    # Мягкое удаление.
    can_delete = True

    async def delete_model(self, request: Request, pk: Any) -> None:
        admin_user_id = UUID(request.session["admin_user_id"])

        async with async_session_maker() as db:
            user_service = UserService(user_repo=UserRepository(db=db))
            try:
                await user_service.delete_user(
                    user_id=UUID(str(pk)),
                    current_user_id=admin_user_id,
                    role=UserRole.ADMIN,
                )
            except HTTPException as exc:
                if exc.status_code == status.HTTP_404_NOT_FOUND:
                    return
                raise

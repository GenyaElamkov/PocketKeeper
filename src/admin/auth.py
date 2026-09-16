from uuid import UUID

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from src.core.database import async_session_maker
from src.core.security.password import verify_password
from src.repositories.users import UserRepository
from src.schemas.users import UserRole


class AdminAuth(AuthenticationBackend):
    """Аутентификация для панели администратора.

    В админку может войти только активный пользователь с ролью 'admin'.
    Проверка выполняется по тем же данным (email/hashed_password/role),
    что и обычный логин в API — отдельных учётных данных для админки нет.
    """

    async def login(self, request: Request) -> bool:
        form = await request.form()

        email = form.get("username")
        password = form.get("password")

        if not email or not password:
            return False

        async with async_session_maker() as db:
            user = await UserRepository(db=db).get_active_by_email(str(email))

        if user is None or user.role != UserRole.ADMIN:
            return False

        if not verify_password(plane_password=str(password), hashed_password=user.hashed_password):
            return False

        request.session.update({"admin_user_id": str(user.id)})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("admin_user_id")
        if not user_id:
            return False

        async with async_session_maker() as db:
            user = await UserRepository(db=db).get_active_by_id(UUID(user_id))

        # Перепроверяем при каждом запросе: если пользователя деактивировали
        # или сняли роль admin, доступ в панель пропадает немедленно.
        if user is None or user.role != UserRole.ADMIN:
            request.session.clear()
            return False

        return True

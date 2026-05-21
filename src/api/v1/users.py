from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_user_service
from src.models.users import User as UserModel
from src.schemas.users import User as UserSchema
from src.schemas.users import UserCreate as UserCreateSchema
from src.schemas.users import UserList as UserListSchema
from src.schemas.users import UserRequest as UserRequestSchema
from src.schemas.users import UserUpdate as UserUpdateSchema
from src.services.current import get_current_admin, get_current_user
from src.services.users import UserService

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get("/", name="Список пользователей",
            response_model=UserListSchema)
async def get_all_users(
    request: UserRequestSchema = Depends(),
    user_service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_admin),
) -> UserListSchema:
    """Получение списка пользователей, может только 'user' с ролью 'admin'."""
    return await user_service.get_all_users(request)


@router.get("/{user_id}",
            name="Пользователь",
            response_model=UserSchema)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_user),
) -> UserSchema:
    """Получение пользователя по ID."""
    return await user_service.get_user_by_id(current_user_id=current_user.id, user_id=user_id)


@router.post("/", name="Создать пользователя",
             response_model=UserSchema,
             status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreateSchema,
    user_service: UserService = Depends(get_user_service),
) -> UserSchema:
    """Создание пользователя."""
    return await user_service.create_user(user)


@router.put("/{user_id}",
            name="Обновить пользователя",
            response_model=UserSchema)
async def update_user(
    user_id: int,
    user: UserUpdateSchema,
    user_service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_user),
) -> UserSchema:
    """Обновление пользователя."""
    return await user_service.update_user(
        user_id=user_id,
        current_user_id=current_user.id,
        user=user)


@router.delete("/{user_id}",
               name="Удалить пользователя",
               response_model=UserSchema,
               status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_user),
) -> UserSchema:
    """Удаление пользователя. Удалить пользователя может 'admin' или сам пользователь."""
    return await user_service.delete_user(user_id, current_user.id, current_user.role)

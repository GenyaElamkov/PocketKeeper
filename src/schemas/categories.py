from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    """
    Схема для создания категории
    """
    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Название категории (от 3 до 50 символов)",
    )
    icon: str | None = Field(
        None,
        description="Ссылка на иконку категории (опционально)",
        max_length=200,
    )
    parent_id: int | None = Field(
        None,
        description="Идентификатор родительской категории (опционально)",
    )


class Category(CategoryCreate):
    """
    Схема для представления категории
    """
    id: int = Field(..., description="Уникальный идентификатор категории")    # noqa
    is_active: bool = Field(..., description="Активна ли категория")

    model_config = ConfigDict(from_attributes=True)


class CategoryUpdate(BaseModel):
    """
    Схема для обновления категории
    """
    name: str | None = Field(
        None,
        min_length=3,
        max_length=50,
        description="Название категории (от 3 до 50 символов)",
    )
    icon: str | None = Field(
        None,
        description="Ссылка на иконку категории (опционально)",
        max_length=200,
    )
    parent_id: int | None = Field(
        None,
        description="Идентификатор родительской категории (опционально)",
    )

    is_active: bool | None = Field(
        None,
        description="Активна ли категория",
    )


class CategoryList(BaseModel):
    """Схема для списка категорий."""
    items: list[Category] = Field(..., description="Список категорий")
    total: int = Field(ge=0, description="Общее количество категорий")
    page: int = Field(ge=1, description="Номер страницы")
    page_size: int = Field(ge=1, description="Количество элементов на странице")

    model_config = ConfigDict(from_attributes=True)


class CategoryRequest(BaseModel):
    """Схема для фильтрации категорий."""
    page: int = Field(ge=1, default=1, description="Номер страницы")
    page_size: int = Field(ge=1, le=100, default=20, description="Количество элементов на странице")
    category_id: int | None = Field(None, description="Название категории")

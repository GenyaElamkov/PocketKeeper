import uuid
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict



class CategoryType(str, Enum):
    income = "расходы"
    expense = "доходы"


class CategoryCreate(BaseModel):
    """
    Модель для создания категории
    """
    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Название категории (от 3 до 50 символов)",
    )
    type: CategoryType = Field(
        ...,
        description="Тип категории (доходы или расходы)",
    )
    icon: str | None = Field(
        None,
        description="Ссылка на иконку категории (опционально)",
    )
    parent_id: uuid.UUID | None = Field(
        None,
        description="Идентификатор родительской категории (опционально)",
    )


class Category(CategoryCreate):
    """
    Модель для представления категории
    """
    id: str

    model_config = ConfigDict(from_attributes=True)
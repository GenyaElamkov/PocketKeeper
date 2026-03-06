import uuid
from pydantic import BaseModel, Field, ConfigDict



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
    icon: str | None = Field(
        None,
        description="Ссылка на иконку категории (опционально)", 
        max_length=200,
    )
    parent_id: uuid.UUID | None = Field(
        None,
        description="Идентификатор родительской категории (опционально)",
    )


class Category(CategoryCreate):
    """
    Модель для представления категории
    """
    id: uuid.UUID = Field(..., description="Уникальный идентификатор категории")

    model_config = ConfigDict(from_attributes=True)
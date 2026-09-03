from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# Входная схема для создания пользователя
class UserCreate(BaseModel):
    username: str = Field(
        min_length= 3,
        max_length= 50,
    )
    password: str = Field(
        min_length= 6,
        max_length= 128,
    )

class UserPublic(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)

# Входная схема для создания заметки
class NoteCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    content: str = Field(
        min_length=1,
    )

# Выходная схема заметки
class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    owner_id: int

    model_config = ConfigDict(from_attributes=True)



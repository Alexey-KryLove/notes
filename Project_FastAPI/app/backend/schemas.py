from pydantic import BaseModel
from datetime import datetime


# Входная схема для создания пользователя
class UserCreate(BaseModel):
    username: str # только имя, без пароля на этом шаге
    password: str


class UserPublic(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


# # Выходная схема пользователя (что отдаём наружу)
# class UserOut(BaseModel):
#     id: int
#     username: str
#
#     class Config:
#         from_attributes = True # позволяет строить схему прямо из ORM-объекта


# Входная схема для создания заметки
class NoteCreate(BaseModel):
    title: str
    content: str
    created_at: datetime
    owner_id: int # id владельца заметки


# Выходная схема заметки
class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True


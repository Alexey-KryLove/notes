from typing import List
from sqlalchemy import String, Integer, Text, ForeignKey, Column, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from .db import Base


# Модель пользователя — таблица users
class User(Base):
    __tablename__ = "users" # имя таблицы в БД

    # id — первичный ключ (уникальный идентификатор записи)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # username — имя пользователя, должно быть уникальным и не NULL
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    # Связь «один-ко-многим»: у пользователя может быть много заметок
    # back_populates связывает это поле с полем Note.owner
    notes: Mapped[List["Note"]] = relationship(back_populates="owner")


# Модель заметки — таблица notes
class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Заголовок заметки (может быть пустым — но оставим как строку)
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # Текст заметки — тип Text для длинного содержания
    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Внешний ключ на users.id (владелец заметки)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Обратная связь к пользователю (Note → User)
    owner: Mapped[User] = relationship(back_populates="notes")
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .models import User, Note
from .db import AsyncSession


# Создать пользователя с уникальным username
async def create_user(session: AsyncSession, username: str) -> User:
    user = User(username=username) # создаём ORM-объект (пока без id)
    session.add(user) # помечаем объект на вставку
    try:
        await session.commit() # отправляем INSERT в БД
    except IntegrityError: # ловим нарушение уникальности и др. ошибки целостности
        await session.rollback() # откатываем транзакцию
        raise # пробрасываем дальше — обработаем в endpoint
    await session.refresh(user) # обновляем объект (получаем сгенерированный id)
    return user


# Создать заметку для владельца owner_id
async def create_note(session: AsyncSession, owner_id: int, title: str, content: str) -> Note:
    note = Note(title=title, content=content, owner_id=owner_id)
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


# Получить все заметки пользователя
async def get_user_notes(session: AsyncSession, owner_id: int) -> list[Note]:
    stmt = select(Note).where(Note.owner_id == owner_id) # SELECT * FROM notes WHERE owner_id = :owner_id
    result = await session.execute(stmt) # выполняем запрос
    return result.scalars().all() # вытаскиваем список ORM-объектов
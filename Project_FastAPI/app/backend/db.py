import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase

# Загружаем переменные окружения
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# Базовый класс моделей
class Base(DeclarativeBase):
    pass

# Асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

# Dependency FastAPI
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Инициализация БД
async def init_db() -> None:
    from . import models
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

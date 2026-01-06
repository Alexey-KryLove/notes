# Импортируем os для чтения переменных окружения (.env)
import os
# Загружаем переменные из .env файла
from dotenv import load_dotenv
load_dotenv()
# Импорты из асинхронной SQLAlchemy 2.0
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase



# Создаём базовый класс, от которого будут наследоваться модели
class Base(DeclarativeBase):
    pass

# Читаем строку подключения к БД из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL",)

# Создаём асинхронный движок (engine) — это «ворота» в БД
engine = create_async_engine(DATABASE_URL, echo=True)# включаем SQL-логирование в консоль, полезно новичку

# Фабрика асинхронных сессий — через неё получаем объекты Session для запросов
AsyncSessionLocal = async_sessionmaker(bind=engine,expire_on_commit=False)


# Зависимость FastAPI: отдаём сессию, а по окончании запроса — закрываем

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session # отдаём наружу активную сессию; после — контекст закроет её


# Создаём таблицы по описаниям моделей (вызывать на старте приложения)
async def init_db() -> None:
    from . import models # noqa: F401 (импорт важен побочным эффектом)
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
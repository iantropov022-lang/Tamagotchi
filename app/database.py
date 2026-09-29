from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем АСИНХРОННЫЙ движок
engine = create_async_engine(
    DATABASE_URL,
    echo=True, # Поставь True, если хочешь видеть все SQL-запросы в консоли (полезно для дебага)
)

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Базовый класс для моделей
Base = declarative_base()

# Асинхронная зависимость для FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
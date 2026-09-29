import asyncio
from sqlalchemy import select
from app.database import engine, Base, AsyncSessionLocal
from app.models import Pet


async def init_db():
    # 1. Создаем таблицы
    async with engine.begin() as conn:
        # run_sync нужен, чтобы выполнить синхронный метод create_all в асинхронном контексте
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы в Postgres созданы/проверены.")

    # 2. Добавляем питомца
    async with AsyncSessionLocal() as db:
        # В асинхронном SQLAlchemy используем select()
        result = await db.execute(select(Pet).limit(1))
        existing_pet = result.scalars().first()

        if not existing_pet:
            new_pet = Pet(
                name="Барсик",
                hunger=100,
                happiness=100,
                energy=100,
                is_sleeping=False
            )
            db.add(new_pet)
            await db.commit()
            print("🐱 Питомец 'Барсик' успешно добавлен в Postgres!")
        else:
            print("ℹ️ Питомец уже существует в базе данных.")


if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(init_db())
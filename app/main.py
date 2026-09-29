from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.database import get_db
from app.models import Pet
from app.schemas import PetResponse, ActionResponse

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="Tamagotchi API", version="1.0")


# --- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ (Магия времени) ---
def update_pet_degradation(pet: Pet):
    """
    Считает, сколько времени прошло с последнего обновления,
    и уменьшает статы питомца.
    """
    now = datetime.now()
    time_diff = now - pet.last_updated
    hours_passed = time_diff.total_seconds() / 3600

    # Статы падают на 10 единиц в час
    drop_amount = int(hours_passed * 10)

    if drop_amount > 0:
        pet.hunger = max(0, pet.hunger - drop_amount)
        pet.happiness = max(0, pet.happiness - drop_amount)
        pet.energy = max(0, pet.energy - drop_amount)
        pet.last_updated = now

    return pet


# --- ЭНДПОИНТЫ ---

@app.get("/pet", response_model=PetResponse)
async def get_pet_status(db: AsyncSession = Depends(get_db)):
    """Получить текущее состояние питомца (с учетом деградации)"""

    # Асинхронный запрос к БД
    result = await db.execute(select(Pet).limit(1))
    pet = result.scalars().first()

    if not pet:
        raise HTTPException(status_code=404, detail="Питомец не найден!")

    # Применяем деградацию
    pet = update_pet_degradation(pet)

    # Сохраняем изменения в БД
    await db.commit()
    await db.refresh(pet)

    return pet


@app.post("/pet/feed", response_model=ActionResponse)
async def feed_pet(db: AsyncSession = Depends(get_db)):
    """Покормить питомца"""

    result = await db.execute(select(Pet).limit(1))
    pet = result.scalars().first()

    if not pet:
        raise HTTPException(status_code=404, detail="Питомец не найден!")

    # Сначала считаем деградацию
    pet = update_pet_degradation(pet)

    if pet.is_sleeping:
        raise HTTPException(status_code=400, detail="Тссс! Питомец спит, не буди его!")

    pet.hunger = min(100, pet.hunger + 20)
    pet.energy = max(0, pet.energy - 5)

    await db.commit()
    await db.refresh(pet)

    return {"message": "Ням-ням! Питомец покормлен.", "pet": pet}


@app.post("/pet/play", response_model=ActionResponse)
async def play_with_pet(db: AsyncSession = Depends(get_db)):
    """Поиграть с питомцем"""

    result = await db.execute(select(Pet).limit(1))
    pet = result.scalars().first()

    if not pet:
        raise HTTPException(status_code=404, detail="Питомец не найден!")

    pet = update_pet_degradation(pet)

    if pet.is_sleeping:
        raise HTTPException(status_code=400, detail="Питомец спит!")
    if pet.energy < 15:
        raise HTTPException(status_code=400, detail="Питомец слишком устал, чтобы играть!")

    pet.happiness = min(100, pet.happiness + 20)
    pet.energy = max(0, pet.energy - 15)
    pet.hunger = max(0, pet.hunger - 10)

    await db.commit()
    await db.refresh(pet)

    return {"message": "Ура! Питомец рад.", "pet": pet}


@app.post("/pet/sleep", response_model=ActionResponse)
async def sleep_pet(db: AsyncSession = Depends(get_db)):
    """Уложить питомца спать"""

    result = await db.execute(select(Pet).limit(1))
    pet = result.scalars().first()

    if not pet:
        raise HTTPException(status_code=404, detail="Питомец не найден!")

    pet = update_pet_degradation(pet)

    if pet.is_sleeping:
        raise HTTPException(status_code=400, detail="Он уже спит!")

    pet.is_sleeping = True
    pet.energy = min(100, pet.energy + 30)
    pet.hunger = max(0, pet.hunger - 5)

    await db.commit()
    await db.refresh(pet)

    return {"message": "Zzz... Питомец уснул.", "pet": pet}


@app.post("/pet/wake", response_model=ActionResponse)
async def wake_pet(db: AsyncSession = Depends(get_db)):
    """Разбудить питомца"""

    result = await db.execute(select(Pet).limit(1))
    pet = result.scalars().first()

    if not pet:
        raise HTTPException(status_code=404, detail="Питомец не найден!")

    if not pet.is_sleeping:
        raise HTTPException(status_code=400, detail="Питомец и так не спит!")

    pet.is_sleeping = False

    await db.commit()
    await db.refresh(pet)

    return {"message": "Доброе утро! Питомец проснулся.", "pet": pet}


# --- ФРОНТЕНД ---

# Создаем папку static, если её нет
os.makedirs("static", exist_ok=True)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Отдаем главную страничку с Барсиком"""
    return FileResponse("static/index.html")
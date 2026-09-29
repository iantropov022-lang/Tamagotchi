# Используем официальный образ Python (легкая версия)
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Сначала копируем только requirements для кэширования слоя
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Теперь копируем весь проект
COPY . .

# Открываем порт
EXPOSE 8000

# Запускаем: сначала инициализация БД, потом сервер
CMD ["sh", "-c", "python init_db.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
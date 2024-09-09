# Используем минимальный образ Python
FROM python:3.11-alpine

# Устанавливаем зависимости для работы FastAPI и Uvicorn
RUN apk add --no-cache gcc musl-dev libffi-dev

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements/base.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем все файлы приложения
COPY . .

# Открываем порт для приложения
EXPOSE 8000

# Запускаем FastAPI приложение с Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
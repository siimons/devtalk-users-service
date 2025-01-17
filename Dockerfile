# Указываем базовый образ
FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    musl-dev \
    libffi-dev \
    libc-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Задаём рабочую директорию
WORKDIR /app

# Копируем только requirements.txt для установки зависимостей (для кеширования слоёв)
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Открываем порт
EXPOSE 8000

# Команда запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
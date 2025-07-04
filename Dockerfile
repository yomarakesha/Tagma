FROM python:3.11-slim

# Установим системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Установим рабочую директорию
WORKDIR /app

# Скопируем зависимости и установим их
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Скопируем весь проект
COPY . .

# Откроем порт (если нужно)
EXPOSE 5000

# Переменные окружения для Flask
ENV FLASK_APP=app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Команда запуска
CMD ["flask", "run"]
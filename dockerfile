# Используем официальный Python-образ
FROM python:3.11-alpine3.18 AS builder

# Установим необходимые зависимости для сборки Python-зависимостей
RUN apk add --no-cache \
    build-base \
    postgresql-dev \
    libffi-dev \
    && pip install --upgrade pip

# Копируем зависимости
COPY requirements.txt /app/requirements.txt

# Устанавливаем зависимости в виртуальное окружение
RUN python -m venv /venv \
    && . /venv/bin/activate \
    && pip install --no-cache-dir -r /app/requirements.txt

# Финальный образ
FROM python:3.11-alpine3.18

# Установим runtime-зависимости
RUN apk add --no-cache libpq libffi

# Копируем виртуальное окружение из builder-образа
COPY --from=builder /venv /venv

# Настраиваем переменные окружения
ENV PATH="/venv/bin:$PATH"

# Создаем пользователя и директорию для приложения
RUN getent group www-data || addgroup -g 1000 www-data && \
    adduser -u 1000 -G www-data -s /bin/sh -D www-data && \
    mkdir -p /service/static /service/media && \
    chown -R www-data:www-data /service

# Копируем код приложения
COPY --chown=www-data:www-data service /service

# Переходим в рабочую директорию
WORKDIR /service

# Открываем порт
EXPOSE 8000

# Переключаемся на пользователя
USER www-data

# Команда запуска
CMD ["gunicorn", "service.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
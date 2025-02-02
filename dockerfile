FROM python:3.11-alpine

# Установим необходимые пакеты для сборки и Nginx
RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    libffi-dev \
    nginx \
    && rm -rf /var/cache/apk/*

# Установим зависимости Python
COPY requirements.txt /temp/requirements.txt
RUN pip install --no-cache-dir -r /temp/requirements.txt

# Копируем приложение
COPY service /service
WORKDIR /service

# Создаем пользователя для запуска приложения
RUN adduser --disabled-password service-user
USER service-user

# Открываем порт приложения
EXPOSE 8000

# Команда по умолчанию для запуска Gunicorn
CMD ["gunicorn", "service.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

RUN mkdir -p /service/static && chmod -R 777 /service/static
RUN python manage.py collectstatic --noinput
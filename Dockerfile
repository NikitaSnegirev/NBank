FROM python:3.13-slim-bookworm

# Аргументы сборки (можно переопределять при docker build)
ARG SERVER=http://host.docker.internal:4111/api
ARG API_VERSION=/v1
ARG UI_BASE_URL=http://host.docker.internal:3000

# Переменные окружения внутри контейнера
ENV SERVER=${SERVER}
ENV API_VERSION=${API_VERSION}
ENV UI_BASE_URL=${UI_BASE_URL}
ENV PLAYWRIGHT_TEST_BASE_URL=${UI_BASE_URL}
ENV SWAGGER_COVERAGE_CONFIG_FILE_YAML=/app/swagger_coverage_config.docker.yaml

ENV DB_HOST=host.docker.internal
ENV DB_PORT=5433
ENV DB_NAME=nbank
ENV DB_USERNAME=postgres
ENV DB_PASSWORD=postgres

# Рабочая директория
WORKDIR /app

# Сначала копируем только зависимости — для кеширования
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
RUN set -eux; \
    apt-get update -o Acquire::Retries=3 || \
    apt-get update -o Acquire::Retries=3 -o Acquire::AllowInsecureRepositories=true -o Acquire::AllowDowngradeToInsecureRepositories=true; \
    playwright install-deps; \
    playwright install; \
    rm -rf /var/lib/apt/lists/*

# Копируем весь проект
COPY . .

# На случай проблем с правами
USER root

# Запуск тестов + логирование
CMD ["pytest"]

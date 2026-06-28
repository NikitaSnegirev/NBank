#!/bin/bash

set -e

# Имя локального Docker-образа
IMAGE_NAME="nbank-tests"

# Username в Docker Hub
DOCKERHUB_USERNAME="niko7645"

# Тег образа
TAG="v1"

# Полное имя образа для Docker Hub
DOCKERHUB_IMAGE="${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}"

# Проверяем, что токен передан через переменную окружения
if [ -z "$DOCKERHUB_TOKEN" ]; then
  echo "Ошибка: переменная окружения DOCKERHUB_TOKEN не задана"
  echo "Сначала выполни:"
  echo "export DOCKERHUB_TOKEN=твой_access_token"
  exit 1
fi

echo "Логинимся в Docker Hub..."
echo "$DOCKERHUB_TOKEN" | docker login \
--username "$DOCKERHUB_USERNAME" \
--password-stdin

echo "Тегируем образ..."
docker tag "${IMAGE_NAME}:${TAG}" "$DOCKERHUB_IMAGE"

echo "Пушим образ в Docker Hub..."
docker push "$DOCKERHUB_IMAGE"

echo ""
echo "Готово! Образ загружен в Docker Hub."

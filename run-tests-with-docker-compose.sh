#!/bin/bash

set -Eeuo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker-compose/docker-compose.yaml}"
TEST_IMAGE="${TEST_IMAGE:-nbank-tests:v1}"

APIBASEURL="http://localhost:4111"
UIBASEURL="http://localhost:3000"

cleanup() {
  exit_code=$?

  set +e
  echo
  echo "Останавливаем тестовое окружение..."
  docker compose -f "$COMPOSE_FILE" down -v --remove-orphans

  if [ "$exit_code" -eq 0 ]; then
    echo "Готово: тесты завершились успешно, окружение остановлено."
  else
    echo "Готово: тесты завершились с ошибкой, окружение всё равно остановлено."
  fi

  exit "$exit_code"
}

wait_for_url() {
  service_name="$1"
  url="$2"
  retries="${3:-60}"
  delay_seconds="${4:-2}"

  echo "Ожидаем готовность $service_name: $url"

  for attempt in $(seq 1 "$retries"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "$service_name готов."
      return 0
    fi

    echo "Попытка $attempt/$retries: $service_name ещё не готов..."
    sleep "$delay_seconds"
  done

  echo "Ошибка: $service_name не стал доступен по адресу $url"
  echo "Последние логи окружения:"
  docker compose -f "$COMPOSE_FILE" logs --tail=100
  return 1
}

trap cleanup EXIT

echo "Поднимаем тестовое окружение через Docker Compose..."
docker compose -f "$COMPOSE_FILE" up -d

echo
echo "Проверяем готовность сервисов..."
wait_for_url "Backend API" "$APIBASEURL/actuator/health"
wait_for_url "Frontend UI" "$UIBASEURL"

echo
echo "Запускаем API и UI тесты в контейнере..."
echo "APIBASEURL=$APIBASEURL"
echo "UIBASEURL=$UIBASEURL"
echo "TEST_IMAGE=$TEST_IMAGE"

docker run --rm \
  --network host \
  -e APIBASEURL="$APIBASEURL" \
  -e UIBASEURL="$UIBASEURL" \
  -e UI_BASE_URL="$UIBASEURL" \
  -e PLAYWRIGHT_TEST_BASE_URL="$UIBASEURL" \
  "$TEST_IMAGE" \
  pytest "$@"

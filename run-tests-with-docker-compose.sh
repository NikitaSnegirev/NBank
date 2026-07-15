#!/bin/bash

set -Eeuo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker-compose/docker-compose.yaml}"
COMPOSE_PROJECT="${COMPOSE_PROJECT:-docker-compose}"
TEST_IMAGE="${TEST_IMAGE:-nbank-tests:v1}"

HOST_APIBASEURL="${HOST_APIBASEURL:-http://localhost:4111}"
HOST_UIBASEURL="${HOST_UIBASEURL:-http://localhost:3000}"
APIBASEURL="${APIBASEURL:-http://backend:4111}"
UIBASEURL="${UIBASEURL:-http://frontend}"
FRAUD_ALIAS="${FRAUD_ALIAS:-fraud-mock}"
NETWORK_NAME="${COMPOSE_PROJECT}_nbank-network"

export FRAUD_DETECTION_SERVICE_URL="${FRAUD_DETECTION_SERVICE_URL:-http://${FRAUD_ALIAS}:8080}"

resolve_workspace_dir() {
  if [ -n "${WORKSPACE_DIR:-}" ]; then
    echo "$WORKSPACE_DIR"
  elif command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$(pwd)"
  else
    pwd
  fi
}

WORKSPACE_DIR="$(resolve_workspace_dir)"

cleanup() {
  exit_code=$?

  set +e
  echo
  echo "Останавливаем тестовое окружение..."
  docker compose -p "$COMPOSE_PROJECT" -f "$COMPOSE_FILE" down -v --remove-orphans

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
  docker compose -p "$COMPOSE_PROJECT" -f "$COMPOSE_FILE" logs --tail=100
  return 1
}

trap cleanup EXIT

echo "Поднимаем тестовое окружение через Docker Compose..."
docker compose -p "$COMPOSE_PROJECT" -f "$COMPOSE_FILE" up -d

echo
echo "Проверяем готовность сервисов..."
wait_for_url "Backend API" "$HOST_APIBASEURL/actuator/health"
wait_for_url "Frontend UI" "$HOST_UIBASEURL"

echo
echo "Запускаем API и UI тесты в контейнере..."
echo "APIBASEURL=$APIBASEURL"
echo "UIBASEURL=$UIBASEURL"
echo "FRAUD_DETECTION_SERVICE_URL=$FRAUD_DETECTION_SERVICE_URL"
echo "TEST_IMAGE=$TEST_IMAGE"
echo "WORKSPACE_DIR=$WORKSPACE_DIR"
echo "NETWORK_NAME=$NETWORK_NAME"
echo "FRAUD_ALIAS=$FRAUD_ALIAS"

rm -rf coverage-results
mkdir -p coverage-results/.history

set +e
MSYS_NO_PATHCONV=1 docker run --rm \
  --network "$NETWORK_NAME" \
  --network-alias "$FRAUD_ALIAS" \
  -v "$WORKSPACE_DIR:/app" \
  -w /app \
  -e APIBASEURL="$APIBASEURL" \
  -e UIBASEURL="$UIBASEURL" \
  -e SERVER="$APIBASEURL/api" \
  -e UI_BASE_URL="$UIBASEURL" \
  -e PLAYWRIGHT_TEST_BASE_URL="$UIBASEURL" \
  -e DB_HOST="postgres" \
  -e DB_PORT="5432" \
  -e SWAGGER_COVERAGE_CONFIG_FILE_YAML="/app/swagger_coverage_config.docker.yaml" \
  "$TEST_IMAGE" \
  pytest "$@"
TEST_EXIT_CODE=$?

echo
echo "Генерация Swagger coverage report..."
MSYS_NO_PATHCONV=1 docker run --rm \
  --network "$NETWORK_NAME" \
  -v "$WORKSPACE_DIR:/app" \
  -w /app \
  -e SWAGGER_COVERAGE_CONFIG_FILE_YAML="/app/swagger_coverage_config.docker.yaml" \
  --entrypoint swagger-coverage-tool \
  "$TEST_IMAGE" \
  save-report
REPORT_EXIT_CODE=$?
set -e

if [ "$TEST_EXIT_CODE" -ne 0 ]; then
  exit "$TEST_EXIT_CODE"
fi

exit "$REPORT_EXIT_CODE"

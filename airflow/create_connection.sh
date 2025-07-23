#!/usr/bin/env bash
set -e

CONTAINER_NAME="${CONTAINER_NAME:-airflow-airflow-apiserver-1}"
CONN_ID="${CONN_ID:-pg-docker}"
CONN_TYPE="${CONN_TYPE:-postgres}"
CONN_LOGIN="${CONN_LOGIN:-postgres}"
CONN_PASSWORD="${CONN_PASSWORD:-postgres}"
CONN_HOST="${CONN_HOST:-rdbms-pg-1}"
CONN_SCHEMA="${CONN_SCHEMA:-default}"
CONN_PORT="${CONN_PORT:-5432}"

docker exec "$CONTAINER_NAME" airflow connections delete "$CONN_ID" >/dev/null 2>&1 || true

docker exec "$CONTAINER_NAME" airflow connections add "$CONN_ID" \
  --conn-type "$CONN_TYPE" \
  --conn-login "$CONN_LOGIN" \
  --conn-password "$CONN_PASSWORD" \
  --conn-host "$CONN_HOST" \
  --conn-schema "$CONN_SCHEMA" \
  --conn-port "$CONN_PORT"
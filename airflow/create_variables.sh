#!/usr/bin/env bash
set -e

CONTAINER_NAME="${CONTAINER_NAME:-airflow-airflow-apiserver-1}"
CONN_ID="${CONN_ID:-pg-docker}"
SCHEMA="${SCHEMA:-rsm}"
LANDING_TABLE="${LANDING_TABLE:-properties_landing}"
CLEAN_TABLE="${CLEAN_TABLE:-properties_clean}"

set_variable () {
    var_name="$1"
    var_value="$2"
    docker exec "$CONTAINER_NAME" airflow variables delete "$var_name" >/dev/null 2>&1 || true
    docker exec "$CONTAINER_NAME" airflow variables set "$var_name" "$var_value"
}

set_variable "rsm_web_scraper.rdbms.connection_id" "$CONN_ID"
set_variable "rsm_web_scraper.rdbms.schema" "$SCHEMA"
set_variable "rsm_web_scraper.rdbms.landing_table" "$LANDING_TABLE"
set_variable "rsm_web_scraper.rdbms.clean_table" "$CLEAN_TABLE"

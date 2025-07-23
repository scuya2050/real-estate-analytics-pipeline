#!/usr/bin/env bash
set -euo pipefail

export CONTAINER_NAME="${CONTAINER_NAME:-rdbms-pg-1}"
export PORT="${PORT:-5432}"
export DB_USER="${DB_USER:-postgres}"
export DB="${DB:-default}"
export SCHEMA="${SCHEMA:-rsm}"
export LANDING_TABLE="${LANDING_TABLE:-properties_landing}"
export CLEAN_TABLE="${CLEAN_TABLE:-properties_clean}"
export LANDING_DIM="${LANDING_DIM:-locations_landing}"
export CLEAN_DIM="${CLEAN_DIM:-locations_clean}"

for file in sql/*.sql; do
  [[ -e "$file" ]] || { echo "No .sql files found"; exit 0; }

  echo "Executing: $file"

  envsubst < "$file" | docker exec -i "$CONTAINER_NAME"  psql -p "$PORT" -U "$DB_USER" -d "$DB"

  echo "Done: $file"
  echo
done

echo "All SQL files executed successfully."

echo "Cleaning locations dim tables if they exist"

docker exec -i "$CONTAINER_NAME" psql -p "$PORT" -U "$DB_USER" -d "$DB" -c  \
"TRUNCATE TABLE ${SCHEMA}.${LANDING_DIM};"

docker exec -i "$CONTAINER_NAME" psql -p "$PORT" -U "$DB_USER" -d "$DB" -c  \
"TRUNCATE TABLE ${SCHEMA}.${CLEAN_DIM};"

echo "Downloading and inserting locations dim table"

wget -O "locations_raw.csv" \
  "https://raw.githubusercontent.com/jmcastagnetto/ubigeo-peru-aumentado/refs/heads/main/ubigeo_distrito.csv"
(head -n1 "locations_raw.csv" && awk -F',' '$1 != "NA" && $2 != "NA"' "locations_raw.csv" | tail -n +2) > filtered_locations.csv

docker cp filtered_locations.csv "$CONTAINER_NAME":/tmp/filtered_locations.csv

docker exec -i "$CONTAINER_NAME" psql -p "$PORT" -U "$DB_USER" -d "$DB" -c  \
"\COPY ${SCHEMA}.${LANDING_DIM} FROM '/tmp/filtered_locations.csv' DELIMITER ',' CSV HEADER;"

docker exec -i "$CONTAINER_NAME" psql -p "$PORT" -U "$DB_USER" -d "$DB" -c  \
"INSERT INTO ${SCHEMA}.${CLEAN_DIM} 
SELECT 
  inei AS location_code, 
  departamento AS region, 
  provincia AS city, 
  distrito AS district 
FROM ${SCHEMA}.${LANDING_DIM};"

echo "Locations dim table downloaded and inserted successfully."

rm locations_raw.csv filtered_locations.csv
docker exec -i "$CONTAINER_NAME" rm /tmp/filtered_locations.csv

echo "Cleanup completed. All temporary files removed."
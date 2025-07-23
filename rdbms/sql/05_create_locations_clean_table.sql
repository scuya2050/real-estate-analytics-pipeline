CREATE TABLE IF NOT EXISTS ${SCHEMA}.${CLEAN_DIM} (
    location_code VARCHAR PRIMARY KEY,
    region VARCHAR,
    city VARCHAR,
    district VARCHAR
);
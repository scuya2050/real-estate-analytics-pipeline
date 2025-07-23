import json
from psycopg2.extras import Json
import psycopg2
from scraper.utils import get_logger
import os
from typing import Dict


def load_json_to_db(path: str, db_config: Dict[str, str]) -> None:
    """
    Loads data from a JSON file into a PostgreSQL database.

    Args:
        path (str): The path to the JSON file.
        db_config (Dict[str, str]): The database configuration.
    """
    logger = get_logger(__name__)
    logger.info("Reading JSON file ...")

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    logger.info(f"JSON file read successfully: {path}")
    logger.info(f"Connecting to database: {db_config['dbname']}")
    conn = psycopg2.connect(
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=db_config['port']
    )
    logger.info("Connected to the database successfully.")
    conn.autocommit = True
    cur = conn.cursor()

    batch_id = data.get('batch_id')
    logger.info(f"Inserting data into raw_data table with batch_id={batch_id} ...")
    cur.execute(
        f"""
        INSERT INTO {db_config['schema']}.{db_config['table']} (batch_id, payload)
        VALUES (%s, %s);
        """,
        (batch_id, Json(data))
    )

    logger.info("Data inserted successfully.")

    cur.close()
    conn.close()


def load_csv_to_db(path: str, db_config: Dict[str, str]) -> None:
    """
    Loads data from a CSV file into a PostgreSQL database.

    Args:
        path (str): The path to the CSV file.
        db_config (Dict[str, str]): The database configuration.
    """
    logger = get_logger(__name__)

    logger.info(f"Connecting to database: {db_config['dbname']}")
    conn = psycopg2.connect(
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=db_config['port']
    )
    logger.info("Connected to the database successfully.")
    conn.autocommit = True
    cur = conn.cursor()

    logger.info(f"Inserting data into landing table from file {os.path.basename(path)} ...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = f.read()
            header = reader.splitlines()[0].split(',')
            columns = ', '.join(header)

        with open(path, 'r', encoding='utf-8') as f:
            sql_expr = f"""
                COPY {db_config['schema']}.{db_config['table']} ({columns})
                FROM STDIN WITH CSV HEADER
            """
            cur.copy_expert(sql_expr, f)
    except psycopg2.Error as e:
        logger.error(f"Error inserting data: {e.pgerror}")
        logger.error(f"Diagnostics: {e.diag.message_detail}")
        raise

    logger.info("Data inserted successfully.")
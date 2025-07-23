import argparse
import json
import os
import shutil
from typing import Dict

from scraper.loader import load_csv_to_db
from scraper.utils import get_logger, CONFIG_PATH


def parse_args(default_db_config: Dict[str, str]) -> Dict[str, str]:
    """
    Parses command-line arguments and merges them with the default database configuration.

    Args:
        default_db_config (Dict[str, str]): The default database configuration.

    Returns:
        Dict[str, str]: The merged database configuration.
    """
    parser = argparse.ArgumentParser(description='Load JSON data into PostgreSQL.')
    parser.add_argument('--dbname', help='Database name')
    parser.add_argument('--user', help='Database user')
    parser.add_argument('--password', help='Database password')
    parser.add_argument('--host', help='Database host')
    parser.add_argument('--port', type=int, help='Database port')
    parser.add_argument('--schema', help='Database schema')
    parser.add_argument('--table', help='Database table')
    args = parser.parse_args()

    db_cfg = default_db_config.copy()
    db_cfg['dbname'] = args.dbname or db_cfg.get('dbname')
    db_cfg['user'] = args.user or db_cfg.get('user')
    db_cfg['password'] = args.password or db_cfg.get('password')
    db_cfg['host'] = args.host or db_cfg.get('host')
    db_cfg['port'] = args.port or db_cfg.get('port')
    db_cfg['schema'] = args.schema or db_cfg.get('schema')
    db_cfg['table'] = args.table or db_cfg.get('table')

    return db_cfg


def main() -> None:
    """
    Main function to load processed CSV files into a PostgreSQL database.

    This function reads the database configuration, processes files in the `processed` directory,
    and moves them to the `loaded` directory after successful loading.
    """
    logger = get_logger(__name__)
    logger.info("Starting the JSON to PostgreSQL loader...")

    with open(CONFIG_PATH, 'r', encoding='utf-8') as cfg:
        default_db_config = json.load(cfg).get('db', {})

    db_cfg = parse_args(default_db_config)

    processed_dir = os.path.join(os.path.dirname(__file__), 'data', 'processed')
    loaded_dir = os.path.join(os.path.dirname(__file__), 'data', 'loaded')
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(loaded_dir, exist_ok=True)

    if not os.listdir(processed_dir):
        logger.error("No files found in the processed directory. Please run the scraper first.")
        return

    logger.info(f"Found {len(os.listdir(processed_dir))} files in the processed directory.")

    for entry in os.listdir(processed_dir):
        full_path = os.path.join(processed_dir, entry)
        if os.path.isfile(full_path):
            logger.info(f"Loading file: {full_path}")
            load_csv_to_db(full_path, db_cfg)
            logger.info(f"File {full_path} loaded successfully into the database.")
            shutil.move(full_path, loaded_dir)
            logger.info(f"Moved {full_path} to {loaded_dir}")

    logger.info("File to PostgreSQL loader completed successfully.")


if __name__ == '__main__':
    main()
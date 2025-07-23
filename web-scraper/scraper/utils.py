import json
import logging
import os
from typing import Any


CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

# Read config once
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG: dict[str, Any] = json.load(f)

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), CONFIG.get('log_file', 'logger.log'))
LOG_TO_FILE = CONFIG.get('log_to_file', True)
LOG_TO_CONSOLE = CONFIG.get('log_to_console', True)


def get_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger instance.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')

    # Remove all handlers if already set (to avoid duplicate logs)
    if logger.hasHandlers():
        logger.handlers.clear()

    if LOG_TO_FILE:
        # Ensure log file directory exists
        log_dir = os.path.dirname(LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if LOG_TO_CONSOLE:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
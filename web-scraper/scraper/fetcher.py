from cloudscraper import CloudScraper
import time
from scraper.utils import get_logger
from typing import Optional, Tuple, List
import requests
import csv


def fetch_location_data() -> Tuple[List[str], List[str], List[str]]:
    """
    Fetches location data from a remote CSV file.

    The data includes regions, cities, and districts, which are extracted from the CSV file.

    Returns:
        Tuple[List[str], List[str], List[str]]: A tuple containing three lists - regions, cities, and districts.
    """
    logger = get_logger(__name__)
    logger.info("Fetching location data ...")

    response = requests.get(
        "https://raw.githubusercontent.com/jmcastagnetto/ubigeo-peru-aumentado/refs/heads/main/ubigeo_distrito.csv"
    )
    response.raise_for_status()

    lines = response.text.splitlines()
    reader = csv.reader(lines)
    header = next(reader)  # Skip the header row

    regions: List[str] = []
    cities: List[str] = []
    districts: List[str] = []

    for row in reader:
        if row[0] != 'NA' and row[1] != 'NA':
            regions.append(row[2])
            cities.append(row[3])
            districts.append(row[4])

    return regions, cities, districts


def fetch_page(
    scraper: CloudScraper,
    url: str,
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    max_retries: int = 0
) -> Optional[str]:
    """
    Fetches the content of a web page using a CloudScraper instance.

    Args:
        scraper (CloudScraper): The CloudScraper instance to use for fetching the page.
        url (str): The URL of the page to fetch.
        headers (Optional[dict], optional): HTTP headers to include in the request. Defaults to None.
        params (Optional[dict], optional): Query parameters to include in the request. Defaults to None.
        max_retries (int, optional): The maximum number of retry attempts in case of failure. Defaults to 0.

    Returns:
        Optional[str]: The content of the page as a string, or None if the request fails.
    """
    logger = get_logger(__name__)
    for i in range(max_retries + 1):
        logger.info(f"Attempt #{i+1}: Fetching content from {url}...")
        try:
            response = scraper.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            time.sleep(2 ** (i + 1))
    return None
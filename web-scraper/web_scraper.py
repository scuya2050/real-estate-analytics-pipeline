import cloudscraper
from bs4 import BeautifulSoup
import time
import random
import json
import os
import hashlib
import csv
from typing import List, Tuple

from scraper.fetcher import fetch_page, fetch_location_data
from scraper.parser import SearchPageParser, PropertyPageParser
from scraper.utils import get_logger

import uuid
from datetime import datetime


def main() -> None:
    """
    Main function to run the web scraper.

    This function initializes the scraping process, fetches location data, and iterates through
    search result pages to extract property details.
    """
    # if os.getenv('ENVIRONMENT') == 'local':
    #     logger.info("Running in local environment.")
    # elif os.getenv('ENVIRONMENT') == 'production':
    #     logger.info("Running in production environment.")
    # else:
    #     logger.error("Environment variable 'ENVIRONMENT' is not set. Exiting...")
    #     return
    
    batch_extraction_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    batch_id = str(uuid.uuid4())

    logger = get_logger(__name__)
    logger.info(f"Starting data extraction with batch ID: {batch_id}")

    base_domain = "https://urbania.pe"
    regions, cities, districts = fetch_location_data()

    max_pages = 1000  # Set a maximum page limit to avoid infinite loops
    property_details_list: List[dict] = []

    scraper = cloudscraper.create_scraper()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        )
    }

    district_search_mapping = {
        "LIMA": "LIMA CERCADO",
        "CARMEN DE LA LEGUA REYNOSO": "CARMEN DE LA LEGUA",
        "ATE": "ATE VITARTE",
        "BREÑA": "BRENA",
        "MAGDALENA DEL MAR": "MAGDALENA",
        "LURIGANCHO": "CHOSICA LURIGANCHO",
    }

    for region, city, district in zip(regions, cities, districts):
        if region.lower() + "-" + city.lower() != "lima-lima" and region.lower() != "callao":
            continue

        # Apply district mapping
        district_search = district_search_mapping.get(district, district)

        logger.info(f"Fetching properties in {district}, {region}, {city}...")

        url = f"https://urbania.pe/buscar/alquiler-de-propiedades-en-{district_search.lower().replace(' ', '-')}--{city.lower().replace(' ', '-')}--{region.lower().replace(' ', '-')}"
        links_combined = []
    
        for page in range(1, max_pages + 1):
            # time.sleep(random.uniform(0.25, 0.75))  # Random sleep to avoid being blocked

            params = {
                "page": page,
                "priceMin": 1,
                "currencyId": 6,
            }

            logger.info(f"Fetching page {page}...")
            content = fetch_page(scraper=scraper, url=url, headers=headers, params=params, max_retries=2)

            if content is None:
                logger.error(f"Failed to fetch or parse page {page}. Stopping...")
                break
        
            soup = BeautifulSoup(content, 'lxml')
            search_parser = SearchPageParser(soup)

            current_page = search_parser.get_current_page_number()
            if current_page != page:
                logger.info(f"Reached the end of available pages at page {current_page - 1}. Stopping...")
                break

            if not search_parser.validate_links():
                logger.error(f"No valid links found on page {page}. Stopping...")
                break

            links = search_parser.get_links()
            links = [base_domain + link for link in links]
            
            logger.info(f"Found {len(links)} links on page {page}.")
            links_combined.extend(links)

        logger.info(f"Total links found: {len(links_combined)}")
        links_combined = list(set(links_combined))
        logger.info(f"Total unique links found: {len(links_combined)}")

        n_links = len(links_combined)
        max_digits = len(str(n_links))

        for i, link in enumerate(links_combined):
            # time.sleep(random.uniform(0.25, 0.75))  # Random sleep to avoid being blocked
            property_extraction_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            property_id = str(uuid.uuid5(uuid.NAMESPACE_URL, link))
            pct = ((i + 1) / n_links) * 100
            logger.info(f"[{(i + 1):{max_digits}}/{n_links} | {pct:6.2f}%] Fetching details from link ...")
            content = fetch_page(scraper=scraper, url=link, headers=headers, max_retries=2)

            if content is None:
                logger.error(f"Failed to fetch or parse link {link}. Skipping...")
                continue

            soup = BeautifulSoup(content, 'lxml')
            property_parser = PropertyPageParser(soup)

            if not property_parser.validate_link():
                logger.error(f"Invalid link: {link}. Article not active. Skipping...")
                continue

            property_type = property_parser.get_property_type()
            if property_type == "Edificio":
                logger.error(f"Property type is 'Edificio', skipping link {link}.")
                continue

            price_type, price_pen, price_usd = property_parser.get_price()
            additional_expense = property_parser.get_additional_expense()
            address = property_parser.get_address()
            total_size, covered_size, bedrooms, bathrooms, half_bathrooms, parking_spaces, age = property_parser.get_main_features()

            property_details = {
                "batch_id": batch_id,
                "batch_extraction_start": batch_extraction_start,
                "property_id": property_id,
                "property_extraction_start": property_extraction_start,
                "property_type": property_type,
                "price_type": price_type,
                "price_pen": price_pen,
                "price_usd": price_usd,
                "additional_expense": additional_expense,
                "address": address,
                "region": region,
                "city": city,
                "district": district,
                "total_size": total_size,
                "covered_size": covered_size,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "half_bathrooms": half_bathrooms,
                "parking_spaces": parking_spaces,
                "age": age,
                "link": link
            }

            property_details_list.append(property_details)
        
        if page == max_pages:
            raise ValueError("Reached maximum page limit without finding valid properties.")

    extraction_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Total properties processed: {len(property_details_list)}. Saving results...")

    # if os.getenv('ENVIRONMENT') == 'local':
    #     output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
    # else:
    #     output_dir = os.path.join(os.path.dirname(__file__), 'data', 'processed')

    output_dir = os.path.join(os.path.dirname(__file__), 'data', 'processed')
    fieldnames = property_details_list[0].keys()

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'properties_listing_{batch_id}.csv')
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(property_details_list)

    logger.info(f"Data extraction completed. Results saved to {output_path}")


if __name__ == "__main__":
    main()

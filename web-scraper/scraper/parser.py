from bs4 import BeautifulSoup
from scraper.utils import get_logger
from typing import Optional, List


class SearchPageParser:
    """
    A parser for extracting data from search result pages.
    """
    def __init__(self, soup: BeautifulSoup):
        """
        Initializes the SearchPageParser with a BeautifulSoup object.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML content of the page.
        """
        self.soup = soup
        self.logger = get_logger(__name__)

    def get_current_page_number(self) -> int:
        """
        Extracts the current page number from the search results.

        Returns:
            int: The current page number. Defaults to 1 if not found.
        """
        self.logger.info("Parsing current page number ...")
        element = self.soup.select_one("a[class='paging-module__page-item paging-module__page-item-current']")
        if element is None:
            self.logger.error("Current page number not found. Assuming just 1 page.")
            return 1
        return int(element.get_text(strip=True))

    def validate_links(self) -> bool:
        """
        Validates if the page contains any links.

        Returns:
            bool: True if links are found, False otherwise.
        """
        self.logger.info("Validating links ...")
        element = self.soup.select_one("div[class='postingsNoResults-module__container']")
        if element is not None:
            self.logger.error("No links found on the page.")
            return False
        return True

    def get_links(self) -> List[str]:
        """
        Extracts all property links from the search results.

        Returns:
            List[str]: A list of property links.
        """
        self.logger.info("Parsing links ...")
        elements = self.soup.select("h3[class='postingCard-module__posting-description'] > a")
        return [element['href'] for element in elements]


class PropertyPageParser:
    """
    A parser for extracting data from property detail pages.
    """
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.logger = get_logger(__name__)


    def validate_link(self) -> list[str]:
        self.logger.info("Validating link ...")
        element = self.soup.select_one("div[id='article-container']")
        if element is None:
            self.logger.error("No article found.")
            return False
        else:
            return True


    def get_property_type(self) -> list[str]:
        self.logger.info("Parsing building type ...")
        element = self.soup.select_one("div[id='article-container'] > *:first-child")
        property_header = element.get_text().strip()
        if "edificio" in property_header.lower():
            property_type = "Edificio"
        else:
            property_type = property_header.split("·")[0].strip().title()

        # self.logger.info(f"Property Type: {property_type}")
        return property_type


    def get_price(self) -> tuple[int, int, Optional[int]]:
        self.logger.info(f"Parsing price ...")

        header_element = self.soup.select_one("div[class='price-item-container']:last-child > div[class='price-value'] > span")
        price_type = header_element.find_all(string=True, recursive=False)[0].strip().title()

        details_elements = self.soup.select("div[class='price-item-container']:last-child > div[class='price-value'] > span:first-child > span")
        price_pen = int(details_elements[0].get_text(strip=True).replace("S/ ", "").replace(",", "").strip())

        if len(details_elements) == 3:
            if details_elements[2].get_text(strip=True) != '':
                price_usd = int(details_elements[2].get_text(strip=True).replace("USD ", "").replace(",", "").strip())
            else:
                price_usd = None
        else:
            price_usd = None

        # self.logger.info(f"Price Type: {price_type}, Prices PEN: {price_pen}, Prices USD: {price_usd}")
        return price_type, price_pen, price_usd


    def get_additional_expense(self) -> list[int]:
        self.logger.info(f"Parsing additional expense ...")
        elements = self.soup.select("div[class='price-item-container']:last-child > div[class='price-extra'] > span")

        if elements is None or len(elements) == 0:
            return None
        additional_expense = elements[0].get_text(strip=True)
        additional_expense = int(additional_expense.replace("S/ ", "").replace("Mantenimiento", "").replace(",", "").strip())
        # self.logger.info(f"Additional Expenses: {additional_expense}")
        return additional_expense


    def get_address(self) -> list[int]:
        self.logger.info(f"Parsing address ...")

        element = self.soup.select_one("div[class='section-location-property section-location-property-classified'] > h4")
        if element is not None:
            address = element.get_text(strip=True)
        else:
            element = self.soup.select_one("div[class='section-location no-location'] > b")
            if element is not None:
                address = element.get_text(strip=True)
            else:
                address = None
        # self.logger.info(f"Addresses: {address}")
        return address


    def get_main_features(self) -> tuple[int, int, int, int, int, int, int]:
        self.logger.info(f"Parsing main features ...")

        elements = self.soup.select("ul[id='section-icon-features-property'] > li")

        total_size = 0
        covered_size = 0
        bedrooms = 0
        bathrooms = 0
        half_bathrooms = 0
        parking_spaces = 0
        age = 0
        
        for element in elements:
            quantity = element.get_text(strip=True).replace("\n", "").replace("\t", " ").strip().split(" ")[0].strip()
            child = element.select_one('i')
            if "icon-stotal" in child['class']:
                total_size = int(quantity)
            elif "icon-scubierta" in child['class']:
                covered_size = int(quantity)
            elif "icon-dormitorio" in child['class']:
                bedrooms = int(quantity)
            elif "icon-bano" in child['class']:
                bathrooms = int(quantity)
            elif "icon-toilete" in child['class']:
                half_bathrooms = int(quantity)
            elif "icon-cochera" in child['class']:
                parking_spaces = int(quantity)
            elif "icon-antiguedad" in child['class']:
                if "a" in quantity.lower():
                    age = -1
                elif "en" in quantity.lower():
                    age = -2
                else:
                    age = int(quantity)
        # self.logger.info(f"Main Features - Total Size: {total_size}, Covered Size: {covered_size}, Bedrooms: {bedrooms}, Bathrooms: {bathrooms}, Half Bathrooms: {half_bathrooms}, Parking Spaces: {parking_spaces}, Age: {age}")
        return total_size, covered_size, bedrooms, bathrooms, half_bathrooms, parking_spaces, age

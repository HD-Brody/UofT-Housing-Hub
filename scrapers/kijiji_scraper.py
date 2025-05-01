from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import List, Dict
import pprint


def get_kijiji_driver() -> webdriver.Chrome:
    """
    Initialize and return a Selenium Chrome driver in headless mode.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Replace with your path to chromedriver if not in PATH
    driver_path = "chromedriver-win64\chromedriver.exe"  

    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def get_kijiji_listings(url: str, max_pages: int = 3) -> List[Dict[str, str]]:
    """
    Scrape Kijiji housing listings across multiple pages.

    Args:
        url (str): The base Kijiji search URL.
        max_pages (int): Maximum number of pages to scrape.

    Returns:
        List[Dict[str, str]]: A list of listings, each with title, price, location, URL, etc.
    """
    driver = get_kijiji_driver()
    driver.get(url)

    cards = get_listing_cards(driver)

    listings = []
    for card in cards[:2]:
        listings.append(parse_listing_card(card))
    
    driver.quit()

    return listings


def get_listing_cards(driver: WebDriver) -> List[WebElement]:
    """
    Find and return all listing card elements from the current page.

    Args:
        driver (WebDriver): An active Selenium driver on a Kijiji search results page.

    Returns:
        List[WebElement]: List of elements representing housing listings.
    """
    return driver.find_elements(By.CSS_SELECTOR, 'section[data-testid="listing-card"]')


def parse_listing_card(card: WebElement) -> Dict[str, str]:
    """
    Extract listing details from a single Kijiji listing card.

    Args:
        card (WebElement): The WebElement representing one listing.

    Returns:
        Dict[str, str]: A dictionary containing the title, price, address, description, bedrooms, bathrooms and URL.
    """
    title = card.find_element(By.CSS_SELECTOR, 'h3[data-testid="listing-title"]').text
    price = card.find_element(By.CSS_SELECTOR, 'div[data-testid="listing-price-container"]').text
    url = card.find_element(By.CSS_SELECTOR, 'a[data-testid="listing-link"]').get_attribute("href")
    address, description = get_address_and_description(url)
    bedrooms = card.find_element(By.CSS_SELECTOR, 'li[aria-label="Bedrooms"]').text
    bathrooms = card.find_element(By.CSS_SELECTOR, 'li[aria-label="Bathrooms"]').text

    return {
        "title": title,
        "price": price,
        "address": address,
        "description": description,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "url": url
    }


def get_address_and_description(listing_url: str) -> tuple[str,str]:
    """
    Navigate to a listing's detail page and extract its address and full description.

    Args:
        driver (WebDriver): Selenium WebDriver instance.
        listing_url (str): The URL of the individual Kijiji listing.

    Returns:
        str: Cleaned description text from the listing page.
    """
    driver = get_kijiji_driver()
    driver.get(listing_url)
    address = driver.find_element(By.CSS_SELECTOR, 'button[class="sc-c8742e84-0 fukShK"]').text
    description = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="vip-description-wrapper"]').text
    driver.quit()
    return address, description


if __name__ == "__main__":
    pprint.pprint(get_kijiji_listings("https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273"))
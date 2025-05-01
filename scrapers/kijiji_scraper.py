from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
import pprint


def get_kijiji_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver_path = "chromedriver-win64\\chromedriver.exe"
    service = Service(executable_path=driver_path)
    return webdriver.Chrome(service=service, options=options)


def get_kijiji_listings(url: str, budget: int, beds: float, baths: float) -> List[Dict[str, str]]:
    """
    Scrape listing summaries, then enrich them in parallel.
    """
    main_driver = get_kijiji_driver()
    main_driver.get(url)

    cards = get_listing_cards(main_driver)
    listings = []
    for card in cards:
        listing = parse_listing_card(card, budget, beds, baths)
        if listing:
            listings.append(listing)
    main_driver.quit()

    # Multithreaded detail scraping
    with ThreadPoolExecutor(max_workers=5) as executor:
        enriched = list(executor.map(enrich_listing_details, listings))

    return enriched


def get_listing_cards(driver: WebDriver) -> List[WebElement]:
    return driver.find_elements(By.CSS_SELECTOR, 'section[data-testid="listing-card"]')


def parse_listing_card(card: WebElement, budget: int, beds: float, baths: float) -> Dict[str, str]:
    try:
        title = card.find_element(By.CSS_SELECTOR, 'h3[data-testid="listing-title"]').text
    except:
        title = "N/A"

    try:
        price = card.find_element(By.CSS_SELECTOR, 'div[data-testid="listing-price-container"]').text
        price_num = int(price.replace("$", "").replace(",", "")[:-3].strip())
        if price_num > budget:
            return None
    except:
        price = "N/A"

    try:
        url = card.find_element(By.CSS_SELECTOR, 'a[data-testid="listing-link"]').get_attribute("href")
    except:
        url = "N/A"

    try:
        bedrooms = card.find_element(By.CSS_SELECTOR, 'li[aria-label="Bedrooms"]').text
        if float(bedrooms) != beds:
            return None
    except:
        bedrooms = "N/A"

    try:
        bathrooms = card.find_element(By.CSS_SELECTOR, 'li[aria-label="Bathrooms"]').text
        if float(bathrooms) < baths:
            return None
    except:
        bathrooms = "N/A"

    return {
        "title": title, 
        "price": price, 
        "url": url, 
        "bedrooms": bedrooms,
        "bathrooms": bathrooms
        }


def enrich_listing_details(listing: Dict[str, str]) -> Dict[str, str]:
    """
    Run in parallel: each thread loads one listing URL and extracts address + description.
    """
    driver = get_kijiji_driver()

    try:
        driver.get(listing["url"])

        try:
            wait = WebDriverWait(driver, 5)
            address_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[class="sc-c8742e84-0 fukShK"]')))
            listing["address"] = address_btn.text
        except:
            listing["address"] = "N/A"

        try:
            desc_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="vip-description-wrapper"]')))
            listing["description"] = desc_div.text
        except:
            listing["description"] = "N/A"

    except:
        listing["address"] = "N/A"
        listing["description"] = "N/A"

    driver.quit()
    return listing


if __name__ == "__main__":
    base_url = "https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273?address=University%20of%20Toronto%2C%20King%27s%20College%20Circle%2C%20Toronto%2C%20ON&ll=43.663487%2C-79.3958273&radius=2"
    
    budget = int(input("Max budget: "))
    num_beds = float(input('Num beds: '))
    min_bathrooms = float(input('Min bathrooms: '))

    results = get_kijiji_listings(base_url, budget, num_beds, min_bathrooms)
    pprint.pprint(results)

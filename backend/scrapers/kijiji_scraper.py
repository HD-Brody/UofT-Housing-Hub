import time
import pprint
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor


def get_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver_path = "chromedriver-win64\\chromedriver.exe"
    service = Service(executable_path=driver_path)
    return webdriver.Chrome(service=service, options=options)


def get_kijiji_listings(url: str) -> List[Dict[str, str]]:
    """
    Scrape listing summaries, then enrich them in parallel.
    """
    driver = get_driver()
    driver.get(url)

    cards = get_listing_cards(driver)
    listings = []
    for card in cards:
        listing = parse_listing_card(card)
        # pprint.pprint(listing)
        listings.append(listing)
    driver.quit()

    # # Multithreaded detail scraping
    # with ThreadPoolExecutor(max_workers=5) as executor:
    #     enriched = list(executor.map(enrich_listing_details, listings))

    # return enriched
    return listings


def get_listing_cards(driver: WebDriver) -> List[WebElement]:
    return driver.find_elements(By.CSS_SELECTOR, 'section[data-testid="listing-card"]')


def parse_listing_card(card: WebElement) -> Dict[str, str]:
    try:
        title = card.find_element(By.CSS_SELECTOR, 'h3[data-testid="listing-title"]').text
    except:
        title = "N/A"

    try:
        price = (card.find_element(By.CSS_SELECTOR, 'div[data-testid="listing-price-container"]').text)[:-3]
    except:
        price = "N/A"

    try:
        url = card.find_element(By.CSS_SELECTOR, 'a[data-testid="listing-link"]').get_attribute("href")
    except:
        url = "N/A"

    try:
        bedrooms = card.find_element(By.CSS_SELECTOR, 'li[aria-label="Bedrooms"]').text
    except:
        bedrooms = "N/A"

    try:
        bathrooms = card.find_element(By.CSS_SELECTOR, 'li[aria-label="Bathrooms"]').text
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
    driver = get_driver()

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


def construct_kijiji_url(budget=None, bedrooms=None, bathrooms=None):
    base_url = "https://www.kijiji.ca/b-apartments-condos/city-of-toronto/"

    # Build the keyword path segment
    keywords = []
    if bathrooms:
        keywords.append(f"{bathrooms}+bathroom" if bathrooms == 1 else f"{bathrooms}+bathrooms")
    if bedrooms:
        keywords.append(f"{bedrooms}+bedroom" if bedrooms == 1 else f"{bedrooms}+bedrooms")
    
    if keywords:
        base_url += "-".join(keywords) + "/"

    # Category and filter codes (in proper order)
    category = "c37l1700273"
    filters = []
    if bathrooms:
        filters.append("a120")
    if bedrooms:
        filters.append("a27949001")

    category_with_filters = category + "".join(filters)
    base_url += category_with_filters

    # Query parameters
    query_params = {
        "radius": "2.0",
        "address": "University+of+Toronto%2C+King%27s+College+Circle%2C+Toronto%2C+ON",
        "ll": "43.663487%2C-79.3958273",
        "view": "list"
    }
    if budget:
        query_params["price"] = f"0__{budget}"

    query_string = "&".join(f"{key}={value}" for key, value in query_params.items())

    return f"{base_url}?{query_string}"


def filtered_listings(listings: List[Dict[str, str]], budget: int, beds: int, baths: int) -> None:
    """ 
    Return copy of listings without listings that do not fit the user's preferences.
    """

    listings_copy = listings[:]

    i = 0
    while i < len(listings_copy):
        listing = listings[i]
        if listing["price"] == "Please Contact":
            i += 1
        try:
            if (int(listing["price"].replace("$","").replace(",","").replace(".","")[:-2]) > int(budget) or 
                    float(listing["bedrooms"]) != int(beds) or 
                    float(listing["bathrooms"]) < int(baths)):
                listings_copy.pop(i)
            else:
                i += 1
        except:
            i += 1

    return listings_copy


if __name__ == "__main__":
    budget = input("Max budget: ")
    num_beds = input('Num beds: ')
    min_bathrooms = input('Min bathrooms: ')
    
    url = construct_kijiji_url(budget,num_beds,min_bathrooms)
    print(url)
    results = get_kijiji_listings(url)
    filtered = filtered_listings(results, budget, num_beds, min_bathrooms)
    pprint.pprint(filtered)

import time
import pprint
import os
import subprocess
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
    options.add_argument("--headless=new")  # Use new headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")  # Suppress most logs
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # Suppress TensorFlow and OpenCV logging (if you use them)
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

    scraper_dir = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.abspath(os.path.join(scraper_dir, "..", "chromedriver-win64", "chromedriver.exe"))

    # Fully suppress ChromeDriver + Chrome output
    service = Service(driver_path)
    service.creationflags = subprocess.CREATE_NO_WINDOW  # Hides the console window (Windows only)
    service.log_file = open(os.devnull, "w")  # Redirects ChromeDriver logs to null

    return webdriver.Chrome(service=service, options=options)


def get_padmapper_listings(url: str) -> List[Dict[str, str]]:
    """
    Scrape listing summaries
    """
    driver = get_driver()
    driver.get(url)

    cards = get_listing_cards(driver)
    listings = []
    for card in cards:
        if card.text:
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
    container = driver.find_element(By.CSS_SELECTOR, 'div[class="list_listItemContainer__h1gh6"]')
    container2 = container.find_element(By.XPATH, "./div")
    listings = container2.find_elements(By.XPATH, "./div")
    return listings


def parse_listing_card(card: WebElement) -> Dict[str, str]:
    txt_list = card.text.split("\n")
    if 'ONLINE TOURS' in txt_list[0] or 'VERIFIED' in txt_list[0]:
        txt_list.pop(0)
    
    title = txt_list[3] + ', ' + txt_list[2]
    price = txt_list[0]
    bedrooms = txt_list[1][0]
    if "Bathroom" in txt_list[1]:
        bathrooms = txt_list[1][txt_list[1].index("Bathroom")-2]
    else:
        bathrooms = "N/A"
    
    url = card.find_element(By.CSS_SELECTOR, 'a').get_attribute("href")

    return {
        "title": title, 
        "price": price, 
        "url": url, 
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "source": "Padmapper"
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


def construct_padmapper_url(budget=None, bedrooms=None, bathrooms=None):
    base_url = "https://www.padmapper.com/apartments/toronto-on/university-of-toronto"
    suffix = "box=-79.40926,43.65619,-79.38034,43.67045"

    bath_str = f"?bathrooms={bathrooms}&" if bathrooms else "?"
    bed_str = f"/{bedrooms}-beds" if bedrooms else ""
    budget_str = f"/under-{budget}" if budget else ""

    return f"{base_url}{bed_str}{budget_str}{bath_str}{suffix}"


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


def get_address_from_url(listing_url: str) -> str:
    driver = get_driver()
    driver.get(listing_url)
    try:
        address_element = driver.find_element(By.XPATH, "//h5[text()='Address']/following-sibling::div")
        return address_element.text
    except:
        return "N/A"


def check_if_old(listing_url: str) -> bool:
    driver = get_driver()
    driver.get(listing_url)

    return bool(driver.find_elements(By.CSS_SELECTOR, ".row.p-no-gutter.NotAvailable_detailFullInactive__RMA9D.NotAvailable_noBorder__IcRaj"))


if __name__ == "__main__":
    # budget = input("Max budget: ")
    # num_beds = input('Num beds: ')
    # min_bathrooms = input('Min bathrooms: ')
    
    # url = construct_padmapper_url(budget,num_beds,min_bathrooms)
    # print(url)
    # results = get_padmapper_listings(url)
    # # filtered = filtered_listings(results, budget, num_beds, min_bathrooms)
    # pprint.pprint(results)
    print(check_if_old("https://www.padmapper.com/rentals/61099961/3-bedroom-3-bath-apartment-at-beverley-st-d'arcy-st-toronto-on-m5t-1j9"))
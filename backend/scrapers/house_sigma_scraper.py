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


def get_house_sigma_listings(pages: int = 1, url: str = "https://housesigma.com/on/map/?status=for-lease&lat=43.657411&lon=-79.387051&zoom=14.1&page=1") -> List[Dict[str, str]]:
    """
    Scrape listing summaries
    """
    listings = []

    for p_num in range(pages):
        try:
            url = url[:-1] + str(p_num+1)

            driver = get_driver()
            driver.get(url)
            
            dropdown = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".dropdown.app-dropdown-options"))
            )
            dropdown.click()
            button = driver.find_element(By.CLASS_NAME, "app-single-option")
            button.click()
            time.sleep(0.5)

            cards = get_listing_cards(driver)

            temp = []
            for card in cards:
                listing = parse_listing_card(card)
                if "sign-in" not in listing["title"]:
                    temp.append(listing)

            listings.extend(temp)

            driver.quit()

        except Exception as e:
            print(e)
            break

    return listings


def get_listing_cards(driver: WebDriver) -> List[WebElement]:
    return driver.find_elements(By.CSS_SELECTOR, 'article[class="pc-listing-card not-logged"]')


def parse_listing_card(card: WebElement) -> Dict[str, str]:
    try:
        title = card.find_element(By.CSS_SELECTOR, 'h3[class="address"]').text
    except:
        title = "N/A"

    try:
        price_box = card.find_element(By.CSS_SELECTOR, 'p[class="price"]')
        price = (price_box.find_element(By.CSS_SELECTOR, 'span[class="highlight"]').text)
    except:
        price = "N/A"

    try:
        url = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
    except:
        url = "N/A"

    try:
        info_box = card.find_element(By.CSS_SELECTOR, 'div[class="listing-spec-mini"]')
        beds_baths = info_box.text.split()
        bedrooms = eval(beds_baths[0])
        bathrooms = beds_baths[1]
    except:
        bedrooms = "N/A"
        bathrooms = "N/A"


    return {
        "title": title, 
        "price": price, 
        "url": url, 
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "source": "House Sigma"
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


def filtered_listings(listings: List[Dict[str, str]], budget: int = None, beds: int = None, baths: int = None) -> None:
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

    driver.quit()
    pass
    

def check_if_old(listing_url: str) -> bool:
    driver = get_driver()
    driver.get(listing_url)

    pass


if __name__ == "__main__":
    listings = get_house_sigma_listings(3)
    for l in listings:
        pprint.pprint(l)
    print(len(listings))
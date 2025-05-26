from scrapers.kijiji_scraper import get_kijiji_listings, construct_kijiji_url, filtered_listings
from scrapers.padmapper_scraper import get_padmapper_listings, construct_padmapper_url
from db.housing_db import insert_listing

def scrape_and_insert(budget: int, num_beds: float, min_bathrooms: float) -> None:
    kijiji_url = construct_kijiji_url(budget, num_beds, min_bathrooms)
    padmapper_url = construct_padmapper_url(budget, num_beds, min_bathrooms)

    kijiji_results = get_kijiji_listings(kijiji_url)
    kijiji_results = filtered_listings(kijiji_results, budget, num_beds, min_bathrooms)
    padmapper_results = get_padmapper_listings(padmapper_url)

    for listing in kijiji_results:
        insert_listing(listing, "Kijiji")

    for listing in padmapper_results:
        insert_listing(listing, "Padmapper")

    print("All listings inserted")
from scrapers.kijiji_scraper import get_kijiji_listings, construct_kijiji_url, filtered_listings
from scrapers.padmapper_scraper import get_padmapper_listings, construct_padmapper_url
from housing_db import init_db, insert_listing


if __name__ == "__main__":
    #Initialize the database
    init_db()

    #Get user preferences
    budget = input("Max budget: ")
    num_beds = input('Num beds: ')
    min_bathrooms = input('Min bathrooms: ')

    #Construct urls based on user preferences
    kijiji_url = construct_kijiji_url(budget, num_beds, min_bathrooms)
    padmapper_url = construct_padmapper_url(budget, num_beds, min_bathrooms)

    #Get listings from scrapers
    kijiji_results = get_kijiji_listings(kijiji_url)
    kijiji_results = filtered_listings(kijiji_results, budget, num_beds, min_bathrooms) #Kijiji results need to be filtered further
    padmapper_results = get_padmapper_listings(padmapper_url)

    #Save listings to database
    for listing in kijiji_results:
        insert_listing(listing, "Kijiji")

    for listing in padmapper_results:
        insert_listing(listing, "Padmapper")

    print("All listings inserted")
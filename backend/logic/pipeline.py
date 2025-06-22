from scrapers.kijiji_scraper import get_kijiji_listings, construct_kijiji_url, filtered_listings, get_address_from_url as get_kijiji_address
from scrapers.padmapper_scraper import get_padmapper_listings, construct_padmapper_url, get_address_from_url as get_padmapper_address
from scrapers.image_scraper import get_first_image_url
from db.housing_db import insert_listing
from db.housing_db import update_listing_info
from api.distance_matrix import get_travel_details, get_coordinates


def scrape_and_insert(budget: int = None, num_beds: float = None, min_bathrooms: float = None) -> list[dict]:
    kijiji_url = construct_kijiji_url(budget, num_beds, min_bathrooms)
    padmapper_url = construct_padmapper_url(budget, num_beds, min_bathrooms)

    kijiji_results = get_kijiji_listings(kijiji_url)
    kijiji_results = filtered_listings(kijiji_results, budget, num_beds, min_bathrooms)
    padmapper_results = get_padmapper_listings(padmapper_url)

    for listing in kijiji_results:
        insert_listing(listing, "Kijiji")

    for listing in padmapper_results:
        insert_listing(listing, "Padmapper")

    print(f"{len(kijiji_results + padmapper_results)} listings inserted")
    return kijiji_results + padmapper_results


def enrich_listings(results: list[dict]):
    for listing in results:
        updated = False

        # Address
        if not listing.get("address") or listing["address"] == "N/A":
            if "Kijiji" == listing["source"]:
                address = get_kijiji_address(listing["url"])
            elif "Padmapper" == listing["source"]:
                address = get_padmapper_address(listing["url"])
            else:
                address = "N/A"

            if address != "N/A":
                update_listing_info(listing["url"], address=address)
                listing["address"] = address
                updated = True
                print(f"Added address: {address}")

        # Lon/lat
        if "lon" not in listing or not listing.get("lon"):
            try:
                lon, lat = get_coordinates(address[-7:])
                update_listing_info(listing["url"], lon=lon, lat=lat)
                listing["lon"] = lon
                listing["lat"] = lat
                updated = True
            except Exception as e:
                print(f"Could not get lon/lat for {listing['url']}: {e}")

        # Walk time
        if "walk_time_minutes" not in listing or not listing.get("walk_time_minutes"):
            try:
                if not listing.get("address") or listing["address"].strip() == "" or listing["address"] == "N/A":
                    continue
                walk_time, _ = get_travel_details((listing["lon"], listing["lat"]))
                update_listing_info(listing["url"], walk_time=walk_time)
                listing["walk_time_minutes"] = walk_time
                updated = True
            except Exception as e:
                print(f"Could not get walk time for {listing['url']}: {e}")

        # Image url
        if "image_url" not in listing or not listing.get("listing_url"):
            try:
                image_url = get_first_image_url(listing["url"])
                update_listing_info(listing["url"], image_url=image_url)
                listing["image_url"] = image_url
                updated = True
            except Exception as e:
                print(f"Could not get image url for {listing['url']}: {e}")

        if updated:
            print(f"Updated listing: {listing['url']}")
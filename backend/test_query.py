from db.housing_db import init_db, get_filtered_listings
from logic.pipeline import add_listings_from_input

init_db()

budget = input("Max budget: ")
beds = input("Min beds: ")
baths = input("Min baths: ")

add_listings_from_input(budget, beds, baths)
results = get_filtered_listings(budget, beds, baths)

for listing in results:
    print(f"{listing['title']} | {listing['price']} | {listing['bedrooms']} bed / {listing['bathrooms']} bath")
    print(f"{listing['address']}")
    print(f"{listing['url']}")
    print(f"Source: {listing['source']}")
    print("-" * 50)

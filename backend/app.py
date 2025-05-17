from flask import Flask, request, jsonify
from flask_cors import CORS
from db.housing_db import init_db, get_filtered_listings
from logic.pipeline import add_listings_from_input

app = Flask(__name__)
CORS(app)

@app.route("/api/listings", methods=["POST"])
def listings():
    data = request.json
    max_price = data.get("max_price")
    min_beds = data.get("min_beds")
    min_baths = data.get("min_baths")

    add_listings_from_input(max_price, min_beds, min_baths)  # Scrape + insert into DB
    listings = get_filtered_listings(max_price, min_beds, min_baths)
    return jsonify(listings)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
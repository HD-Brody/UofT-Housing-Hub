from flask import Flask, request, jsonify
from flask_cors import CORS
from db.housing_db import init_db, get_filtered_listings
from logic.pipeline import scrape_and_insert, enrich_listings

app = Flask(__name__)
CORS(app)

@app.route("/api/listings", methods=["POST"])
def listings():
    data = request.json
    max_price = data.get("max_price")
    min_beds = data.get("min_beds")
    min_baths = data.get("min_baths")

    results = get_filtered_listings(max_price, min_beds, min_baths)

    if len(results) >= 7:
        enrich_listings(results)
        print("nuff listings, we good")
        return jsonify(results)
    
    scrape_and_insert(max_price, min_beds, min_baths)
    new_results = get_filtered_listings(max_price, min_beds, min_baths)
    enrich_listings(new_results)
    return jsonify(new_results)
    

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
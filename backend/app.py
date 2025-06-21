import sqlite3
import pprint
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from itertools import cycle
from apscheduler.schedulers.background import BackgroundScheduler
from db.housing_db import init_db, get_filtered_listings
from logic.pipeline import scrape_and_insert, enrich_listings
from ai.ai_search import get_filters_from_query

app = Flask(__name__)
CORS(app)

param_cycle = cycle([1, 2, 3, 4])

@app.route("/api/listings", methods=["POST"])
def listings():
    data = request.json
    max_price = data.get("max_price")
    min_beds = data.get("min_beds")
    min_baths = data.get("min_baths")
    walk_time_minutes = data.get("walk_time_minutes")

    results = get_filtered_listings(max_price, min_beds, min_baths)

    if len(results) >= 7:
        enrich_listings(results)
        results = get_filtered_listings(max_price, min_beds, min_baths, walk_time_minutes)
        print(f"Found {len(results)} results.")
        for r in results:
            pprint.pprint(r)
        return jsonify(results)
    
    scrape_and_insert(max_price, min_beds, min_baths)
    new_results = get_filtered_listings(max_price, min_beds, min_baths)
    enrich_listings(new_results)
    new_results = get_filtered_listings(max_price, min_beds, min_baths, walk_time_minutes)
    return jsonify(new_results)


@app.route("/api/smart_search", methods=["POST"])
def smart_search():
    user_input = request.json.get("query", "")
    if not user_input:
        return jsonify({"error": "No query provided"}), 400
    
    raw_filters = get_filters_from_query(user_input)

    if raw_filters is None:
        return jsonify({"error": "AI failed to return valid JSON"}), 500
    print(raw_filters)
    
    budget = raw_filters.get("budget")
    bedrooms = raw_filters.get("bedrooms")
    bathrooms = raw_filters.get("bathrooms")
    max_walk_time = raw_filters.get("max_walk_time")

    listings = get_filtered_listings(budget, bedrooms, bathrooms, max_walk_time)
    return jsonify(listings)


@app.route('/api/favourites', methods=['POST'])
def get_favourites():
    ids = request.json.get('ids', [])
    if not ids:
        return jsonify([])
    
    conn = sqlite3.connect("listings.db")
    c = conn.cursor()

    placeholders = ",".join("?" for _ in ids)
    query = f"""
        SELECT id, title, price, address, bedrooms, bathrooms, description, url, source, walk_time_minutes, image_url, lon, lat
        FROM listings
        WHERE id IN ({placeholders})
    """

    c.execute(query, ids)
    rows = c.fetchall()

    listings = [dict(zip([column[0] for column in c.description], row)) for row in rows]

    return jsonify(listings)


def scheduled_scrape():
    param = next(param_cycle)
    print(f"✅✅ Running scheduled scrape with param {param}...")
    new_listings = scrape_and_insert(param * 1000, param, 1)
    enrich_listings(new_listings)


if __name__ == "__main__":
    # init_db()
    # scheduled_scrape()

    # scheduler = BackgroundScheduler()
    # scheduler.add_job(func=scheduled_scrape, trigger="interval", hours=2.5)
    # scheduler.start()

    # import atexit
    # atexit.register(lambda: scheduler.shutdown())

    app.run(debug=True)
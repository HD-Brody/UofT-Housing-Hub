import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
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
    walk_time_minutes = data.get("walk_time_minutes")

    results = get_filtered_listings(max_price, min_beds, min_baths)

    if len(results) >= 7:
        enrich_listings(results)
        results = get_filtered_listings(max_price, min_beds, min_baths, walk_time_minutes)
        return jsonify(results)
    
    scrape_and_insert(max_price, min_beds, min_baths)
    new_results = get_filtered_listings(max_price, min_beds, min_baths)
    enrich_listings(new_results)
    new_results = get_filtered_listings(max_price, min_beds, min_baths, walk_time_minutes)
    return jsonify(new_results)


@app.route('/api/favourites', methods=['POST'])
def get_favourites():
    ids = request.json.get('ids', [])
    if not ids:
        return jsonify([])
    
    conn = sqlite3.connect("listings.db")
    c = conn.cursor()

    placeholders = ",".join("?" for _ in ids)
    query = f"""
        SELECT id, title, price, address, bedrooms, bathrooms, description, url, source, walk_time_minutes
        FROM listings
        WHERE id IN ({placeholders})
    """

    c.execute(query, ids)
    rows = c.fetchall()

    listings = [dict(zip([column[0] for column in c.description], row)) for row in rows]

    return jsonify(listings)


def scheduled_scrape():
    print("Running scheduled scrape...")
    new_listings = scrape_and_insert()
    enrich_listings(new_listings)


if __name__ == "__main__":
    # init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=scheduled_scrape, trigger="interval", hours=6)
    scheduler.start()

    import atexit
    atexit.register(lambda: scheduler.shutdown())

    app.run(debug=True)
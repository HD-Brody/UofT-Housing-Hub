import os
import sqlite3
from scrapers.image_scraper import get_first_image_url


# Get the directory of the current file (i.e., db/)
db_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level to backend/
project_root = os.path.abspath(os.path.join(db_dir, ".."))

# Build path to listings.db inside backend/
db_path = os.path.join(project_root, "listings.db")


def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS listings (  -- 3. Create table with columns
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price TEXT,
            address TEXT,
            bedrooms TEXT,
            bathrooms TEXT,
            description TEXT,
            url TEXT UNIQUE,
            source TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_listing(listing: dict, source: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        c.execute("""
            INSERT INTO listings (title, price, address, bedrooms, bathrooms, description, url, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            listing["title"],
            listing["price"],
            listing.get("address", ""),
            listing.get("bedrooms", ""),
            listing.get("bathrooms", ""),
            listing.get("description", ""),
            listing["url"],
            source
        ))

        conn.commit()
    except sqlite3.IntegrityError:
        # This happens if the URL already exists (because of UNIQUE constraint)
        print(f"[SKIP] Duplicate listing: {listing['url']}")

    conn.close()


def get_filtered_listings(max_price=None, num_bedrooms=None, min_bathrooms=None, walk_time_minutes=None) -> list[dict]:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Base query
    query = """
        SELECT id, title, price, address, bedrooms, bathrooms, description, url, source, walk_time_minutes, image_url
        FROM listings
        WHERE 1=1
    """

    params = []

    # Add filters conditionally
    if max_price:
        query += " AND CAST(REPLACE(REPLACE(price, '$', ''), ',', '') AS INTEGER) <= ?"
        params.append(max_price)

    if num_bedrooms:
        query += " AND CAST(bedrooms AS FLOAT) = ?"
        params.append(num_bedrooms)

    if min_bathrooms:
        query += " AND CAST(bathrooms AS FLOAT) >= ?"
        params.append(min_bathrooms)

    if walk_time_minutes:
        query += " AND CAST(walk_time_minutes AS FLOAT) <= ?"
        params.append(walk_time_minutes)

    
    query += " ORDER BY id DESC"

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    # Convert to list of dictionaries
    return [
        {
            "id": row[0],
            "title": row[1],
            "price": row[2],
            "address": row[3],
            "bedrooms": row[4],
            "bathrooms": row[5],
            "description": row[6],
            "url": row[7],
            "source": row[8],
            "walk_time_minutes": row[9],
            "image_url": row[10]
        }
        for row in rows
    ]


def update_listing_info(url: str, address: str = None, walk_time: float = None) -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    if address:
        c.execute("UPDATE listings SET address = ? WHERE url = ?", (address, url))

    if walk_time:
        c.execute("UPDATE listings SET walk_time_minutes = ? WHERE url = ?", (walk_time, url))

    conn.commit()
    conn.close()


def add_image_urls_to_listings() -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT id, url FROM listings WHERE image_url IS NULL")
    listings = c.fetchall()

    print(f"Found {len(listings)} listings to process.")
    count = 1

    for listing_id, url in listings:
        img_url = get_first_image_url(url)
        try:
            c.execute("UPDATE listings SET image_url = ? WHERE id = ?", (img_url, listing_id))
            conn.commit()
            print(f"Image saved {count}/{len(listings)}: {img_url}")
        except:
            print(f"Could not add image to {url}")
        count += 1

    conn.close()
    print("Done adding images")


def add_col(col_name: str) -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute(f"ALTER TABLE listings ADD COLUMN {col_name} REAL")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    add_image_urls_to_listings()
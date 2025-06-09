import os
import sys
import sqlite3
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scrapers.image_scraper import get_first_image_url
from api.distance_matrix import get_coordinates
from scrapers.kijiji_scraper import get_address_from_url as get_kijiji_address
from scrapers.padmapper_scraper import get_address_from_url as get_padmapper_address


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
        SELECT id, title, price, address, bedrooms, bathrooms, description, url, source, walk_time_minutes, image_url, lon, lat
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
            "image_url": row[10],
            "lon": row[11],
            "lat": row[12]
        }
        for row in rows
    ]


def update_listing_info(url: str, address: str = None, walk_time: float = None, lon: float = None, lat: float = None) -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    if address:
        c.execute("UPDATE listings SET address = ? WHERE url = ?", (address, url))

    if walk_time:
        c.execute("UPDATE listings SET walk_time_minutes = ? WHERE url = ?", (walk_time, url))

    if lon:
        c.execute("UPDATE listings SET lon = ? WHERE url = ?", (lon, url))

    if lat:
        c.execute("UPDATE listings SET lat = ? WHERE url = ?", (lat, url))

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


def add_lon_lat_to_listings() -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT id, address FROM listings WHERE walk_time_minutes IS NOT NULL OR walk_time_minutes != 222.6")
    listings = c.fetchall()

    print(f"Found {len(listings)} listings to process.")
    count = 1

    for listing_id, address in listings:
        lon, lat = get_coordinates(address)
        try:
            c.execute("UPDATE listings SET lon = ? WHERE id = ?", (lon, listing_id))
            c.execute("UPDATE listings SET lat = ? WHERE id = ?", (lat, listing_id))
            conn.commit()
            print(f"Coords saved {count}/{len(listings)}: {lon, lat}")
        except:
            print(f"Could not add coords")
        count += 1

    conn.close()
    print("Done adding lon and lat")


def add_col(col_name: str) -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute(f"ALTER TABLE listings ADD COLUMN {col_name} REAL")
    conn.commit()
    conn.close()


def add_address_where_needed() -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT url, source FROM listings WHERE address = ''")
    listings = c.fetchall()

    print(f"Found {len(listings)} listings to process.")
    count = 1

    for url, source in listings:
        try:
            if source == "Kijiji":
                address = get_kijiji_address(url)
            elif source == "Padmapper":
                address = get_padmapper_address(url)
            c.execute("UPDATE listings SET address = ? WHERE url = ?", (address, url))
            conn.commit()
            print(f"Coords saved {count}/{len(listings)}: {address}")
        except:
            print(f"Could not add address")
        count += 1

    conn.close()
    print("Done adding addresses")


def remove_old_listings() -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT id, url, source FROM listings")
    listings = c.fetchall()
    print(f"Found {len(listings)} listings to delete.")
    count = 1

    for listing_id, url, source in listings:
        try:
            is_old = False
            if source == "Kijiji":
                pass
            elif source == "Padmapper":
                pass

            if is_old:
                c.execute("DELETE FROM listings WHERE url = ?", url)
                conn.commit()
                print((f"Deleted {count} listings: {url}"))
                count += 1
        except:
            print("Could not find listing in database")
        
    conn.close()
    print("Done deleting listings")


if __name__ == "__main__":
    pass
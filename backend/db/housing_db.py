import sqlite3

def init_db():
    conn = sqlite3.connect("listings.db")
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
    conn = sqlite3.connect("backend\listings.db")
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
    conn = sqlite3.connect("listings.db")
    c = conn.cursor()

    # Base query
    query = """
        SELECT title, price, address, bedrooms, bathrooms, description, url, source, walk_time_minutes
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
            "title": row[0],
            "price": row[1],
            "address": row[2],
            "bedrooms": row[3],
            "bathrooms": row[4],
            "description": row[5],
            "url": row[6],
            "source": row[7],
            "walk_time_minutes": row[8]
        }
        for row in rows
    ]


def update_listing_info(url: str, address: str = None, walk_time: float = None) -> None:
    conn = sqlite3.connect("listings.db")
    c = conn.cursor()

    if address:
        c.execute("UPDATE listings SET address = ? WHERE url = ?", (address, url))

    if walk_time:
        c.execute("UPDATE listings SET walk_time_minutes = ? WHERE url = ?", (walk_time, url))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    test_filtered = get_filtered_listings(3000, 3, 1, 20)
    print([listing["walk_time_minutes"] for listing in test_filtered])
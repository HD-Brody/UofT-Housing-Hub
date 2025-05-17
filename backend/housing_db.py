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
    conn = sqlite3.connect("listings.db")
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


def get_filtered_listings(max_price=None, min_bedrooms=None, min_bathrooms=None) -> list[dict]:
    conn = sqlite3.connect("listings.db")
    c = conn.cursor()

    # Base query
    query = """
        SELECT title, price, address, bedrooms, bathrooms, description, url, source
        FROM listings
        WHERE 1=1
    """

    params = []

    # Add filters conditionally
    if max_price:
        query += " AND CAST(REPLACE(REPLACE(price, '$', ''), ',', '') AS INTEGER) <= ?"
        params.append(max_price)

    if min_bedrooms:
        query += " AND CAST(bedrooms AS FLOAT) >= ?"
        params.append(min_bedrooms)

    if min_bathrooms:
        query += " AND CAST(bathrooms AS FLOAT) >= ?"
        params.append(min_bathrooms)

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
            "source": row[7]
        }
        for row in rows
    ]
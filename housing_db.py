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
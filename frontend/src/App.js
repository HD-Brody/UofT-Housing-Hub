import { useState } from "react";

function App() {
  const [maxPrice, setMaxPrice] = useState("");
  const [minBeds, setMinBeds] = useState("");
  const [minBaths, setMinBaths] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    const response = await fetch("http://localhost:5000/api/listings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        max_price: parseInt(maxPrice),
        min_beds: parseFloat(minBeds),
        min_baths: parseFloat(minBaths),
      }),
    });

    const data = await response.json();
    setResults(data); // Save the listings
  };

  return (
    <div>
      <h2>Student Housing Finder</h2>

      <h1>Find Student Housing Near UofT</h1>

      <div>
        <label>Max Price: ${maxPrice}</label>
        <input
          type="range"
          min="500"
          max="5000"
          step="50"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
        />
      </div>

      <div>
        <label>Num Bedrooms:</label>
        <input
          type="number"
          min="0"
          step="1"
          value={minBeds}
          onChange={(e) => setMinBeds(e.target.value)}
        />
      </div>

      <div>
        <label>Min Bathrooms:</label>
        <input
          type="number"
          min="0"
          step="1"
          value={minBaths}
          onChange={(e) => setMinBaths(e.target.value)}
        />
      </div>

      <button onClick={handleSearch}>Search</button>

      <div style={{ marginTop: "2rem" }}>
        <h2>Results</h2>

        {results.length === 0 && <p>No listings found.</p>}

        <ul>
          {results.map((listing, index) => (
            <li key={index} style={{ marginBottom: "1rem" }}>
              <strong>{listing.title}</strong><br />
              {listing.price} — {listing.bedrooms} bed / {listing.bathrooms} bath<br />
              {listing.address}<br />
              <a href={listing.url} target="_blank" rel="noopener noreferrer">View Listing</a><br />
              <em>Source: {listing.source}</em>
            </li>
          ))}
        </ul>
      </div>

    </div>
  );
}

export default App;
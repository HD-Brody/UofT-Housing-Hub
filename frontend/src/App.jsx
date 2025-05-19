import { useState } from "react";

function App() {
  const [maxPrice, setMaxPrice] = useState("");
  const [numBeds, setNumBeds] = useState("");
  const [minBaths, setMinBaths] = useState("");
  const [maxWalkTime, setMaxWalkTime] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    const response = await fetch("http://localhost:5000/api/listings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        max_price: parseInt(maxPrice),
        min_beds: parseFloat(numBeds),
        min_baths: parseFloat(minBaths),
      }),
    });

    const data = await response.json();
    setResults(data);
  };

  return (
    <div>
      <nav className="navbar">
        <h2>STUDENT HOUSING FINDER</h2>
        <div className="menu">
          <ul className="menuItems">
            <li><a href="#home">Home</a></li>
            <li><a href="#favourites">Favourites</a></li>
            <li><a href="#about">About</a></li>
          </ul>
        </div>
      </nav>

      <h1 className="title">Find Student Housing Near UofT</h1>

      <div className="userInputContainer">
        <div className="userInputs">

          <div className="budgetSection">
            <label>Budget</label>
            <div className="budgetRow">
              <span className="budgetAmount">${maxPrice}</span>
              <input
                type="range"
                min="500"
                max="5000"
                step="50"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
              />
            </div>
          </div>

          <div className="inputGroup">
            <label>Num Beds</label>
            <select value={numBeds} onChange={(e) => setNumBeds(e.target.value)}>
              {[1, 2, 3, 4].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>

          <div className="inputGroup">
            <label>Min Baths</label>
            <select value={minBaths} onChange={(e) => setMinBaths(e.target.value)}>
              {[1, 2, 3].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>

          <div className="inputGroup">
            <label>Max Walk Time (minutes)</label>
            <input
              type="number"
              min="5"
              step="5"
              value={maxWalkTime}
              onChange={(e) => setMaxWalkTime(e.target.value)}
            />
          </div>

          <button className="searchButton" onClick={handleSearch}>
            Find Listings
          </button>
        </div>
      </div>

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

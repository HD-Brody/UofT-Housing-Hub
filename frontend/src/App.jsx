import { useState } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHeart as farHeart } from '@fortawesome/free-regular-svg-icons'; // regular (outline)
import { faHeart as fasHeart } from '@fortawesome/free-solid-svg-icons';   // solid (filled)
import { faHouseUser } from '@fortawesome/free-solid-svg-icons';
import { useMemo } from "react";

function App() {
  const [maxPrice, setMaxPrice] = useState("2500");
  const [numBeds, setNumBeds] = useState("");
  const [minBaths, setMinBaths] = useState("");
  const [maxWalkTime, setMaxWalkTime] = useState("20");
  const [results, setResults] = useState([]);
  const [showListings, setShowListings] = useState(false);
  const [likedListings, setLikedListings] = useState({});
  const [showLoading, setShowLoading] = useState(false);
  const [sortBy, setSortBy] = useState("");


  const handleSearch = async () => {
    setShowLoading(true);
    const response = await fetch("http://localhost:5000/api/listings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        max_price: parseInt(maxPrice),
        min_beds: parseFloat(numBeds),
        min_baths: parseFloat(minBaths),
        walk_time_minutes: parseFloat(maxWalkTime)
      }),
    });

    const data = await response.json();
    setResults(data);
    setShowLoading(false);
    setShowListings(true);
  };


  const sortedResults = useMemo(() => {
    if (!sortBy) return results;

    const sorted = [...results];

    switch (sortBy) {
      case "Lowest price":
        sorted.sort((a, b) => parseInt(a.price.replace(/\D/g, "")) - parseInt(b.price.replace(/\D/g, "")));
        break;
      case "Hightest price":
        sorted.sort((a, b) => parseInt(b.price.replace(/\D/g, "")) - parseInt(a.price.replace(/\D/g, "")));
        break;
      case "Shortest distance":
        sorted.sort((a, b) => a.walk_time_minutes - b.walk_time_minutes);
        break;
      case "Longest distance":
        sorted.sort((a, b) => b.walk_time_minutes - a.walk_time_minutes);
        break;
      default:
        break;
    }

    return sorted;
  }, [results, sortBy]);


  return (
    <div>
      <nav className="navbar">
        
        <h2> <FontAwesomeIcon icon={faHouseUser} style={{ fontSize: "24px", color: "#3b82f6" }} /> UofT Housing Hub</h2>
        <div className="menu">
          <ul className="menuItems">
            <li><a href="#home">Home</a></li>
            <li><a href="#favourites">Favourites</a></li>
            <li><a href="#about">About</a></li>
          </ul>
        </div>
      </nav>

      <h1 className="subtitle">Find Student Housing Near UofT</h1>

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
              max="60"
              step="5"
              value={maxWalkTime}
              onChange={(e) => setMaxWalkTime(e.target.value)}
              onKeyDown={(e) => e.preventDefault()}
            />
          </div>

          <button className="searchButton" onClick={handleSearch}>
            Find Listings
          </button>
        </div>
      </div>

      {showLoading && (<div class="loader"></div>)}

      {showListings && (
        <div className="listings-div" style={{ marginTop: "2rem" }}>
          <h2>Matching Listings</h2>
          <select className="sort-by" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            {["", "Lowest price", "Hightest price", "Shortest distance", "Longest distance"].map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
          {results.length === 0 && <p className="no-listings-found">No listings found.</p>}
          <ul className="listings-list">
            {sortedResults.map((listing, index) => {
              const isLiked = likedListings[index] || false;

              const toggleLike = () => {
                setLikedListings(prev => ({
                  ...prev,
                  [index]: !isLiked
                }));
              };

              return (
                <div className="listing-box" key={index}>
                  <button className="heart-button" onClick={toggleLike}
                    style={isLiked ? {color: "#ff4d4d"} : {color:"grey"}}>
                    <FontAwesomeIcon icon={isLiked ? fasHeart : farHeart} />
                  </button>
                  <li style={{ marginBottom: "1rem" }}>
                    <div className="listing-text">
                      <h3>{listing.price}</h3>
                      <h4>{listing.title}</h4>
                      <p>{listing.bedrooms} Bed, {listing.bathrooms} Bath</p>
                      <p>{listing.walk_time_minutes} min walk from campus</p>
                      <div className="link-right">
                        <a href={listing.url} target="_blank" rel="noopener noreferrer">
                          View Listing
                        </a>
                      </div>
                    </div>
                  </li>
                </div>
              );
            })}
          </ul>
        </div>
      )}
      
    </div>
  );
}

export default App;

import './Listings.css';
import { useMemo, useState, useEffect } from "react";
import { MapView } from '../Map/Map';
import { toggleFavourites, isFavourite } from '../../pages/Favourites';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHeart as farHeart } from '@fortawesome/free-regular-svg-icons';
import { faHeart as fasHeart } from '@fortawesome/free-solid-svg-icons';

export function Listings({
    showLoading,
    showListings,
    sortBy,
    setSortBy,
    results,
    likedListings,
    setLikedListings,
    customToggleLike,
    title = "Matching Listings",
    titleClass
}) {
    const [hoveredListingUrl, setHoveredListingUrl] = useState(null);

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
        }
        return sorted;
    }, [results, sortBy]);

    return (
        <>
            {showLoading && (<div class="loader"></div>)}

            {showListings && results.length === 0 && <p className="no-listings-found">No listings found.</p>}

            {showListings && results.length != 0  && (
                <div className="listings-div" style={{ marginTop: "2rem" }}>
                    <h2 className={titleClass || "default-title"}>{title}</h2>

                    <div className='map-and-listings'>
                        <MapView listings={results} hoveredListingUrl={hoveredListingUrl} />

                        <div className='sort-btn-and-listings'>
                            <div className='listings-found-and-sort-by'>
                                <p className='listings-found'>Found {results.length} listings</p>

                                <select className="sort-by" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                                    {["⇅ Sort by", "Lowest price", "Hightest price", "Shortest distance", "Longest distance"].map((n) => (
                                        <option key={n} value={n}>{n}</option>
                                    ))}
                                </select>
                            </div>

                            <div className='listings'>
                                <ul className="listings-list">
                                    {sortedResults.map((listing, index) => {
                                        const isLiked = likedListings[index] || false;

                                        const toggleLike = () => {
                                            if (customToggleLike) {
                                                customToggleLike(listing);
                                            } else {
                                                toggleFavourites(listing.id);
                                                setLikedListings(prev => ({
                                                    ...prev,
                                                    [index]: !isLiked
                                                }));
                                            }  
                                        };

                                        return (
                                            <div
                                                className="listing-box"
                                                key={listing.url}
                                                onMouseEnter={() => setHoveredListingUrl(listing.url)}
                                                onMouseLeave={() => setHoveredListingUrl(null)}
                                            >
                                                <button className="heart-button" onClick={toggleLike}
                                                    style={isLiked ? {color: "#ff4d4d"} : {color:"grey"}}>
                                                    <FontAwesomeIcon icon={isLiked ? fasHeart : farHeart} />
                                                </button>

                                                <img src={listing.image_url} alt='' className='listing-img'/>

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

                        </div>
                    </div>
                </div>
            )}
        </>
    );
}

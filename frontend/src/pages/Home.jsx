import { useState } from "react";
import { useMemo } from "react";

import { UserInputs } from "../components/UserInputs/UserInputs";
import { Listings } from "../components/Listings/Listings";
import { isFavourite } from "./Favourites";


export function Home() {
    const [maxPrice, setMaxPrice] = useState("2500");
    const [numBeds, setNumBeds] = useState("1");
    const [minBaths, setMinBaths] = useState("1");
    const [maxWalkTime, setMaxWalkTime] = useState("20");
    const [results, setResults] = useState([]);
    const [showListings, setShowListings] = useState(false);
    const [likedListings, setLikedListings] = useState({});
    const [showLoading, setShowLoading] = useState(false);
    const [sortBy, setSortBy] = useState("");

    const API_BASE_URL = "https://uoft-housing-hub.onrender.com/api";
    
    const handleSearch = async () => {
        setShowLoading(true);
        const response = await fetch(`${API_BASE_URL}/listings`, {
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

        const liked = {};
        data.forEach((listing, index) => {
            liked[index] = isFavourite(listing.id);
        });
        setLikedListings(liked);

        setShowLoading(false);
        setShowListings(true);
    };

    
    const handleAISearch = async (query) => {
        setShowLoading(true);
        const response = await fetch(`${API_BASE_URL}/smart_search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
        });

        const data = await response.json();
        setResults(data);

        const liked = {};
        data.forEach((listing, index) => {
            liked[index] = isFavourite(listing.id);
        });
        setLikedListings(liked);

        setShowLoading(false);
        setShowListings(true);
    } 


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
            <UserInputs
                handleAISearch={handleAISearch}
                maxPrice={maxPrice}
                setMaxPrice={setMaxPrice}
                numBeds={numBeds}
                setNumBeds={setNumBeds}
                minBaths={minBaths}
                setMinBaths={setMinBaths}
                maxWalkTime={maxWalkTime}
                setMaxWalkTime={setMaxWalkTime}
                handleSearch={handleSearch}
            />
            <Listings
                showLoading={showLoading}
                showListings={showListings}
                sortBy={sortBy}
                setSortBy={setSortBy}
                results={sortedResults}
                likedListings={likedListings}
                setLikedListings={setLikedListings}
            />
        </div>
    );
}
import { Listings } from "../components/Listings/Listings";
import { useEffect, useState } from "react";

const FAV_KEY = "favouriteListingsIds";

export const getFavourites = () => {
    const raw = localStorage.getItem(FAV_KEY);
    return raw ? JSON.parse(raw) : [];
};


export const toggleFavourites = (listingsId) => {
    const current = getFavourites();
    const updated = current.includes(listingsId)
        ? current.filter((id) => id !== listingsId)
        : [...current, listingsId];
    localStorage.setItem(FAV_KEY, JSON.stringify(updated));
};


export const isFavourite = (listingsId) => {
    return getFavourites().includes(listingsId);
};


export function Favourites() {
    const [sortBy, setSortBy] = useState("");
    const [favourites, setFavourites] = useState([]);
    const [likedListings, setLikedListings] = useState({});


    useEffect(() => {
        const fetchFaves = async () => {
        const ids = getFavourites();
        const res = await fetch("http://localhost:5000/api/favourites", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ids }),
        });

        const data = await res.json();
        setFavourites(data);

        // Initialize liked state
        const liked = {};
        data.forEach((listing, index) => {
            liked[index] = true;
        });
        setLikedListings(liked);
        };

        fetchFaves();
    }, []);

    const handleToggleLike = (listing) => {
        toggleFavourites(listing.id);

        setFavourites((prev) => prev.filter((item) => item.id !== listing.id));
    };

    return (
    <Listings
        showLoading={false}
        showListings={true}
        sortBy={sortBy}
        setSortBy={setSortBy}
        results={favourites}
        likedListings={likedListings}
        setLikedListings={setLikedListings}
        customToggleLike={handleToggleLike}
        title="Favourites"
        titleClass="favourites-title"
    />
  );
}
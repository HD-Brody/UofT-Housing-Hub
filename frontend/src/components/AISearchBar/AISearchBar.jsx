import React, { useState } from "react";
import './AISearchBar.css'

export function AISearchBar({ onSearch }) {
    const [query, setQuery] = useState("")

    const handleSubmit = (e) => {
    e.preventDefault(); // prevent page reload
    if (query.trim().length > 0) {
        onSearch(query); // pass query to parent or function
        }
    };

    return (
        <div className="smart-search">
            <p className="text">Want to describe what you’re looking for? Just type below:</p>
            <form className="search-items" onSubmit={handleSubmit}>
                <input
                    className="search-bar"
                    type="search"
                    placeholder="Find me a 2-bedroom under $2200 that's close to campus"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
                <button className="search-button" type="submit">
                    AI Search
                </button>
            </form>
        </div>
    );
}

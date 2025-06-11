import React, { useState } from "react";

export function AISearchBar({ onSearch }) {
    const [query, setQuery] = useState("")

    const handleSubmit = (e) => {
    e.preventDefault(); // prevent page reload
    if (query.trim()) {
        onSearch(query); // pass query to parent or function
        }
    };

     return (
    <form onSubmit={handleSubmit}>
      <input
        type="search"
        placeholder="Describe what you're looking for..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button type="submit" style={{ padding: "0.5em 1em" }}>
        AI Search
      </button>
    </form>
  );
}

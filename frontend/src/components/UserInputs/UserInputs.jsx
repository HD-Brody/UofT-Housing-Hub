import './UserInputs.css';

export function UserInputs({
    maxPrice,
    setMaxPrice,
    numBeds,
    setNumBeds,
    minBaths,
    setMinBaths,
    maxWalkTime,
    setMaxWalkTime,
    handleSearch
}) {
    return (
        <>
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
        </>
    );
}
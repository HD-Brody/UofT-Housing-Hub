import './Navbar.css';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHouseUser } from '@fortawesome/free-solid-svg-icons';
import { faBars } from '@fortawesome/free-solid-svg-icons';
import { faXmark } from '@fortawesome/free-solid-svg-icons';

export function Navbar() {
    const [menuOpen, setMenuOpen] = useState(false);

    return (
        <nav className="navbar">
            <h2> <FontAwesomeIcon icon={faHouseUser} style={{ fontSize: "24px", color: "#3b82f6" }} /> UofT Housing Hub</h2>
            <div className="menu">
                <button className="menu-button" onClick={() => setMenuOpen(!menuOpen)}>
                    <FontAwesomeIcon icon={menuOpen ? faXmark : faBars} />
                </button>

                <ul className={menuOpen ? "menu-open" : "menuItems"} onClick={() => setMenuOpen(false)}>
                    <li><Link to="/home">Home</Link></li>
                    <li><Link to="/favourites">Favourites</Link></li>
                    <li><Link to="/about">About</Link></li>
                </ul>
            </div>
        </nav>
    );
}
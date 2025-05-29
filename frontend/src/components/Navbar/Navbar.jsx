import './Navbar.css';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHouseUser } from '@fortawesome/free-solid-svg-icons';

export function Navbar() {
  return <nav className="navbar">
            <h2> <FontAwesomeIcon icon={faHouseUser} style={{ fontSize: "24px", color: "#3b82f6" }} /> UofT Housing Hub</h2>
            <div className="menu">
            <ul className="menuItems">
                <li><Link to="/home">Home</Link></li>
                <li><Link to="/favourites">Favourites</Link></li>
                <li><Link to="/about">About</Link></li>
            </ul>
            </div>
        </nav>;
}
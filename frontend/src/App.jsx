import { Routes, Route, Link } from "react-router-dom";
import { Home } from "./pages/Home";
import { Favourites } from "./pages/Favourites";
import { About } from "./pages/About";
import { faHouseUser } from '@fortawesome/free-solid-svg-icons';

function App() {
  return (
    <>
      <nav className="navbar">
        <h2>UofT Housing Hub</h2>
        <div className="menu">
          <ul className="menuItems">
            <li><Link to="/home">Home</Link></li>
            <li><Link to="/favourites">Favourites</Link></li>
            <li><Link to="/about">About</Link></li>
          </ul>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/home" element={<Home />} />
        <Route path="/favourites" element={<Favourites />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </>
  );
}

export default App;

import { Routes, Route } from "react-router-dom";
import { Home } from "./pages/Home";
import { Favourites } from "./pages/Favourites";
import { About } from "./pages/About";

import { Navbar } from "./components/Navbar/Navbar";

function App() {
  return (
    <>
      <Navbar />

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

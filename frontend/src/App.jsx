import { Routes, Route } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Trajets from "./pages/Trajets.jsx";
import Sante from "./pages/Sante.jsx";

// Composant racine : définit la structure commune (Layout) et les routes.
export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/trajets" element={<Trajets />} />
        <Route path="/sante" element={<Sante />} />
      </Routes>
    </Layout>
  );
}

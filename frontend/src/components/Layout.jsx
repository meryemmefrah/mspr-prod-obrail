import { NavLink } from "react-router-dom";

// Structure commune à toutes les pages : en-tête, navigation, pied de page.
// L'accessibilité est traitée ici : lien d'évitement, repères ARIA (banner,
// navigation, contentinfo), état actif de la navigation.
export default function Layout({ children }) {
  return (
    <div className="app-shell">
      {/* Lien d'évitement : permet aux utilisateurs au clavier d'aller
          directement au contenu sans parcourir toute la navigation. */}
      <a className="skip-link" href="#contenu">
        Aller au contenu principal
      </a>

      <header className="site-header" role="banner">
        <div className="container">
          <NavLink to="/" className="brand">
            <span className="brand-mark" aria-hidden="true">⬢</span>
            <span>
              ObRail Europe
              <span className="brand-sub">Observatoire ferroviaire</span>
            </span>
          </NavLink>

          <nav className="main-nav" aria-label="Navigation principale">
            <ul>
              <li>
                <NavLink to="/" end>
                  Tableau de bord
                </NavLink>
              </li>
              <li>
                <NavLink to="/trajets">Trajets</NavLink>
              </li>
              <li>
                <NavLink to="/sante">État du service</NavLink>
              </li>
            </ul>
          </nav>
        </div>
      </header>

      <main id="contenu">
        <div className="container">{children}</div>
      </main>

      <footer className="site-footer" role="contentinfo">
        <div className="container">
          ObRail Europe — Observatoire indépendant des dessertes ferroviaires
          européennes et de la mobilité durable. Données harmonisées à des fins
          d'analyse, conformément au RGPD.
        </div>
      </footer>
    </div>
  );
}

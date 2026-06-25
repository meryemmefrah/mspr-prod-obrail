// Petits composants réutilisables partagés par plusieurs pages.

/** Carte affichant un indicateur clé (valeur + libellé). */
export function StatCard({ label, value, variant = "" }) {
  return (
    <div className={`stat-card ${variant}`}>
      <p className="stat-label">{label}</p>
      <div className="stat-value">{value}</div>
    </div>
  );
}

/**
 * Message d'état standardisé (chargement, erreur, information).
 * Le rôle ARIA "status" annonce le message aux lecteurs d'écran.
 */
export function Message({ type = "loading", children }) {
  return (
    <div className={`message ${type}`} role="status">
      {children}
    </div>
  );
}

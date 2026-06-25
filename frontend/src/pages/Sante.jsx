import { useEffect, useState, useCallback } from "react";

import { getHealth } from "../api/client.js";
import { Message } from "../components/common.jsx";

export default function Sante() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastCheck, setLastCheck] = useState(null);

  const verifier = useCallback(() => {
    setLoading(true);
    setError(null);

    getHealth()
      .then((data) => {
        setHealth(data);
        setLastCheck(new Date());
      })
      .catch((err) => {
        // Si l'API renvoie 503, le client lève une erreur : on considère
        // le service comme indisponible.
        setHealth({ api_status: "error", database_status: "error" });
        setError(err.message);
        setLastCheck(new Date());
      })
      .finally(() => setLoading(false));
  }, []);

  // Vérification au chargement, puis rafraîchissement automatique toutes les 15 s.
  useEffect(() => {
    verifier();
    const interval = setInterval(verifier, 15000);
    return () => clearInterval(interval);
  }, [verifier]);

  const apiOk = health?.api_status === "ok";
  const dbOk = health?.database_status === "ok";

  return (
    <>
      <div className="page-head">
        <h1>État du service</h1>
        <p>
          Supervision en temps réel de la disponibilité de l'API et de la base de
          données. Cette page se rafraîchit automatiquement toutes les 15 secondes.
        </p>
      </div>

      {loading && !health && (
        <Message type="loading">Vérification de l'état du service…</Message>
      )}

      {health && (
        <section className="panel" aria-label="Statut des composants">
          <h2>Composants</h2>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "1rem",
                flexWrap: "wrap",
              }}
            >
              <span>Interface de programmation (API)</span>
              <span className={`status-badge ${apiOk ? "ok" : "error"}`}>
                <span className="status-dot" aria-hidden="true" />
                {apiOk ? "Opérationnelle" : "Indisponible"}
              </span>
            </div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "1rem",
                flexWrap: "wrap",
              }}
            >
              <span>Base de données (PostgreSQL)</span>
              <span className={`status-badge ${dbOk ? "ok" : "error"}`}>
                <span className="status-dot" aria-hidden="true" />
                {dbOk ? "Connectée" : "Injoignable"}
              </span>
            </div>
          </div>

          {lastCheck && (
            <p style={{ marginBottom: 0, marginTop: "1.25rem", color: "var(--color-ink-soft)", fontSize: "0.85rem" }}>
              Dernière vérification : {lastCheck.toLocaleTimeString("fr-FR")}
            </p>
          )}

          <div style={{ marginTop: "1rem" }}>
            <button type="button" className="btn btn-ghost" onClick={verifier}>
              Vérifier maintenant
            </button>
          </div>
        </section>
      )}

      {error && (
        <Message type="error">
          Le service signale une anomalie : {error}
        </Message>
      )}

      <section className="panel">
        <h2>Supervision avancée</h2>
        <p style={{ marginBottom: 0 }}>
          Les métriques détaillées (latence, taux d'erreurs, volumétrie) sont
          disponibles dans les tableaux de bord Grafana, alimentés par Prometheus.
          Cette page offre une vue synthétique destinée à tous les publics.
        </p>
      </section>
    </>
  );
}

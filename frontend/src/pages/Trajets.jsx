import { useEffect, useState } from "react";

import { getTrajets } from "../api/client.js";
import { Message } from "../components/common.jsx";

// Valeurs initiales des filtres.
const EMPTY_FILTERS = {
  train_type: "",
  departure_city: "",
  arrival_city: "",
};

export default function Trajets() {
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [trajets, setTrajets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Charge les trajets en appliquant les filtres courants.
  function chargerTrajets(activeFilters) {
    setLoading(true);
    setError(null);

    getTrajets({ ...activeFilters, limit: 100 })
      .then((data) => setTrajets(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  // Premier chargement : tous les trajets (sans filtre).
  useEffect(() => {
    chargerTrajets(EMPTY_FILTERS);
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    chargerTrajets(filters);
  }

  function handleReset() {
    setFilters(EMPTY_FILTERS);
    chargerTrajets(EMPTY_FILTERS);
  }

  return (
    <>
      <div className="page-head">
        <h1>Trajets ferroviaires</h1>
        <p>
          Consultez et filtrez les dessertes ferroviaires européennes harmonisées.
          Recherchez par type de train, ville de départ ou d'arrivée.
        </p>
      </div>

      {/* Formulaire de filtres */}
      <section className="panel" aria-label="Filtres de recherche">
        <form onSubmit={handleSubmit}>
          <div className="filters">
            <div className="field">
              <label htmlFor="train_type">Type de train</label>
              <select
                id="train_type"
                name="train_type"
                value={filters.train_type}
                onChange={handleChange}
              >
                <option value="">Tous</option>
                <option value="day">Jour</option>
                <option value="night">Nuit</option>
              </select>
            </div>

            <div className="field">
              <label htmlFor="departure_city">Ville de départ</label>
              <input
                id="departure_city"
                name="departure_city"
                type="text"
                placeholder="ex : Paris"
                value={filters.departure_city}
                onChange={handleChange}
              />
            </div>

            <div className="field">
              <label htmlFor="arrival_city">Ville d'arrivée</label>
              <input
                id="arrival_city"
                name="arrival_city"
                type="text"
                placeholder="ex : Berlin"
                value={filters.arrival_city}
                onChange={handleChange}
              />
            </div>

            <div className="field" style={{ display: "flex", gap: "0.5rem" }}>
              <button type="submit" className="btn btn-primary">
                Rechercher
              </button>
              <button type="button" className="btn btn-ghost" onClick={handleReset}>
                Réinitialiser
              </button>
            </div>
          </div>
        </form>
      </section>

      {/* Résultats */}
      {loading && <Message type="loading">Chargement des trajets…</Message>}

      {error && <Message type="error">{error}</Message>}

      {!loading && !error && trajets.length === 0 && (
        <Message type="loading">
          Aucun trajet ne correspond à ces critères. Modifiez les filtres et
          relancez la recherche.
        </Message>
      )}

      {!loading && !error && trajets.length > 0 && (
        <section className="panel" aria-label="Résultats">
          <p style={{ marginTop: 0, color: "var(--color-ink-soft)" }}>
            {trajets.length} trajet(s) affiché(s).
          </p>
          <div className="table-wrap">
            <table className="data">
              <caption className="sr-only">Liste des trajets ferroviaires</caption>
              <thead>
                <tr>
                  <th scope="col">Type</th>
                  <th scope="col">Départ</th>
                  <th scope="col">Arrivée</th>
                  <th scope="col">Opérateur</th>
                  <th scope="col">Durée (min)</th>
                  <th scope="col">Source</th>
                </tr>
              </thead>
              <tbody>
                {trajets.map((t) => (
                  <tr key={t.trip_id}>
                    <td>
                      <span className={`tag ${t.train_type}`}>
                        {t.train_type === "night" ? "Nuit" : "Jour"}
                      </span>
                    </td>
                    <td>
                      {t.departure_city}
                      <br />
                      <small style={{ color: "var(--color-ink-soft)" }}>
                        {t.departure_station}
                      </small>
                    </td>
                    <td>
                      {t.arrival_city}
                      <br />
                      <small style={{ color: "var(--color-ink-soft)" }}>
                        {t.arrival_station}
                      </small>
                    </td>
                    <td>{t.operator_name}</td>
                    <td>{t.duration_minutes ?? "—"}</td>
                    <td>{t.source_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </>
  );
}

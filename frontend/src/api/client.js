// ============================================================
// Client API - ObRail Europe
// ============================================================
// Centralise tous les appels au backend FastAPI. Le reste de
// l'application n'a pas besoin de connaître l'URL de l'API ni
// les détails techniques des requêtes HTTP.
// ============================================================

// L'URL de base de l'API est lue depuis la variable d'environnement Vite.
// En local : http://localhost:8000. En production, elle est injectée au build.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Effectue un appel GET sur l'API et renvoie la réponse JSON.
 * Lève une erreur explicite si la requête échoue, pour que les pages
 * puissent afficher un message clair à l'utilisateur.
 */
async function apiGet(path) {
  const url = `${API_BASE_URL}${path}`;

  let response;
  try {
    response = await fetch(url);
  } catch (networkError) {
    throw new Error(
      "Impossible de joindre le service. Verifiez que l'API est demarree."
    );
  }

  if (!response.ok) {
    throw new Error(`Le service a repondu avec une erreur (code ${response.status}).`);
  }

  return response.json();
}

/** Construit une chaîne de paramètres de requête à partir d'un objet, en ignorant les valeurs vides. */
function buildQuery(params) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.append(key, value);
    }
  });
  const queryString = search.toString();
  return queryString ? `?${queryString}` : "";
}

// ------------------------------------------------------------
// Fonctions exposées aux pages
// ------------------------------------------------------------

/** État de santé de l'API et de la base de données. */
export function getHealth() {
  return apiGet("/health");
}

/** Indicateurs de volumes : total, répartition jour/nuit, par opérateur. */
export function getVolumes() {
  return apiGet("/stats/volumes");
}

/** Statistiques de qualité globales des données. */
export function getQualityStats() {
  return apiGet("/stats/quality");
}

/** Liste des trajets avec filtres optionnels. */
export function getTrajets(filters = {}) {
  return apiGet(`/trajets${buildQuery(filters)}`);
}

/** Détail d'un trajet par identifiant. */
export function getTrajet(id) {
  return apiGet(`/trajets/${id}`);
}

/** Liste des opérateurs ferroviaires (pour alimenter les filtres). */
export function getOperators() {
  return apiGet("/operators");
}

export { API_BASE_URL };

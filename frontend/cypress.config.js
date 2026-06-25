import { defineConfig } from "cypress";

// Configuration Cypress pour les tests end-to-end (E2E) du frontend.
// Les tests vérifient le parcours utilisateur réel dans un navigateur.
export default defineConfig({
  e2e: {
    // URL de base du frontend testé.
    baseUrl: "http://localhost:5173",
    // Dossier contenant les tests E2E.
    specPattern: "cypress/e2e/**/*.cy.js",
    supportFile: false,
    video: false,
    // Délai d'attente par défaut (pratique quand l'API met un peu de temps).
    defaultCommandTimeout: 8000,
  },
});

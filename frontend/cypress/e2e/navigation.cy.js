// ============================================================
// Tests end-to-end (E2E) - ObRail Europe
// ============================================================
// Ces tests simulent un véritable utilisateur dans le navigateur :
// ils ouvrent l'application, naviguent entre les pages et vérifient
// que les éléments clés s'affichent.
//
// Prérequis : la solution complète doit tourner (docker compose up),
// avec le frontend accessible sur http://localhost:5173 et l'API
// alimentée.
// ============================================================

describe("Navigation et pages principales", () => {
  it("affiche le tableau de bord avec les indicateurs clés", () => {
    cy.visit("/");

    // Le titre principal est présent.
    cy.contains("h1", "Tableau de bord").should("be.visible");

    // Les cartes d'indicateurs sont affichées.
    cy.contains("Trajets recensés").should("be.visible");
    cy.contains("Trains de jour").should("be.visible");
    cy.contains("Trains de nuit").should("be.visible");
  });

  it("permet de naviguer vers la page Trajets", () => {
    cy.visit("/");

    // Clic sur le lien de navigation "Trajets".
    cy.get("nav").contains("Trajets").click();

    // L'URL et le titre changent.
    cy.url().should("include", "/trajets");
    cy.contains("h1", "Trajets ferroviaires").should("be.visible");

    // Le formulaire de filtres est présent.
    cy.get("#train_type").should("exist");
    cy.get("#departure_city").should("exist");
  });

  it("affiche des trajets dans le tableau de résultats", () => {
    cy.visit("/trajets");

    // Le tableau de résultats doit contenir au moins une ligne de données.
    cy.get("table.data tbody tr", { timeout: 10000 })
      .its("length")
      .should("be.greaterThan", 0);
  });

  it("filtre les trajets par type de train", () => {
    cy.visit("/trajets");

    // On sélectionne "Nuit" et on lance la recherche.
    cy.get("#train_type").select("night");
    cy.contains("button", "Rechercher").click();

    // Les résultats affichés doivent porter l'étiquette "Nuit".
    cy.get("table.data tbody tr", { timeout: 10000 }).should("exist");
    cy.get("table.data tbody").contains("Nuit").should("exist");
  });

  it("affiche l'état du service", () => {
    cy.visit("/sante");

    cy.contains("h1", "État du service").should("be.visible");

    // Les composants supervisés sont listés.
    cy.contains("Interface de programmation (API)").should("be.visible");
    cy.contains("Base de données (PostgreSQL)").should("be.visible");
  });
});

describe("Accessibilité de base", () => {
  it("propose un lien d'évitement vers le contenu", () => {
    cy.visit("/");
    cy.get(".skip-link").should("exist");
  });

  it("définit la langue de la page en français", () => {
    cy.visit("/");
    cy.get("html").should("have.attr", "lang", "fr");
  });
});

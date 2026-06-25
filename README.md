# ObRail Europe — Mise en production de la solution (MSPR TPRE532 / Bloc 3)

Industrialisation et mise en production de la solution applicative ObRail Europe :
observatoire des dessertes ferroviaires européennes (trains de jour / trains de nuit)
au service de la mobilité durable.

Ce dépôt correspond au **Bloc 3 — Produire et maintenir une solution I.A**. Il part
du socle technique des MSPR précédentes (entrepôt de données harmonisé + API REST +
modèle d'IA de substitution avion/train) et le transforme en une **application web
complète, conteneurisée, testée, supervisée et déployée en continu (CI/CD)**.

## Architecture de la solution

| Composant | Rôle | Technologie |
|---|---|---|
| **Base de données** | Persistance des données ferroviaires harmonisées | PostgreSQL 16 |
| **Backend** | API REST + endpoint IA `/predict` | FastAPI (Python 3.11) |
| **Frontend** | Interface de consultation et de visualisation | React |
| **Monitoring** | Métriques (latence, erreurs, disponibilité) + tableaux de bord | Prometheus + Grafana |
| **CI/CD** | Tests, build d'images, livraison continue | GitHub Actions |
| **Orchestration** | Démarrage coordonné de tous les services | Docker Compose |

## Démarrage rapide

> Prérequis : Docker et Docker Compose installés.

```bash
# 1. Copier le fichier d'environnement et l'adapter si besoin
cp .env.example .env

# 2. Lancer toute la solution en une seule commande
docker compose up -d
```

Une fois démarré :

| Service | URL |
|---|---|
| API (documentation Swagger) | http://localhost:8000/docs |
| Frontend | http://localhost:5173 |
| Grafana (monitoring) | http://localhost:3000 |
| Prometheus | http://localhost:9090 |

## Structure du dépôt

```
.
├── backend/            API FastAPI, scripts ETL/ML, tests, modèle
├── frontend/           Application React
├── monitoring/         Configuration Prometheus + Grafana
├── docs/               Documentation (RGPD, dictionnaire de données, etc.)
├── .github/workflows/  Pipelines CI/CD (GitHub Actions)
├── docker-compose.yml  Orchestration de l'ensemble des services
├── .env.example        Modèle de configuration (sans secret)
└── README.md
```

## Documentation

- Rapport technique complet : `docs/rapport_technique.md`
- Conformité RGPD : `docs/RGPD.md`
- Dictionnaire des données : `docs/dictionnaire_donnees.md`

---

*Projet pédagogique réalisé dans le cadre de la certification Développeur en
Intelligence Artificielle et Data Science (RNCP 36581 / RNCP 37827) — EPSI.*

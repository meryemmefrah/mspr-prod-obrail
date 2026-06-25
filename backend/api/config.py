"""
Configuration centralisée de l'API ObRail Europe.

Ce module regroupe en un seul endroit tous les paramètres de l'application qui
peuvent changer selon l'environnement (développement local, conteneur Docker,
production). Les valeurs sont lues depuis les variables d'environnement, avec
des valeurs par défaut raisonnables pour un démarrage en local.

Centraliser la configuration évite de disperser des os.getenv(...) un peu
partout dans le code et facilite la maintenance.
"""

import os

from dotenv import load_dotenv


# Charge le fichier .env s'il existe (utile en local hors Docker).
# En conteneur, les variables sont injectées par docker-compose.
load_dotenv()


def _parse_cors_origins(raw_value: str) -> list[str]:
    """
    Transforme une liste d'origines séparées par des virgules en liste Python.

    Exemple : "http://localhost:5173,http://localhost:3000"
    devient   ["http://localhost:5173", "http://localhost:3000"]
    """
    if not raw_value:
        return []

    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


# ------------------------------------------------------------
# Paramètres de connexion à la base de données PostgreSQL
# ------------------------------------------------------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "obrail"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}


# ------------------------------------------------------------
# Paramètres applicatifs de l'API
# ------------------------------------------------------------

# Origines autorisées à appeler l'API depuis un navigateur (CORS).
# Le frontend React (Vite) tourne par défaut sur le port 5173.
CORS_ORIGINS = _parse_cors_origins(
    os.getenv("API_CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
)

# Niveau de journalisation : DEBUG, INFO, WARNING, ERROR.
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Métadonnées de l'API exposées dans la documentation Swagger.
API_TITLE = "ObRail Europe API"
API_VERSION = "2.0.0"
API_DESCRIPTION = (
    "API REST ObRail permettant de consulter les données ferroviaires "
    "transformées dans PostgreSQL et d'exposer le modèle IA de substitution "
    "avion-train. Version industrialisée (Bloc 3 - mise en production)."
)

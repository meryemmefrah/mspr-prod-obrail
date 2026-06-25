"""
Couche d'accès à la base de données PostgreSQL.

Ce module centralise la connexion à PostgreSQL et l'exécution des requêtes.
Le reste de l'API n'a ainsi pas besoin de connaître les détails techniques
(host, port, mot de passe, sérialisation JSON...).
"""

import logging
from decimal import Decimal
from datetime import date, datetime, time

import psycopg2
from psycopg2.extras import RealDictCursor

from api.config import DB_CONFIG


logger = logging.getLogger("obrail.database")


def get_connection():
    """
    Crée une nouvelle connexion à la base PostgreSQL.

    Chaque requête ouvre une connexion puis la referme proprement. Cette
    approche simple convient au volume de ce projet ; pour une charge plus
    élevée, on utiliserait un pool de connexions.
    """
    return psycopg2.connect(**DB_CONFIG)


def serialize_value(value):
    """
    Transforme une valeur PostgreSQL en valeur compatible avec une réponse JSON.

    Certains types renvoyés par PostgreSQL (Decimal, date, datetime, time)
    ne sont pas directement sérialisables en JSON et doivent être convertis.
    """
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (date, datetime, time)):
        return value.isoformat()

    return value


def serialize_row(row: dict) -> dict:
    """Convertit une ligne SQL complète en dictionnaire compatible JSON."""
    return {key: serialize_value(value) for key, value in row.items()}


def execute_query(query: str, params: tuple | list | None = None, fetch_one: bool = False):
    """
    Exécute une requête SQL et retourne le résultat sous forme de dictionnaire.

    - query : la requête SQL à exécuter.
    - params : les valeurs utilisées dans les filtres SQL (requêtes paramétrées,
      ce qui protège contre les injections SQL).
    - fetch_one : récupère une seule ligne au lieu d'une liste.

    RealDictCursor permet d'obtenir des résultats lisibles, avec le nom des
    colonnes comme clés.
    """
    connection = get_connection()

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)

            if fetch_one:
                row = cursor.fetchone()
                return serialize_row(row) if row else None

            rows = cursor.fetchall()
            return [serialize_row(row) for row in rows]

    finally:
        connection.close()


def check_database() -> bool:
    """
    Vérifie que la base de données est joignable et répond.

    Contrairement à execute_query, cette fonction ne lève jamais d'exception :
    elle renvoie True si la base répond, False sinon. Elle est utilisée par
    l'endpoint /health pour déterminer l'état de santé du service sans faire
    planter l'API si la base est momentanément indisponible.
    """
    try:
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
            return True
        finally:
            connection.close()
    except Exception as exc:
        logger.warning("Base de donnees injoignable : %s", exc)
        return False

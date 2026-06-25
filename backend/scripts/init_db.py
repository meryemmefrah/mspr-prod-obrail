"""
Initialisation de la base de données PostgreSQL pour l'environnement conteneurisé.

Ce script est appelé automatiquement au démarrage du conteneur API. Il :
  1. crée les tables à partir du schéma SQL,
  2. importe les données transformées (CSV) dans le bon ordre,
  3. ne fait rien si la base est déjà initialisée (idempotent).

Contrairement à scripts/loading/load_to_postgres.py (qui visait une exécution
manuelle en local), cette version lit sa configuration depuis les variables
d'environnement et utilise des chemins absolus, afin de fonctionner dans Docker.
"""

import os
from pathlib import Path

import psycopg2


# Configuration lue depuis l'environnement (injectée par docker-compose).
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "obrail"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

# Racine du backend dans le conteneur (/app).
BACKEND_ROOT = Path(__file__).resolve().parents[1]
SQL_FILE = BACKEND_ROOT / "sql" / "create_tables.sql"
PROCESSED_DIR = BACKEND_ROOT / "data" / "processed"

# Ordre de chargement respectant les dépendances de clés étrangères.
LOAD_ORDER = [
    ("country", "country.csv"),
    ("city", "city.csv"),
    ("station", "station.csv"),
    ('"operator"', "operator.csv"),
    ("train_type", "train_type.csv"),
    ("data_source", "data_source.csv"),
    ("route", "route.csv"),
    ("trip", "trip.csv"),
    ("trip_stop", "trip_stop.csv"),
    ("quality_check", "quality_check.csv"),
]


def get_connection():
    """Ouvre une connexion PostgreSQL avec la configuration de l'environnement."""
    return psycopg2.connect(**DB_CONFIG)


def database_already_initialized(connection) -> bool:
    """
    Vérifie si la base est déjà initialisée.

    On considère qu'elle l'est si la table 'trip' existe et contient des lignes.
    Cela rend le script idempotent : relancer le conteneur ne recharge pas
    inutilement les données.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass('public.trip');")
            table_exists = cursor.fetchone()[0] is not None

            if not table_exists:
                return False

            cursor.execute("SELECT COUNT(*) FROM trip;")
            count = cursor.fetchone()[0]
            return count > 0
    except Exception:
        return False


def execute_sql_file(connection, sql_file: Path):
    """Exécute le script SQL de création des tables."""
    if not sql_file.exists():
        raise FileNotFoundError(f"Fichier SQL introuvable : {sql_file}")

    print(f"[init] Execution du script SQL : {sql_file}")

    with open(sql_file, "r", encoding="utf-8") as file:
        sql_script = file.read()

    with connection.cursor() as cursor:
        cursor.execute(sql_script)

    connection.commit()
    print("[init] Tables creees avec succes")


def load_csv_to_table(connection, table_name: str, csv_file: str):
    """Charge un fichier CSV dans une table via la commande COPY."""
    csv_path = PROCESSED_DIR / csv_file

    if not csv_path.exists():
        raise FileNotFoundError(f"Fichier CSV introuvable : {csv_path}")

    print(f"[init] Chargement de {csv_file} -> {table_name}")

    copy_sql = f"""
        COPY {table_name}
        FROM STDIN
        WITH (FORMAT CSV, HEADER TRUE, NULL '', DELIMITER ',');
    """

    with connection.cursor() as cursor:
        with open(csv_path, "r", encoding="utf-8") as file:
            cursor.copy_expert(copy_sql, file)

    connection.commit()


def main():
    """Initialise la base si nécessaire."""
    print("[init] Verification de l'etat de la base de donnees...")

    connection = get_connection()

    try:
        if database_already_initialized(connection):
            print("[init] Base deja initialisee : aucun chargement necessaire.")
            return

        print("[init] Base vide : creation du schema et chargement des donnees.")
        execute_sql_file(connection, SQL_FILE)

        for table_name, csv_file in LOAD_ORDER:
            load_csv_to_table(connection, table_name, csv_file)

        print("[init] Chargement termine avec succes.")

    except Exception as error:
        connection.rollback()
        print(f"[init][ERREUR] Echec de l'initialisation : {error}")
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()

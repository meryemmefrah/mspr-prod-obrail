#!/bin/sh
# ============================================================
# Entrypoint du conteneur API - ObRail Europe
# ============================================================
# Ce script orchestre le démarrage du backend :
#   1. attend que PostgreSQL soit prêt à accepter des connexions,
#   2. initialise la base (tables + données) si elle est vide,
#   3. lance le serveur API.
# Cela permet à un évaluateur de tout démarrer avec une seule
# commande (docker compose up), sans étape manuelle.
# ============================================================

set -e

echo "[entrypoint] Attente de PostgreSQL (${DB_HOST}:${DB_PORT})..."

# On attend que la base réponde avant de continuer.
# La boucle teste la connexion toutes les 2 secondes.
until python -c "
import os, sys, psycopg2
try:
    psycopg2.connect(
        host=os.getenv('DB_HOST', 'postgres'),
        port=int(os.getenv('DB_PORT', '5432')),
        dbname=os.getenv('DB_NAME', 'obrail'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
    ).close()
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  echo "[entrypoint] PostgreSQL pas encore pret, nouvelle tentative dans 2s..."
  sleep 2
done

echo "[entrypoint] PostgreSQL est pret."

# Initialisation de la base (idempotent : ne recharge pas si deja fait).
echo "[entrypoint] Initialisation de la base de donnees..."
python scripts/init_db.py

# Demarrage du serveur API.
echo "[entrypoint] Demarrage de l'API FastAPI..."
exec uvicorn api.main:app --host 0.0.0.0 --port 8000

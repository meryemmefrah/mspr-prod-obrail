# ============================================================
# Dockerfile - Backend API ObRail Europe
# ============================================================
# Construit l'image de l'API FastAPI. L'image démarre via un
# entrypoint qui attend la base, l'initialise puis lance l'API.
# ============================================================

FROM python:3.11-slim

# Dossier de travail dans le conteneur.
WORKDIR /app

# Bonnes pratiques Python en conteneur :
# - PYTHONDONTWRITEBYTECODE : pas de fichiers .pyc.
# - PYTHONUNBUFFERED : logs affichés immédiatement (utile pour la supervision).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Installation des dépendances système minimales nécessaires à psycopg2,
# puis nettoyage du cache apt pour garder l'image légère.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copie d'abord le fichier des dépendances pour profiter du cache Docker :
# tant que requirements.txt ne change pas, cette couche est réutilisée.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code de l'application.
COPY . .

# Rend l'entrypoint exécutable.
RUN chmod +x entrypoint.sh

# Sécurité : on crée un utilisateur non privilégié et on lui donne la main,
# afin de ne pas exécuter l'application en tant que root.
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# Port exposé par l'API (documentaire ; le mapping réel est dans compose).
EXPOSE 8000

# Au démarrage : attente DB -> init -> lancement API.
ENTRYPOINT ["./entrypoint.sh"]

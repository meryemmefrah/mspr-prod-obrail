# ============================================================
# Dockerfile - Frontend React ObRail Europe
# ============================================================
# Construction en deux étapes (multi-stage) :
#   1. "build"  : compile l'application React avec Node + Vite.
#   2. "runtime": sert les fichiers statiques avec Nginx (léger).
# Cette approche produit une image finale petite et rapide,
# sans les outils de build inutiles en production.
# ============================================================

# ----- Étape 1 : build -----
FROM node:20-alpine AS build

WORKDIR /app

# Installation des dépendances (cache Docker sur package.json).
COPY package.json package-lock.json ./
RUN npm ci

# Copie du code et build de production.
COPY . .

# L'URL de l'API est injectée au build (variable Vite).
# Valeur par défaut : l'API exposée sur le port 8000 de la machine hôte.
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# ----- Étape 2 : runtime (Nginx) -----
FROM nginx:1.27-alpine AS runtime

# Configuration Nginx adaptée à une application monopage (SPA).
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copie des fichiers compilés depuis l'étape de build.
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

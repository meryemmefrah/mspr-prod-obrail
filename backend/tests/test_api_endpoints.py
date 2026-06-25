"""
Tests unitaires des endpoints "production" de l'API.

Ces tests vérifient le comportement des routes ajoutées ou durcies lors de la
mise en production (/, /health, /trajets, /stats/volumes), sans dépendre d'une
vraie base de données : la couche d'accès aux données est simulée (mockée).

Cela permet de les exécuter rapidement et dans n'importe quel environnement,
y compris dans la chaîne d'intégration continue (CI) où PostgreSQL peut être
absent.
"""

from pathlib import Path
import sys

from fastapi.testclient import TestClient

import api.main as main_module
from api.main import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


client = TestClient(app)


# ------------------------------------------------------------
# Endpoint racine
# ------------------------------------------------------------
def test_root_endpoint_returns_running_status():
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "documentation" in data


# ------------------------------------------------------------
# Endpoint /health
# ------------------------------------------------------------
def test_health_returns_200_when_database_is_up(monkeypatch):
    # On simule une base joignable.
    monkeypatch.setattr(main_module, "check_database", lambda: True)

    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["api_status"] == "ok"
    assert data["database_status"] == "ok"


def test_health_returns_503_when_database_is_down(monkeypatch):
    # On simule une base injoignable : l'API doit se déclarer dégradée (503).
    monkeypatch.setattr(main_module, "check_database", lambda: False)

    response = client.get("/health")

    assert response.status_code == 503
    data = response.json()
    assert data["database_status"] == "error"


# ------------------------------------------------------------
# Endpoint /trajets (alias FR)
# ------------------------------------------------------------
def test_trajets_returns_data_from_query(monkeypatch):
    # On simule la réponse de la base.
    fake_rows = [
        {
            "trip_id": 1,
            "train_type": "night",
            "departure_city": "Paris",
            "arrival_city": "Berlin",
            "operator_name": "Test Operator",
            "duration_minutes": 480,
            "source_name": "test_source",
        }
    ]
    monkeypatch.setattr(main_module, "execute_query", lambda *args, **kwargs: fake_rows)

    response = client.get("/trajets")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["departure_city"] == "Paris"


def test_trajets_rejects_invalid_limit():
    # limit hors bornes (> 1000) doit être refusé par la validation FastAPI.
    response = client.get("/trajets?limit=99999")

    assert response.status_code == 422


# ------------------------------------------------------------
# Endpoint /stats/volumes
# ------------------------------------------------------------
def test_stats_volumes_aggregates_results(monkeypatch):
    # execute_query est appelé trois fois (total, par type, par opérateur).
    # On renvoie des valeurs différentes selon la forme attendue.
    def fake_execute_query(query, params=None, fetch_one=False):
        if fetch_one:
            return {"total_trips": 1500}
        if "train_type" in query:
            return [
                {"type_name": "day", "total_trips": 1000},
                {"type_name": "night", "total_trips": 500},
            ]
        return [{"operator_name": "SNCF", "total_trips": 800}]

    monkeypatch.setattr(main_module, "execute_query", fake_execute_query)

    response = client.get("/stats/volumes")

    assert response.status_code == 200
    data = response.json()
    assert data["total_trips"] == 1500
    assert len(data["by_train_type"]) == 2
    assert data["by_operator"][0]["operator_name"] == "SNCF"


# ------------------------------------------------------------
# Documentation OpenAPI
# ------------------------------------------------------------
def test_openapi_documentation_is_available():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]

    # Les endpoints clés du cahier des charges doivent être documentés.
    for endpoint in ["/health", "/trajets", "/trajets/{trip_id}", "/stats/volumes", "/predict"]:
        assert endpoint in paths, f"Endpoint non documenté : {endpoint}"

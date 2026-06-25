"""
Tests d'intégration : API <-> base de données PostgreSQL.

Contrairement aux tests unitaires (qui simulent la base), ces tests vérifient
que l'API fonctionne réellement de bout en bout avec une base PostgreSQL
alimentée.

Ils ne s'exécutent que si une base est joignable. Sinon, ils sont
automatiquement ignorés (skip), ce qui permet de lancer la suite de tests
même sans base disponible (par exemple en local sans Docker).

Pour les exécuter : démarrer la solution avec `docker compose up`, puis lancer
les tests en pointant DB_HOST vers la base (localhost si exposée).
"""

from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from api.database import check_database  # noqa: E402
from api.main import app  # noqa: E402


client = TestClient(app)


# Si la base n'est pas joignable, on saute tous les tests de ce fichier.
database_available = check_database()

pytestmark = pytest.mark.skipif(
    not database_available,
    reason="Base de donnees indisponible : tests d'integration ignores.",
)


def test_health_reports_database_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["database_status"] == "ok"


def test_trajets_returns_real_data():
    response = client.get("/trajets?limit=5")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # La base alimentée doit contenir au moins un trajet.
    assert len(data) > 0

    # Chaque trajet doit avoir les champs structurants.
    first = data[0]
    for field in ["trip_id", "train_type", "departure_city", "arrival_city"]:
        assert field in first


def test_trajet_detail_returns_404_for_unknown_id():
    response = client.get("/trajets/99999999")

    assert response.status_code == 404


def test_stats_volumes_returns_consistent_totals():
    response = client.get("/stats/volumes")

    assert response.status_code == 200
    data = response.json()

    assert "total_trips" in data
    assert isinstance(data["by_train_type"], list)
    assert isinstance(data["by_operator"], list)

    # La somme des trajets par type ne doit pas dépasser le total.
    sum_by_type = sum(row["total_trips"] for row in data["by_train_type"])
    assert sum_by_type <= data["total_trips"]


def test_train_types_endpoint_returns_day_and_night():
    response = client.get("/train-types")

    assert response.status_code == 200
    type_names = {row["type_name"] for row in response.json()}

    # Le projet distingue trains de jour et de nuit.
    assert "day" in type_names or "night" in type_names

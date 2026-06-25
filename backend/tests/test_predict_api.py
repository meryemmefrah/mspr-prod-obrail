from pathlib import Path
import sys

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from api.main import app  # noqa: E402


client = TestClient(app)


VALID_PAYLOAD = {
    "is_international": 1,
    "distance_km": 850.0,
    "weekly_frequency": 7.0,
    "daily_frequency_avg": 1.0,
    "avg_duration_minutes": 480.0,
    "min_duration_minutes": 450.0,
    "max_duration_minutes": 520.0,
    "has_night_train": 1,
    "has_day_train": 0,
    "avg_num_stops": 6.0,
    "avg_quality_score": 85.0,
    "quality_issues_count": 0,
    "co2_train_kg": 11.9,
    "co2_plane_kg": 195.5,
    "co2_saving_kg": 183.6,
    "co2_saving_percent": 93.9,
}


def test_model_info_endpoint_returns_model_metadata():
    response = client.get("/model-info")

    assert response.status_code == 200

    data = response.json()

    assert "best_model" in data
    assert "target_column" in data
    assert "feature_columns" in data
    assert "test_metrics" in data

    assert data["target_column"] == "substitution_potential"
    assert isinstance(data["feature_columns"], list)
    assert "substitution_score" not in data["feature_columns"]


def test_predict_endpoint_returns_valid_prediction():
    response = client.post("/predict", json=VALID_PAYLOAD)

    assert response.status_code == 200

    data = response.json()

    assert "prediction" in data
    assert "input" in data
    assert "probabilities" in data
    assert "confidence" in data

    assert data["prediction"] in {"faible", "moyen", "fort"}
    assert set(data["probabilities"].keys()) == {"faible", "moyen", "fort"}
    assert 0 <= data["confidence"] <= 1


def test_predict_endpoint_default_business_case_is_fort():
    response = client.post("/predict", json=VALID_PAYLOAD)

    assert response.status_code == 200

    data = response.json()

    assert data["prediction"] == "fort"


def test_predict_endpoint_rejects_invalid_distance():
    invalid_payload = VALID_PAYLOAD.copy()
    invalid_payload["distance_km"] = 0

    response = client.post("/predict", json=invalid_payload)

    assert response.status_code == 422


def test_predict_endpoint_rejects_missing_required_field():
    invalid_payload = VALID_PAYLOAD.copy()
    invalid_payload.pop("distance_km")

    response = client.post("/predict", json=invalid_payload)

    assert response.status_code == 422
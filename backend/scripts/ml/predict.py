from pathlib import Path
import argparse
import json
import pandas as pd
import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODELS_DIR = PROJECT_ROOT / "models"
PREDICTIONS_DIR = PROJECT_ROOT / "data" / "predictions"

MODEL_PATH = MODELS_DIR / "substitution_model.joblib"
METRICS_PATH = MODELS_DIR / "model_metrics.json"

OUTPUT_PATH = PREDICTIONS_DIR / "last_prediction.json"


DEFAULT_SAMPLE = {
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


def load_feature_columns():
    if not METRICS_PATH.exists():
        raise FileNotFoundError(f"Fichier métriques introuvable : {METRICS_PATH}")

    with open(METRICS_PATH, "r", encoding="utf-8") as file:
        metrics = json.load(file)

    feature_columns = metrics.get("feature_columns")

    if not feature_columns:
        raise ValueError("Aucune liste de variables trouvée dans model_metrics.json")

    return feature_columns


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Modèle introuvable : {MODEL_PATH}")

    return joblib.load(MODEL_PATH)


def load_input_data(input_json):
    if input_json is None:
        return DEFAULT_SAMPLE

    input_path = Path(input_json)

    # Si le chemin est relatif, on teste aussi depuis la racine du projet
    possible_paths = [
        input_path,
        PROJECT_ROOT / input_path,
    ]

    for path in possible_paths:
        if path.exists():
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)

    try:
        return json.loads(input_json)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Entrée invalide : {input_json}\n"
            "L'entrée doit être soit un chemin vers un fichier JSON existant, "
            "soit une chaîne JSON valide."
        ) from exc


def validate_input(input_data, feature_columns):
    missing_columns = [
        column for column in feature_columns if column not in input_data
    ]

    if missing_columns:
        raise ValueError(
            f"Variables manquantes dans les données d'entrée : {missing_columns}"
        )

    prediction_df = pd.DataFrame([input_data])
    prediction_df = prediction_df[feature_columns]

    return prediction_df


def predict(input_data):
    model = load_model()
    feature_columns = load_feature_columns()

    prediction_df = validate_input(input_data, feature_columns)

    predicted_class = model.predict(prediction_df)[0]

    result = {
        "prediction": predicted_class,
        "input": input_data,
    }

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(prediction_df)[0]
        classes = model.classes_

        result["probabilities"] = {
            str(class_name): round(float(probability), 4)
            for class_name, probability in zip(classes, probabilities)
        }

        result["confidence"] = round(float(max(probabilities)), 4)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Script de prédiction locale pour le modèle ObRail."
    )

    parser.add_argument(
        "--input",
        required=False,
        help=(
            "Chemin vers un fichier JSON ou chaîne JSON contenant les variables de la liaison. "
            "Si absent, un exemple par défaut est utilisé."
        ),
    )

    args = parser.parse_args()

    PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)

    input_data = load_input_data(args.input)
    result = predict(input_data)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

    print("[OK] Prédiction réalisée")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nRésultat sauvegardé dans : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
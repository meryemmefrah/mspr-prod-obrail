from pathlib import Path
import json
import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.utils.class_weight import compute_sample_weight


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODELING_DIR = PROJECT_ROOT / "data" / "modeling"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

TRAIN_PATH = MODELING_DIR / "train.csv"
VALIDATION_PATH = MODELING_DIR / "validation.csv"
TEST_PATH = MODELING_DIR / "test.csv"

MODEL_OUTPUT_PATH = MODELS_DIR / "substitution_model.joblib"
METRICS_OUTPUT_PATH = MODELS_DIR / "model_metrics.json"
COMPARISON_OUTPUT_PATH = REPORTS_DIR / "model_comparison.csv"

TARGET_COLUMN = "substitution_potential"
RANDOM_STATE = 42


# Important :
# On n'utilise PAS substitution_score comme variable d'entrée,
# car la cible substitution_potential est construite à partir de ce score.
# L'utiliser créerait une fuite de données.
FEATURE_COLUMNS = [
    "is_international",
    "distance_km",
    "weekly_frequency",
    "daily_frequency_avg",
    "avg_duration_minutes",
    "min_duration_minutes",
    "max_duration_minutes",
    "has_night_train",
    "has_day_train",
    "avg_num_stops",
    "avg_quality_score",
    "quality_issues_count",
    "co2_train_kg",
    "co2_plane_kg",
    "co2_saving_kg",
    "co2_saving_percent",
]


def load_data():
    train_df = pd.read_csv(TRAIN_PATH)
    validation_df = pd.read_csv(VALIDATION_PATH)
    test_df = pd.read_csv(TEST_PATH)

    for col in FEATURE_COLUMNS + [TARGET_COLUMN]:
        if col not in train_df.columns:
            raise ValueError(f"Colonne manquante dans train.csv : {col}")

    return train_df, validation_df, test_df


def build_pipeline(model):
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", model),
        ]
    )


def get_models():
    return {
        "logistic_regression": build_pipeline(
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            )
        ),
        "decision_tree": build_pipeline(
            DecisionTreeClassifier(
                max_depth=6,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            )
        ),
        "random_forest": build_pipeline(
            RandomForestClassifier(
                n_estimators=300,
                max_depth=12,
                min_samples_leaf=3,
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            )
        ),
        "gradient_boosting": build_pipeline(
            GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=3,
                random_state=RANDOM_STATE,
            )
        ),
    }


def compute_metrics(y_true, y_pred):
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision_macro": round(
            precision_score(y_true, y_pred, average="macro", zero_division=0), 4
        ),
        "recall_macro": round(
            recall_score(y_true, y_pred, average="macro", zero_division=0), 4
        ),
        "f1_macro": round(
            f1_score(y_true, y_pred, average="macro", zero_division=0), 4
        ),
        "f1_weighted": round(
            f1_score(y_true, y_pred, average="weighted", zero_division=0), 4
        ),
    }


def train_and_compare_models(train_df, validation_df):
    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]

    X_validation = validation_df[FEATURE_COLUMNS]
    y_validation = validation_df[TARGET_COLUMN]

    models = get_models()
    results = []

    for model_name, pipeline in models.items():
        print(f"\n[INFO] Entraînement du modèle : {model_name}")

        if model_name == "gradient_boosting":
            sample_weight = compute_sample_weight(class_weight="balanced", y=y_train)
            pipeline.fit(X_train, y_train, model__sample_weight=sample_weight)
        else:
            pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_validation)
        metrics = compute_metrics(y_validation, y_pred)

        result = {
            "model": model_name,
            **metrics,
        }

        results.append(result)

        print(f"Résultats validation pour {model_name} :")
        print(result)

    comparison_df = pd.DataFrame(results)
    comparison_df = comparison_df.sort_values(by="f1_macro", ascending=False)

    return comparison_df, models


def retrain_best_model(best_model_name, train_df, validation_df):
    full_train_df = pd.concat([train_df, validation_df], ignore_index=True)

    X_full_train = full_train_df[FEATURE_COLUMNS]
    y_full_train = full_train_df[TARGET_COLUMN]

    models = get_models()
    best_pipeline = models[best_model_name]

    print(f"\n[INFO] Réentraînement du meilleur modèle : {best_model_name}")

    if best_model_name == "gradient_boosting":
        sample_weight = compute_sample_weight(class_weight="balanced", y=y_full_train)
        best_pipeline.fit(X_full_train, y_full_train, model__sample_weight=sample_weight)
    else:
        best_pipeline.fit(X_full_train, y_full_train)

    return best_pipeline


def evaluate_on_test(best_pipeline, test_df):
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    y_pred = best_pipeline.predict(X_test)

    test_metrics = compute_metrics(y_test, y_pred)

    report = classification_report(
        y_test,
        y_pred,
        output_dict=True,
        zero_division=0,
    )

    matrix = confusion_matrix(y_test, y_pred, labels=["faible", "moyen", "fort"])

    return test_metrics, report, matrix.tolist()


def main():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    train_df, validation_df, test_df = load_data()

    print("[INFO] Données chargées")
    print(f"Train      : {train_df.shape}")
    print(f"Validation : {validation_df.shape}")
    print(f"Test       : {test_df.shape}")

    comparison_df, _ = train_and_compare_models(train_df, validation_df)

    print("\n[OK] Comparaison des modèles sur validation")
    print(comparison_df)

    comparison_df.to_csv(COMPARISON_OUTPUT_PATH, index=False, encoding="utf-8")

    best_model_name = comparison_df.iloc[0]["model"]

    best_pipeline = retrain_best_model(best_model_name, train_df, validation_df)

    test_metrics, test_report, test_confusion_matrix = evaluate_on_test(
        best_pipeline,
        test_df,
    )

    joblib.dump(best_pipeline, MODEL_OUTPUT_PATH)

    final_metrics = {
        "best_model": best_model_name,
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "validation_comparison": comparison_df.to_dict(orient="records"),
        "test_metrics": test_metrics,
        "test_classification_report": test_report,
        "test_confusion_matrix": {
            "labels": ["faible", "moyen", "fort"],
            "matrix": test_confusion_matrix,
        },
        "note": (
            "La variable substitution_score a été exclue des variables d'entrée "
            "afin d'éviter une fuite de données."
        ),
    }

    with open(METRICS_OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(final_metrics, file, indent=2, ensure_ascii=False)

    print("\n[OK] Modèle final sauvegardé")
    print(f"Modèle : {MODEL_OUTPUT_PATH}")
    print(f"Métriques : {METRICS_OUTPUT_PATH}")
    print(f"Comparaison : {COMPARISON_OUTPUT_PATH}")

    print("\nMeilleur modèle :", best_model_name)
    print("\nMétriques finales sur test :")
    print(test_metrics)

    print("\nMatrice de confusion test :")
    print(pd.DataFrame(
        test_confusion_matrix,
        index=["réel_faible", "réel_moyen", "réel_fort"],
        columns=["pred_faible", "pred_moyen", "pred_fort"],
    ))


if __name__ == "__main__":
    main()
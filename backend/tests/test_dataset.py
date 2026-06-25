from pathlib import Path
import json
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = PROJECT_ROOT / "data" / "modeling" / "route_substitution_dataset.csv"
METADATA_PATH = PROJECT_ROOT / "data" / "modeling" / "dataset_metadata.json"
TRAIN_PATH = PROJECT_ROOT / "data" / "modeling" / "train.csv"
VALIDATION_PATH = PROJECT_ROOT / "data" / "modeling" / "validation.csv"
TEST_PATH = PROJECT_ROOT / "data" / "modeling" / "test.csv"
SPLIT_METADATA_PATH = PROJECT_ROOT / "data" / "modeling" / "split_metadata.json"

TARGET_COLUMN = "substitution_potential"

REQUIRED_COLUMNS = [
    "route_id",
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
    "substitution_score",
    "substitution_potential",
]


def test_dataset_file_exists():
    assert DATASET_PATH.exists(), f"Dataset introuvable : {DATASET_PATH}"


def test_dataset_metadata_exists():
    assert METADATA_PATH.exists(), f"Métadonnées introuvables : {METADATA_PATH}"


def test_dataset_has_required_columns():
    df = pd.read_csv(DATASET_PATH)

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in df.columns
    ]

    assert not missing_columns, f"Colonnes manquantes : {missing_columns}"


def test_dataset_is_not_empty():
    df = pd.read_csv(DATASET_PATH)

    assert len(df) > 0, "Le dataset est vide"
    assert df.shape[1] >= len(REQUIRED_COLUMNS), "Le dataset contient trop peu de colonnes"


def test_dataset_has_no_missing_values_on_required_columns():
    df = pd.read_csv(DATASET_PATH)

    missing_values = df[REQUIRED_COLUMNS].isna().sum()
    missing_values = missing_values[missing_values > 0]

    assert missing_values.empty, f"Valeurs manquantes détectées : {missing_values.to_dict()}"


def test_numeric_business_values_are_positive():
    df = pd.read_csv(DATASET_PATH)

    assert (df["distance_km"] > 0).all(), "Certaines distances sont nulles ou négatives"
    assert (df["avg_duration_minutes"] > 0).all(), "Certaines durées sont nulles ou négatives"
    assert (df["weekly_frequency"] > 0).all(), "Certaines fréquences sont nulles ou négatives"


def test_target_contains_expected_classes():
    df = pd.read_csv(DATASET_PATH)

    expected_classes = {"faible", "moyen", "fort"}
    actual_classes = set(df[TARGET_COLUMN].unique())

    assert actual_classes == expected_classes, (
        f"Classes attendues : {expected_classes}, classes trouvées : {actual_classes}"
    )


def test_each_target_class_has_enough_rows():
    df = pd.read_csv(DATASET_PATH)

    class_counts = df[TARGET_COLUMN].value_counts().to_dict()

    assert class_counts.get("faible", 0) > 0, "Classe faible absente"
    assert class_counts.get("moyen", 0) > 0, "Classe moyen absente"
    assert class_counts.get("fort", 0) > 0, "Classe fort absente"


def test_train_validation_test_files_exist():
    assert TRAIN_PATH.exists(), f"train.csv introuvable : {TRAIN_PATH}"
    assert VALIDATION_PATH.exists(), f"validation.csv introuvable : {VALIDATION_PATH}"
    assert TEST_PATH.exists(), f"test.csv introuvable : {TEST_PATH}"
    assert SPLIT_METADATA_PATH.exists(), f"split_metadata.json introuvable : {SPLIT_METADATA_PATH}"


def test_train_validation_test_are_not_empty():
    train_df = pd.read_csv(TRAIN_PATH)
    validation_df = pd.read_csv(VALIDATION_PATH)
    test_df = pd.read_csv(TEST_PATH)

    assert len(train_df) > 0, "train.csv est vide"
    assert len(validation_df) > 0, "validation.csv est vide"
    assert len(test_df) > 0, "test.csv est vide"


def test_split_preserves_target_classes():
    train_df = pd.read_csv(TRAIN_PATH)
    validation_df = pd.read_csv(VALIDATION_PATH)
    test_df = pd.read_csv(TEST_PATH)

    expected_classes = {"faible", "moyen", "fort"}

    assert set(train_df[TARGET_COLUMN].unique()) == expected_classes
    assert set(validation_df[TARGET_COLUMN].unique()) == expected_classes
    assert set(test_df[TARGET_COLUMN].unique()) == expected_classes


def test_metadata_target_distribution_matches_dataset():
    df = pd.read_csv(DATASET_PATH)

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    dataset_distribution = df[TARGET_COLUMN].value_counts().to_dict()
    metadata_distribution = metadata.get("target_distribution", {})

    assert dataset_distribution == metadata_distribution, (
        "La répartition de la cible dans dataset_metadata.json ne correspond pas au dataset"
    )
from pathlib import Path
import json
import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODELING_DIR = PROJECT_ROOT / "data" / "modeling"

INPUT_DATASET = MODELING_DIR / "route_substitution_dataset.csv"

TRAIN_OUTPUT = MODELING_DIR / "train.csv"
VALIDATION_OUTPUT = MODELING_DIR / "validation.csv"
TEST_OUTPUT = MODELING_DIR / "test.csv"
SPLIT_METADATA_OUTPUT = MODELING_DIR / "split_metadata.json"

TARGET_COLUMN = "substitution_potential"
RANDOM_STATE = 42


def split_dataset():
    if not INPUT_DATASET.exists():
        raise FileNotFoundError(f"Dataset introuvable : {INPUT_DATASET}")

    df = pd.read_csv(INPUT_DATASET)

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Colonne cible absente : {TARGET_COLUMN}")

    print("[INFO] Dataset chargé")
    print(f"Shape initiale : {df.shape}")
    print("\nRépartition initiale :")
    print(df[TARGET_COLUMN].value_counts())

    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=df[TARGET_COLUMN],
    )

    validation_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=temp_df[TARGET_COLUMN],
    )

    train_df.to_csv(TRAIN_OUTPUT, index=False, encoding="utf-8")
    validation_df.to_csv(VALIDATION_OUTPUT, index=False, encoding="utf-8")
    test_df.to_csv(TEST_OUTPUT, index=False, encoding="utf-8")

    metadata = {
        "input_dataset": str(INPUT_DATASET),
        "target_column": TARGET_COLUMN,
        "random_state": RANDOM_STATE,
        "split_strategy": "stratified train/validation/test split",
        "train": {
            "path": str(TRAIN_OUTPUT),
            "rows": int(len(train_df)),
            "distribution": train_df[TARGET_COLUMN].value_counts().to_dict(),
        },
        "validation": {
            "path": str(VALIDATION_OUTPUT),
            "rows": int(len(validation_df)),
            "distribution": validation_df[TARGET_COLUMN].value_counts().to_dict(),
        },
        "test": {
            "path": str(TEST_OUTPUT),
            "rows": int(len(test_df)),
            "distribution": test_df[TARGET_COLUMN].value_counts().to_dict(),
        },
    }

    with open(SPLIT_METADATA_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2, ensure_ascii=False)

    print("\n[OK] Split terminé")
    print(f"Train      : {train_df.shape}")
    print(f"Validation : {validation_df.shape}")
    print(f"Test       : {test_df.shape}")

    print("\nRépartition train :")
    print(train_df[TARGET_COLUMN].value_counts())

    print("\nRépartition validation :")
    print(validation_df[TARGET_COLUMN].value_counts())

    print("\nRépartition test :")
    print(test_df[TARGET_COLUMN].value_counts())


if __name__ == "__main__":
    split_dataset()
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

METRICS_PATH = MODELS_DIR / "model_metrics.json"
MODEL_PATH = MODELS_DIR / "substitution_model.joblib"
COMPARISON_PATH = REPORTS_DIR / "model_comparison.csv"

REPORT_OUTPUT = REPORTS_DIR / "rapport_evaluation.md"
FEATURE_IMPORTANCE_OUTPUT = REPORTS_DIR / "feature_importance.csv"

FIG_MODEL_COMPARISON = FIGURES_DIR / "model_comparison_f1_macro.png"
FIG_CONFUSION_MATRIX = FIGURES_DIR / "confusion_matrix.png"
FIG_FEATURE_IMPORTANCE = FIGURES_DIR / "feature_importance.png"


def load_metrics():
    with open(METRICS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def plot_model_comparison(comparison_df):
    comparison_df = comparison_df.sort_values("f1_macro", ascending=True)

    plt.figure(figsize=(8, 5))
    plt.barh(comparison_df["model"], comparison_df["f1_macro"])
    plt.title("Comparaison des modèles - F1 macro")
    plt.xlabel("F1 macro")
    plt.ylabel("Modèle")
    plt.xlim(0, 1.05)
    plt.tight_layout()
    plt.savefig(FIG_MODEL_COMPARISON, dpi=150)
    plt.close()


def plot_confusion_matrix(metrics):
    labels = metrics["test_confusion_matrix"]["labels"]
    matrix = metrics["test_confusion_matrix"]["matrix"]

    plt.figure(figsize=(6, 5))
    plt.imshow(matrix)
    plt.title("Matrice de confusion - jeu de test")
    plt.xticks(range(len(labels)), labels)
    plt.yticks(range(len(labels)), labels)
    plt.xlabel("Classe prédite")
    plt.ylabel("Classe réelle")

    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            plt.text(j, i, str(value), ha="center", va="center")

    plt.tight_layout()
    plt.savefig(FIG_CONFUSION_MATRIX, dpi=150)
    plt.close()


def compute_feature_importance(metrics):
    pipeline = joblib.load(MODEL_PATH)
    model = pipeline.named_steps["model"]
    feature_columns = metrics["feature_columns"]

    if not hasattr(model, "feature_importances_"):
        return None

    importance_df = pd.DataFrame(
        {
            "feature": feature_columns,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)

    importance_df.to_csv(FEATURE_IMPORTANCE_OUTPUT, index=False, encoding="utf-8")

    top_features = importance_df.head(10).sort_values("importance", ascending=True)

    plt.figure(figsize=(8, 5))
    plt.barh(top_features["feature"], top_features["importance"])
    plt.title("Importance des variables - Gradient Boosting")
    plt.xlabel("Importance")
    plt.ylabel("Variable")
    plt.tight_layout()
    plt.savefig(FIG_FEATURE_IMPORTANCE, dpi=150)
    plt.close()

    return importance_df


def generate_markdown_report(metrics, comparison_df, importance_df):
    best_model = metrics["best_model"]
    test_metrics = metrics["test_metrics"]
    report = metrics["test_classification_report"]
    confusion = metrics["test_confusion_matrix"]

    lines = []

    lines.append("# Rapport d’évaluation du modèle IA ObRail")
    lines.append("")
    lines.append("## Objectif")
    lines.append("")
    lines.append(
        "L’objectif du modèle est de classifier les liaisons ferroviaires selon leur potentiel "
        "de substitution à l’avion : faible, moyen ou fort."
    )
    lines.append("")
    lines.append("## Modèles comparés")
    lines.append("")
    lines.append(comparison_df.to_markdown(index=False))
    lines.append("")
    lines.append(f"Le meilleur modèle sélectionné est : **{best_model}**.")
    lines.append("")
    lines.append("## Métriques finales sur le jeu de test")
    lines.append("")
    lines.append(f"- Accuracy : {test_metrics['accuracy']}")
    lines.append(f"- Precision macro : {test_metrics['precision_macro']}")
    lines.append(f"- Recall macro : {test_metrics['recall_macro']}")
    lines.append(f"- F1 macro : {test_metrics['f1_macro']}")
    lines.append(f"- F1 weighted : {test_metrics['f1_weighted']}")
    lines.append("")
    lines.append("## Rapport par classe")
    lines.append("")
    class_rows = []
    for label in ["faible", "moyen", "fort"]:
        class_rows.append(
            {
                "classe": label,
                "precision": round(report[label]["precision"], 4),
                "recall": round(report[label]["recall"], 4),
                "f1_score": round(report[label]["f1-score"], 4),
                "support": int(report[label]["support"]),
            }
        )

    lines.append(pd.DataFrame(class_rows).to_markdown(index=False))
    lines.append("")
    lines.append("## Matrice de confusion")
    lines.append("")
    matrix_df = pd.DataFrame(
        confusion["matrix"],
        index=[f"réel_{label}" for label in confusion["labels"]],
        columns=[f"pred_{label}" for label in confusion["labels"]],
    )
    lines.append(matrix_df.to_markdown())
    lines.append("")
    lines.append("## Variables les plus importantes")
    lines.append("")

    if importance_df is not None:
        lines.append(importance_df.head(10).to_markdown(index=False))
    else:
        lines.append("Le modèle sélectionné ne fournit pas d’importance de variables exploitable.")

    lines.append("")
    lines.append("## Interprétation")
    lines.append("")
    lines.append(
        "Les résultats montrent que le modèle Gradient Boosting reproduit très bien la logique métier "
        "de classification construite à partir des indicateurs ferroviaires et environnementaux."
    )
    lines.append("")
    lines.append(
        "La métrique principale retenue est le F1 macro, car les classes ne sont pas parfaitement équilibrées. "
        "Cette métrique permet de tenir compte de la performance sur chaque classe, et pas uniquement de la classe majoritaire."
    )
    lines.append("")
    lines.append("## Limites")
    lines.append("")
    lines.append(
        "La cible utilisée est une cible métier construite à partir d’un score de substitution. "
        "Le modèle ne repose donc pas encore sur des labels historiques validés par des experts. "
        "Une amélioration future consisterait à valider les classes avec ObRail ou à intégrer des données réelles "
        "de report modal entre avion et train."
    )
    lines.append("")
    lines.append(
        "La variable substitution_score a été exclue des variables d’entrée afin d’éviter une fuite de données."
    )

    REPORT_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    metrics = load_metrics()
    comparison_df = pd.read_csv(COMPARISON_PATH)

    plot_model_comparison(comparison_df)
    plot_confusion_matrix(metrics)
    importance_df = compute_feature_importance(metrics)
    generate_markdown_report(metrics, comparison_df, importance_df)

    print("[OK] Artefacts d’évaluation générés")
    print(f"Rapport : {REPORT_OUTPUT}")
    print(f"Comparaison modèles : {FIG_MODEL_COMPARISON}")
    print(f"Matrice de confusion : {FIG_CONFUSION_MATRIX}")
    print(f"Importance variables : {FIG_FEATURE_IMPORTANCE}")
    print(f"Importance CSV : {FEATURE_IMPORTANCE_OUTPUT}")


if __name__ == "__main__":
    main()
# Procédure de ré-entraînement du modèle IA ObRail

## 1. Objectif du document

Ce document décrit la procédure permettant de réentraîner le modèle d’intelligence artificielle ObRail.

Le modèle a pour objectif de classifier les liaisons ferroviaires selon leur potentiel de substitution à l’avion :

* `faible` ;
* `moyen` ;
* `fort`.

Cette procédure permet de garantir que le modèle peut être reconstruit, évalué, sauvegardé et réutilisé de manière reproductible.

---

## 2. Cas d’usage du ré-entraînement

Le ré-entraînement du modèle peut être nécessaire dans plusieurs situations :

1. De nouvelles données ferroviaires sont disponibles.
2. Le flux ETL a été mis à jour.
3. De nouvelles routes ou de nouveaux trajets ont été intégrés.
4. Les règles de création du score métier ont évolué.
5. Les facteurs d’émission CO₂ ont été corrigés ou affinés.
6. Les performances du modèle diminuent.
7. Une dérive des données est détectée.
8. ObRail souhaite ajuster les critères métier de classification.

---

## 3. Prérequis techniques

Avant de lancer la procédure, vérifier que l’environnement Python est actif.

### Activation de l’environnement virtuel

Sous Windows PowerShell :

```bash
.\.venv\Scripts\Activate.ps1
```

Sous Windows CMD :

```bash
.venv\Scripts\activate
```

### Installation des dépendances

Depuis la racine du projet :

```bash
python -m pip install -r requirements.txt
```

Le fichier `requirements.txt` doit contenir au minimum :

```text
pandas
numpy
scikit-learn
joblib
matplotlib
fastapi
uvicorn
pydantic
tabulate
```

---

## 4. Structure attendue du projet

La procédure s’appuie sur la structure suivante :

```text
mspr-ia-obrail/
│
├── data/
│   ├── processed/
│   │   ├── country.csv
│   │   ├── city.csv
│   │   ├── station.csv
│   │   ├── operator.csv
│   │   ├── train_type.csv
│   │   ├── data_source.csv
│   │   ├── route.csv
│   │   ├── trip.csv
│   │   ├── trip_stop.csv
│   │   └── quality_check.csv
│   │
│   ├── modeling/
│   │   ├── route_substitution_dataset.csv
│   │   ├── dataset_metadata.json
│   │   ├── train.csv
│   │   ├── validation.csv
│   │   ├── test.csv
│   │   └── split_metadata.json
│   │
│   └── predictions/
│       └── last_prediction.json
│
├── models/
│   ├── substitution_model.joblib
│   └── model_metrics.json
│
├── reports/
│   ├── model_comparison.csv
│   ├── rapport_evaluation.md
│   ├── feature_importance.csv
│   └── figures/
│
├── scripts/
│   └── ml/
│       ├── build_dataset.py
│       ├── split_dataset.py
│       ├── train_models.py
│       ├── generate_evaluation_artifacts.py
│       └── predict.py
│
├── api/
│   ├── main.py
│   └── prediction.py
│
└── docs/
    ├── api_prediction.md
    └── procedure_reentrainement.md
```

---

## 5. Étape 1 — Vérifier les données ETL

Le modèle IA est entraîné à partir des données harmonisées issues du flux ETL.

Les fichiers attendus sont situés dans :

```text
data/processed/
```

Les fichiers principaux sont :

```text
country.csv
city.csv
station.csv
operator.csv
train_type.csv
data_source.csv
route.csv
trip.csv
trip_stop.csv
quality_check.csv
```

Avant de réentraîner le modèle, vérifier que ces fichiers existent.

Commande de vérification sous Windows :

```bash
dir data\processed
```

---

## 6. Étape 2 — Générer le dataset IA

Le dataset IA est généré à partir des tables harmonisées du dossier `data/processed/`.

Commande :

```bash
python scripts/ml/build_dataset.py
```

Cette commande génère :

```text
data/modeling/route_substitution_dataset.csv
data/modeling/dataset_metadata.json
```

Le fichier `route_substitution_dataset.csv` contient une ligne par liaison ferroviaire exploitable par le modèle.

---

## 7. Variables créées dans le dataset IA

Le script `build_dataset.py` construit notamment les variables suivantes :

| Variable                 | Description                                                   |
| ------------------------ | ------------------------------------------------------------- |
| `is_international`       | Indique si la liaison est internationale                      |
| `distance_km`            | Distance estimée entre la gare de départ et la gare d’arrivée |
| `weekly_frequency`       | Nombre de trajets estimé par semaine                          |
| `daily_frequency_avg`    | Fréquence quotidienne moyenne                                 |
| `avg_duration_minutes`   | Durée moyenne du trajet                                       |
| `min_duration_minutes`   | Durée minimale observée                                       |
| `max_duration_minutes`   | Durée maximale observée                                       |
| `has_night_train`        | Présence d’un train de nuit                                   |
| `has_day_train`          | Présence d’un train de jour                                   |
| `avg_num_stops`          | Nombre moyen d’arrêts intermédiaires                          |
| `avg_quality_score`      | Score moyen de qualité des données                            |
| `quality_issues_count`   | Nombre d’anomalies qualité                                    |
| `co2_train_kg`           | Émissions CO₂ estimées du trajet en train                     |
| `co2_plane_kg`           | Émissions CO₂ estimées du trajet en avion                     |
| `co2_saving_kg`          | Gain CO₂ estimé                                               |
| `co2_saving_percent`     | Pourcentage de réduction des émissions                        |
| `substitution_score`     | Score métier de substitution avion → train                    |
| `substitution_potential` | Classe cible : faible, moyen ou fort                          |

---

## 8. Création de la cible métier

La cible du modèle est :

```text
substitution_potential
```

Elle contient trois classes :

```text
faible
moyen
fort
```

Cette cible est construite à partir d’un score métier nommé :

```text
substitution_score
```

Le score tient compte des critères suivants :

* distance de la liaison ;
* durée moyenne ;
* fréquence hebdomadaire ;
* présence d’un train de nuit ;
* gain CO₂ estimé ;
* qualité des données ;
* caractère international de la liaison.

Important : la variable `substitution_score` ne doit pas être utilisée comme variable d’entrée du modèle. Elle sert à construire la cible et à expliquer la logique métier, mais son utilisation dans l’entraînement créerait une fuite de données.

---

## 9. Contrôles qualité du dataset IA

Après génération du dataset, exécuter la commande suivante :

```bash
python -c "import pandas as pd; df=pd.read_csv('data/modeling/route_substitution_dataset.csv'); print(df.shape); print(df['substitution_potential'].value_counts()); print('Distances <= 0:', (df['distance_km'] <= 0).sum()); print('Durées <= 0:', (df['avg_duration_minutes'] <= 0).sum()); print('Fréquences <= 0:', (df['weekly_frequency'] <= 0).sum()); print('Valeurs manquantes:', df.isna().sum().sum())"
```

Résultat attendu dans la version actuelle du projet :

```text
(4101, 35)

moyen     2919
faible     733
fort       449

Distances <= 0   : 0
Durées <= 0      : 0
Fréquences <= 0  : 0
Valeurs manquantes : 0
```

Si des distances, durées ou fréquences inférieures ou égales à zéro apparaissent, le dataset doit être corrigé avant l’entraînement.

---

## 10. Étape 3 — Séparer les données

Le dataset doit être séparé en trois parties :

* jeu d’entraînement ;
* jeu de validation ;
* jeu de test.

Commande :

```bash
python scripts/ml/split_dataset.py
```

Cette commande génère :

```text
data/modeling/train.csv
data/modeling/validation.csv
data/modeling/test.csv
data/modeling/split_metadata.json
```

La stratégie utilisée est une séparation stratifiée afin de conserver les proportions des classes dans chaque jeu.

Répartition actuelle :

```text
Train      : 2870 lignes
Validation : 615 lignes
Test       : 616 lignes
```

Répartition actuelle par classe :

```text
Train :
moyen     2043
faible     513
fort       314

Validation :
moyen      438
faible     110
fort        67

Test :
moyen      438
faible     110
fort        68
```

---

## 11. Étape 4 — Entraîner les modèles candidats

Commande :

```bash
python scripts/ml/train_models.py
```

Ce script entraîne et compare plusieurs modèles :

| Modèle                | Rôle                                                             |
| --------------------- | ---------------------------------------------------------------- |
| Régression logistique | Modèle simple et interprétable                                   |
| Arbre de décision     | Modèle explicable                                                |
| Random Forest         | Modèle robuste basé sur plusieurs arbres                         |
| Gradient Boosting     | Modèle performant basé sur une combinaison séquentielle d’arbres |

Le script compare les modèles sur le jeu de validation.

La métrique principale utilisée est :

```text
F1 macro
```

Cette métrique est privilégiée car les classes ne sont pas parfaitement équilibrées.

---

## 12. Variables utilisées pour l’entraînement

Les variables utilisées par le modèle sont :

```text
is_international
distance_km
weekly_frequency
daily_frequency_avg
avg_duration_minutes
min_duration_minutes
max_duration_minutes
has_night_train
has_day_train
avg_num_stops
avg_quality_score
quality_issues_count
co2_train_kg
co2_plane_kg
co2_saving_kg
co2_saving_percent
```

La variable cible est :

```text
substitution_potential
```

La variable suivante est volontairement exclue :

```text
substitution_score
```

Motif : éviter une fuite de données, car la cible est construite à partir de ce score.

---

## 13. Étape 5 — Sauvegarde du modèle

Après entraînement, le script génère :

```text
models/substitution_model.joblib
models/model_metrics.json
reports/model_comparison.csv
```

Le fichier `substitution_model.joblib` contient le modèle final sauvegardé.

Le fichier `model_metrics.json` contient :

* le meilleur modèle ;
* les variables d’entrée ;
* la colonne cible ;
* les métriques sur validation ;
* les métriques sur test ;
* le rapport de classification ;
* la matrice de confusion ;
* une note sur l’exclusion de `substitution_score`.

---

## 14. Résultats actuels du modèle

Le meilleur modèle actuellement obtenu est :

```text
gradient_boosting
```

Performances sur le jeu de test :

| Métrique        | Valeur |
| --------------- | -----: |
| Accuracy        | 0.9919 |
| Precision macro | 0.9805 |
| Recall macro    | 0.9921 |
| F1 macro        | 0.9861 |
| F1 weighted     | 0.9920 |

Matrice de confusion sur le jeu de test :

| Classe réelle | Prédit faible | Prédit moyen | Prédit fort |
| ------------- | ------------: | -----------: | ----------: |
| faible        |           110 |            0 |           0 |
| moyen         |             0 |          434 |           4 |
| fort          |             0 |            1 |          67 |

Le modèle réalise actuellement 5 erreurs sur 616 exemples de test.

---

## 15. Étape 6 — Générer les artefacts d’évaluation

Commande :

```bash
python scripts/ml/generate_evaluation_artifacts.py
```

Cette commande génère :

```text
reports/rapport_evaluation.md
reports/model_comparison.csv
reports/feature_importance.csv
reports/figures/model_comparison_f1_macro.png
reports/figures/confusion_matrix.png
reports/figures/feature_importance.png
```

Ces artefacts permettent de documenter les performances du modèle et d’alimenter le rapport technique final ainsi que la soutenance.

---

## 16. Étape 7 — Tester une prédiction locale

Commande avec l’exemple par défaut :

```bash
python scripts/ml/predict.py
```

Commande avec un fichier JSON :

```bash
python scripts/ml/predict.py --input data/predictions/sample_input.json
```

Exemple de fichier d’entrée :

```json
{
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
  "co2_saving_percent": 93.9
}
```

Résultat attendu :

```json
{
  "prediction": "fort",
  "probabilities": {
    "faible": 0.0,
    "fort": 1.0,
    "moyen": 0.0
  },
  "confidence": 1.0
}
```

---

## 17. Étape 8 — Tester l’API après ré-entraînement

Après ré-entraînement, il faut relancer l’API afin qu’elle recharge le modèle sauvegardé.

Commande :

```bash
python -m uvicorn api.main:app --reload
```

Documentation Swagger :

```text
http://127.0.0.1:8000/docs
```

Tester ensuite les routes :

```text
GET /model-info
POST /predict
```

La route `/model-info` doit retourner le nouveau modèle chargé et les nouvelles métriques.

La route `/predict` doit retourner une prédiction valide pour un exemple métier.

---

## 18. Critères de validation du nouveau modèle

Un modèle réentraîné peut être accepté si :

1. Le script `build_dataset.py` s’exécute sans erreur.
2. Le dataset final ne contient pas de valeurs critiques manquantes.
3. Les distances, durées et fréquences sont strictement positives.
4. Les trois classes `faible`, `moyen` et `fort` sont représentées.
5. Le split train / validation / test est bien stratifié.
6. Les performances sur test restent cohérentes.
7. Le F1 macro ne chute pas fortement.
8. Le modèle est sauvegardé dans `models/substitution_model.joblib`.
9. Le script `predict.py` fonctionne.
10. L’API `/predict` retourne une prédiction correcte.

---

## 19. Seuils de contrôle recommandés

Les seuils suivants peuvent être utilisés pour accepter ou refuser un nouveau modèle :

| Indicateur                   | Seuil recommandé |
| ---------------------------- | ---------------: |
| Valeurs manquantes critiques |                0 |
| Distances <= 0               |                0 |
| Durées <= 0                  |                0 |
| Fréquences <= 0              |                0 |
| F1 macro test                |          >= 0.85 |
| Accuracy test                |          >= 0.85 |
| Présence des trois classes   |      obligatoire |
| Prédiction API fonctionnelle |      obligatoire |

Si le F1 macro chute sous `0.85`, il faut analyser les causes avant de remplacer le modèle en production.

---

## 20. Gestion de version du modèle

Avant de remplacer le modèle actuel, il est recommandé de sauvegarder l’ancienne version.

Exemple :

```bash
copy models\substitution_model.joblib models\substitution_model_backup.joblib
copy models\model_metrics.json models\model_metrics_backup.json
```

Il est aussi possible de versionner les modèles avec un timestamp :

```text
models/substitution_model_YYYYMMDD.joblib
models/model_metrics_YYYYMMDD.json
```

Exemple :

```text
models/substitution_model_20260215.joblib
models/model_metrics_20260215.json
```

---

## 21. Retour arrière

Si le nouveau modèle est moins performant ou provoque une erreur dans l’API, restaurer l’ancien modèle.

Exemple :

```bash
copy models\substitution_model_backup.joblib models\substitution_model.joblib
copy models\model_metrics_backup.json models\model_metrics.json
```

Puis relancer l’API :

```bash
python -m uvicorn api.main:app --reload
```

Vérifier ensuite :

```text
GET /model-info
POST /predict
```

---

## 22. Journalisation recommandée

À chaque ré-entraînement, il est recommandé de conserver les informations suivantes :

| Élément                 | Description                                       |
| ----------------------- | ------------------------------------------------- |
| Date de ré-entraînement | Date et heure du lancement                        |
| Version du dataset      | Nom ou hash du fichier utilisé                    |
| Nombre de lignes        | Taille du dataset final                           |
| Répartition des classes | Nombre de faible, moyen, fort                     |
| Modèle sélectionné      | Nom du meilleur modèle                            |
| F1 macro                | Score principal                                   |
| Accuracy                | Score global                                      |
| Commentaire             | Raisons du ré-entraînement ou anomalies observées |

Ces informations peuvent être ajoutées dans un fichier :

```text
reports/training_log.md
```

---

## 23. Limites de la procédure actuelle

La procédure actuelle est adaptée à un prototype IA, mais elle comporte plusieurs limites :

1. La cible est construite à partir d’un score métier, et non à partir de labels historiques réels.
2. Les facteurs CO₂ sont estimés avec des hypothèses simplifiées.
3. Le modèle dépend de la qualité des données issues de l’ETL.
4. Le système ne dispose pas encore d’un monitoring automatique en production.
5. Les prédictions ne sont pas encore enregistrées dans une base de logs.
6. Le modèle n’est pas encore validé par des experts métier ObRail.

Ces limites devront être présentées dans le rapport technique final.

---

## 24. Améliorations futures

Les améliorations suivantes sont recommandées :

1. Ajouter des labels validés par des experts métier.
2. Utiliser des facteurs CO₂ officiels et plus granulaires.
3. Intégrer des données réelles de fréquentation ou de report modal avion/train.
4. Automatiser le ré-entraînement avec une chaîne CI/CD.
5. Ajouter des tests unitaires sur le pipeline IA.
6. Ajouter un monitoring des prédictions en production.
7. Détecter la dérive des données.
8. Versionner automatiquement les modèles.
9. Ajouter une route API de prédiction à partir d’un `route_id`.
10. Connecter le modèle directement à PostgreSQL.

---

## 25. Commandes complètes de ré-entraînement

La procédure complète peut être rejouée avec les commandes suivantes :

```bash
python scripts/ml/build_dataset.py
python scripts/ml/split_dataset.py
python scripts/ml/train_models.py
python scripts/ml/generate_evaluation_artifacts.py
python scripts/ml/predict.py
python -m uvicorn api.main:app --reload
```

---

## 26. Conclusion

Cette procédure permet de réentraîner le modèle IA ObRail de manière structurée et reproductible.

Elle couvre l’ensemble du cycle :

```text
Données ETL
→ Dataset IA
→ Séparation train / validation / test
→ Entraînement
→ Évaluation
→ Sauvegarde du modèle
→ Test local
→ Exposition via API REST
```

Elle répond aux objectifs de reproductibilité, de documentation et d’intégration applicative attendus pour le projet ObRail.

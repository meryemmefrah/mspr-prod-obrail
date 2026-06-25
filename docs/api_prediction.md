# Documentation API de prédiction IA ObRail

## 1. Objectif de l’API

Cette API permet d’exposer le modèle d’intelligence artificielle développé dans le cadre du projet ObRail.

Le modèle a pour objectif d’identifier le potentiel de substitution d’une liaison ferroviaire par rapport à l’avion. Il classe chaque liaison en trois catégories :

* `faible` : liaison peu pertinente pour remplacer l’avion ;
* `moyen` : liaison présentant un potentiel partiel ;
* `fort` : liaison fortement candidate à la substitution avion → train.

L’API permet donc à un utilisateur ou à une future application ObRail d’envoyer les caractéristiques d’une liaison ferroviaire et d’obtenir une prédiction automatique.

---

## 2. Modèle utilisé

Le modèle retenu après comparaison est :

```text
Gradient Boosting Classifier
```

Ce modèle a été sélectionné car il obtient les meilleures performances sur les jeux de validation et de test.

### Métriques finales sur le jeu de test

| Métrique        | Valeur |
| --------------- | -----: |
| Accuracy        | 0.9919 |
| Precision macro | 0.9805 |
| Recall macro    | 0.9921 |
| F1 macro        | 0.9861 |
| F1 weighted     | 0.9920 |

La métrique principale retenue est le `F1 macro`, car les classes ne sont pas parfaitement équilibrées. Cette métrique permet de tenir compte de la performance du modèle sur chaque classe.

---

## 3. Fichiers nécessaires

Pour fonctionner, l’API de prédiction utilise les fichiers suivants :

```text
api/main.py
api/prediction.py
models/substitution_model.joblib
models/model_metrics.json
```

Le fichier `substitution_model.joblib` contient le modèle entraîné et sauvegardé.

Le fichier `model_metrics.json` contient les métadonnées du modèle :

* le nom du meilleur modèle ;
* les variables utilisées en entrée ;
* la colonne cible ;
* les métriques d’évaluation ;
* la matrice de confusion ;
* une note sur l’exclusion de `substitution_score`.

---

## 4. Lancement de l’API

Depuis la racine du projet, lancer la commande suivante :

```bash
python -m uvicorn api.main:app --reload
```

Une fois le serveur lancé, l’API est disponible à l’adresse suivante :

```text
http://127.0.0.1:8000
```

La documentation interactive Swagger est disponible ici :

```text
http://127.0.0.1:8000/docs
```

---

## 5. Endpoints disponibles

### 5.1. Vérification du modèle

```http
GET /model-info
```

Cet endpoint retourne les informations principales du modèle chargé par l’API.

#### Exemple de réponse

```json
{
  "best_model": "gradient_boosting",
  "target_column": "substitution_potential",
  "feature_columns": [
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
    "co2_saving_percent"
  ],
  "test_metrics": {
    "accuracy": 0.9919,
    "precision_macro": 0.9805,
    "recall_macro": 0.9921,
    "f1_macro": 0.9861,
    "f1_weighted": 0.992
  },
  "note": "La variable substitution_score a été exclue des variables d'entrée afin d'éviter une fuite de données."
}
```

---

### 5.2. Prédiction du potentiel de substitution

```http
POST /predict
```

Cet endpoint reçoit les caractéristiques d’une liaison ferroviaire et retourne la classe prédite par le modèle.

---

## 6. Variables attendues par `/predict`

| Variable               |  Type | Description                                                   |
| ---------------------- | ----: | ------------------------------------------------------------- |
| `is_international`     |   int | Indique si la liaison est internationale : `1` oui, `0` non   |
| `distance_km`          | float | Distance estimée entre la gare de départ et la gare d’arrivée |
| `weekly_frequency`     | float | Nombre estimé de trajets par semaine                          |
| `daily_frequency_avg`  | float | Fréquence moyenne quotidienne                                 |
| `avg_duration_minutes` | float | Durée moyenne du trajet en minutes                            |
| `min_duration_minutes` | float | Durée minimale observée                                       |
| `max_duration_minutes` | float | Durée maximale observée                                       |
| `has_night_train`      |   int | Présence d’un train de nuit : `1` oui, `0` non                |
| `has_day_train`        |   int | Présence d’un train de jour : `1` oui, `0` non                |
| `avg_num_stops`        | float | Nombre moyen d’arrêts intermédiaires                          |
| `avg_quality_score`    | float | Score moyen de qualité des données                            |
| `quality_issues_count` |   int | Nombre d’anomalies qualité détectées                          |
| `co2_train_kg`         | float | Émissions CO₂ estimées pour le train                          |
| `co2_plane_kg`         | float | Émissions CO₂ estimées pour l’avion                           |
| `co2_saving_kg`        | float | Gain CO₂ estimé en choisissant le train                       |
| `co2_saving_percent`   | float | Pourcentage de réduction des émissions                        |

---

## 7. Exemple de requête `/predict`

### Requête

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

### Réponse attendue

```json
{
  "prediction": "fort",
  "input": {
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
  },
  "probabilities": {
    "faible": 0.0,
    "fort": 1.0,
    "moyen": 0.0
  },
  "confidence": 1.0
}
```

---

## 8. Interprétation de la réponse

La clé `prediction` indique la classe prédite par le modèle.

La clé `probabilities` donne la probabilité associée à chaque classe :

* `faible` ;
* `moyen` ;
* `fort`.

La clé `confidence` correspond à la probabilité la plus élevée. Elle indique le niveau de confiance du modèle dans sa prédiction.

Exemple :

```json
{
  "prediction": "fort",
  "confidence": 1.0
}
```

Cela signifie que le modèle considère la liaison comme fortement candidate à la substitution avion → train.

---

## 9. Exemple de test avec `curl`

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
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
     }'
```

---

## 10. Validation technique

L’API a été testée avec Swagger à l’adresse :

```text
http://127.0.0.1:8000/docs
```

Les routes suivantes sont disponibles :

```text
GET /model-info
POST /predict
```

Le test de `/model-info` confirme que le modèle chargé est bien :

```text
gradient_boosting
```

Le test de `/predict` confirme que l’API retourne :

* une classe prédite ;
* les probabilités par classe ;
* un niveau de confiance ;
* les données d’entrée utilisées.

---

## 11. Points de vigilance

### 11.1. Cible métier construite

La variable cible `substitution_potential` n’est pas issue d’un historique réel de décisions ObRail. Elle a été construite à partir d’un score métier basé sur :

* la distance ;
* la durée ;
* la fréquence ;
* la présence d’un train de nuit ;
* le gain CO₂ ;
* la qualité des données ;
* le caractère international de la liaison.

Le modèle constitue donc un prototype d’aide à la décision.

### 11.2. Exclusion de `substitution_score`

La variable `substitution_score` n’a pas été utilisée comme variable d’entrée du modèle.

Elle a été exclue volontairement afin d’éviter une fuite de données, car la classe cible `substitution_potential` a été construite à partir de ce score.

### 11.3. Données réalistes

Il est important d’envoyer à l’API des valeurs réalistes. Par exemple, une distance de `1 km` n’est pas pertinente pour évaluer une substitution avion → train.

Les tests métier doivent donc utiliser des distances, durées et fréquences cohérentes avec des liaisons ferroviaires réelles.

---

## 12. Améliorations futures

Plusieurs améliorations peuvent être envisagées :

1. Ajouter une route permettant de prédire directement à partir d’un `route_id`.
2. Connecter l’API à PostgreSQL pour récupérer automatiquement les variables d’une liaison.
3. Ajouter un suivi des prédictions dans une table de logs.
4. Surveiller les distributions des variables en production afin de détecter une dérive des données.
5. Ajouter des données réelles de fréquentation ou de report modal avion/train.
6. Faire valider les classes par des experts métier ObRail.
7. Ajouter une authentification si l’API est exposée publiquement.

---

## 13. Conclusion

L’API REST permet d’exposer le modèle IA développé pour ObRail sous une forme simple, testable et réutilisable.

Elle répond au besoin d’intégration applicative du projet en fournissant une route `/predict` capable de retourner automatiquement le potentiel de substitution avion → train d’une liaison ferroviaire.

Cette API constitue une première brique vers une solution applicative plus complète, intégrant à terme l’entrepôt de données ObRail, le modèle IA, le monitoring et une interface utilisateur.

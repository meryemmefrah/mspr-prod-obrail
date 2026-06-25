# Dictionnaire des données — Projet IA ObRail

## 1. Objectif du document

Ce document décrit les données utilisées pour construire le modèle d’intelligence artificielle ObRail.

Le modèle vise à identifier les liaisons ferroviaires candidates à la substitution avion → train.
Chaque liaison est classée selon trois niveaux de potentiel :

```text
faible
moyen
fort
```

Le dictionnaire présente :

* les sources de données utilisées ;
* les tables issues du flux ETL ;
* les variables créées pour le dataset IA ;
* les variables utilisées pour l’entraînement ;
* la variable cible ;
* les règles de transformation et de qualité.

---

## 2. Origine des données

Les données utilisées proviennent du premier projet MSPR ObRail, dans lequel un flux ETL a été développé.

Ce flux ETL permet de collecter, transformer et harmoniser des données ferroviaires issues de plusieurs sources.

Les données finales utilisées par le projet IA sont stockées dans :

```text
data/processed/
```

Les fichiers exploités sont :

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

Ces fichiers constituent le référentiel de données ferroviaires harmonisées.

---

## 3. Dataset IA final

Le dataset utilisé pour entraîner le modèle est généré par le script :

```text
scripts/ml/build_dataset.py
```

Le fichier généré est :

```text
data/modeling/route_substitution_dataset.csv
```

Dans la version actuelle, le dataset contient :

```text
4101 lignes
35 colonnes
0 valeur manquante critique
```

Chaque ligne représente une liaison ferroviaire enrichie avec des indicateurs géographiques, temporels, environnementaux et qualité.

---

## 4. Granularité du dataset

La granularité choisie est :

```text
1 ligne = 1 liaison ferroviaire
```

Exemple :

```text
Paris → Lyon
Paris → Berlin
Lyon → Marseille
```

Ce choix est adapté au cas métier, car la décision de substitution avion → train se prend au niveau d’une liaison entre deux zones géographiques, et non au niveau d’un trajet isolé.

---

## 5. Tables sources issues de l’ETL

### 5.1. `country.csv`

| Colonne        | Description                |
| -------------- | -------------------------- |
| `country_id`   | Identifiant unique du pays |
| `country_name` | Nom du pays                |
| `country_code` | Code du pays               |

Cette table permet d’identifier le pays associé aux villes, gares et opérateurs.

---

### 5.2. `city.csv`

| Colonne      | Description                    |
| ------------ | ------------------------------ |
| `city_id`    | Identifiant unique de la ville |
| `city_name`  | Nom de la ville                |
| `country_id` | Identifiant du pays associé    |

Cette table permet de rattacher chaque gare à une ville et à un pays.

---

### 5.3. `station.csv`

| Colonne        | Description                      |
| -------------- | -------------------------------- |
| `station_id`   | Identifiant unique de la gare    |
| `station_name` | Nom de la gare                   |
| `station_code` | Code ou identifiant de la gare   |
| `latitude`     | Latitude de la gare              |
| `longitude`    | Longitude de la gare             |
| `timezone`     | Fuseau horaire                   |
| `city_id`      | Identifiant de la ville associée |

Cette table est utilisée pour récupérer les coordonnées GPS des gares et calculer les distances entre gare de départ et gare d’arrivée.

---

### 5.4. `operator.csv`

| Colonne         | Description                         |
| --------------- | ----------------------------------- |
| `operator_id`   | Identifiant unique de l’opérateur   |
| `operator_name` | Nom de l’opérateur ferroviaire      |
| `operator_code` | Code de l’opérateur                 |
| `country_id`    | Pays de rattachement de l’opérateur |

Cette table permet d’identifier les opérateurs associés aux routes ferroviaires.

---

### 5.5. `train_type.csv`

| Colonne         | Description                          |
| --------------- | ------------------------------------ |
| `train_type_id` | Identifiant unique du type de train  |
| `type_name`     | Type de train : `day`, `night`, etc. |

Cette table permet d’identifier si une liaison dispose d’un train de jour ou d’un train de nuit.

---

### 5.6. `data_source.csv`

| Colonne           | Description                     |
| ----------------- | ------------------------------- |
| `data_source_id`  | Identifiant unique de la source |
| `source_name`     | Nom de la source                |
| `source_format`   | Format de la source             |
| `source_url`      | URL de la source                |
| `extraction_date` | Date d’extraction               |
| `import_status`   | Statut d’import                 |

Cette table permet d’assurer la traçabilité des données.

---

### 5.7. `route.csv`

| Colonne                | Description                      |
| ---------------------- | -------------------------------- |
| `route_id`             | Identifiant unique de la liaison |
| `departure_station_id` | Gare de départ                   |
| `arrival_station_id`   | Gare d’arrivée                   |
| `operator_id`          | Opérateur associé                |
| `distance_km`          | Distance si disponible           |

Cette table constitue la base de construction du dataset IA.

---

### 5.8. `trip.csv`

| Colonne                | Description                        |
| ---------------------- | ---------------------------------- |
| `trip_id`              | Identifiant unique du trajet       |
| `trip_code`            | Code du trajet                     |
| `route_id`             | Identifiant de la liaison          |
| `train_type_id`        | Type de train                      |
| `data_source_id`       | Source du trajet                   |
| `service_date`         | Date de service                    |
| `departure_time`       | Heure de départ                    |
| `arrival_time`         | Heure d’arrivée                    |
| `departure_day_offset` | Décalage jour départ               |
| `arrival_day_offset`   | Décalage jour arrivée              |
| `duration_minutes`     | Durée du trajet en minutes         |
| `co2_estimated_kg`     | Émission CO₂ estimée si disponible |

Cette table est utilisée pour calculer la durée moyenne, la fréquence hebdomadaire et les types de service disponibles.

---

### 5.9. `trip_stop.csv`

| Colonne                | Description                       |
| ---------------------- | --------------------------------- |
| `trip_stop_id`         | Identifiant unique de l’arrêt     |
| `trip_id`              | Identifiant du trajet             |
| `station_id`           | Gare d’arrêt                      |
| `stop_order`           | Ordre de l’arrêt dans le parcours |
| `arrival_time`         | Heure d’arrivée à l’arrêt         |
| `departure_time`       | Heure de départ de l’arrêt        |
| `arrival_day_offset`   | Décalage jour arrivée             |
| `departure_day_offset` | Décalage jour départ              |

Cette table permet de calculer le nombre moyen d’arrêts intermédiaires d’une liaison.

---

### 5.10. `quality_check.csv`

| Colonne              | Description                                       |
| -------------------- | ------------------------------------------------- |
| `quality_check_id`   | Identifiant du contrôle qualité                   |
| `trip_id`            | Identifiant du trajet contrôlé                    |
| `has_missing_values` | Présence de valeurs manquantes                    |
| `has_time_error`     | Présence d’une incohérence horaire                |
| `is_duplicate`       | Indique si le trajet est potentiellement dupliqué |
| `quality_score`      | Score qualité du trajet                           |
| `rule_name`          | Nom de la règle de contrôle                       |
| `error_message`      | Message d’erreur éventuel                         |
| `check_date`         | Date du contrôle                                  |

Cette table permet d’intégrer la qualité des données dans la classification.

---

## 6. Variables finales du dataset IA

### 6.1. Variables d’identification

| Variable                 |   Type | Description                      | Utilisation modèle |
| ------------------------ | -----: | -------------------------------- | ------------------ |
| `route_id`               |    int | Identifiant unique de la liaison | Non                |
| `departure_station_id`   |    int | Identifiant de la gare de départ | Non                |
| `arrival_station_id`     |    int | Identifiant de la gare d’arrivée | Non                |
| `departure_station_name` | string | Nom de la gare de départ         | Non                |
| `arrival_station_name`   | string | Nom de la gare d’arrivée         | Non                |
| `departure_city_name`    | string | Ville de départ                  | Non                |
| `arrival_city_name`      | string | Ville d’arrivée                  | Non                |
| `departure_country_name` | string | Pays de départ                   | Non                |
| `arrival_country_name`   | string | Pays d’arrivée                   | Non                |
| `departure_country_code` | string | Code pays de départ              | Non                |
| `arrival_country_code`   | string | Code pays d’arrivée              | Non                |
| `operator_name`          | string | Nom de l’opérateur ferroviaire   | Non                |

Ces variables sont conservées pour la compréhension métier, la traçabilité et l’interprétation des résultats, mais elles ne sont pas utilisées directement dans le modèle.

---

### 6.2. Variables géographiques

| Variable           |  Type | Description                                                   | Utilisation modèle |
| ------------------ | ----: | ------------------------------------------------------------- | ------------------ |
| `is_international` |   int | Indique si la liaison est internationale : `1` oui, `0` non   | Oui                |
| `distance_km`      | float | Distance estimée entre la gare de départ et la gare d’arrivée | Oui                |

La distance est calculée à partir des coordonnées GPS des gares lorsque la distance n’est pas déjà disponible.

La variable `is_international` est calculée ainsi :

```text
is_international = 1 si departure_country_code != arrival_country_code
is_international = 0 sinon
```

---

### 6.3. Variables de fréquence

| Variable              |  Type | Description                                | Utilisation modèle |
| --------------------- | ----: | ------------------------------------------ | ------------------ |
| `trip_count`          |   int | Nombre de trajets observés pour la liaison | Non                |
| `weekly_frequency`    | float | Nombre estimé de trajets par semaine       | Oui                |
| `daily_frequency_avg` | float | Fréquence moyenne quotidienne              | Oui                |

La fréquence est un indicateur essentiel : une liaison peut être rapide et écologique, mais elle est moins crédible comme alternative à l’avion si elle est très peu desservie.

---

### 6.4. Variables de durée

| Variable               |  Type | Description                            | Utilisation modèle |
| ---------------------- | ----: | -------------------------------------- | ------------------ |
| `avg_duration_minutes` | float | Durée moyenne de la liaison en minutes | Oui                |
| `min_duration_minutes` | float | Durée minimale observée                | Oui                |
| `max_duration_minutes` | float | Durée maximale observée                | Oui                |

La durée permet d’évaluer la compétitivité du train face à l’avion.

---

### 6.5. Variables de type de service

| Variable          |   Type | Description                                             | Utilisation modèle |
| ----------------- | -----: | ------------------------------------------------------- | ------------------ |
| `main_train_type` | string | Type de train majoritaire sur la liaison                | Non                |
| `has_night_train` |    int | Présence d’au moins un train de nuit : `1` oui, `0` non | Oui                |
| `has_day_train`   |    int | Présence d’au moins un train de jour : `1` oui, `0` non | Oui                |

La présence d’un train de nuit est importante pour les longues distances, car elle peut rendre le train compétitif malgré une durée élevée.

---

### 6.6. Variables d’arrêts

| Variable        |  Type | Description                            | Utilisation modèle |
| --------------- | ----: | -------------------------------------- | ------------------ |
| `avg_num_stops` | float | Nombre moyen d’arrêts intermédiaires   | Oui                |
| `min_num_stops` | float | Nombre minimal d’arrêts intermédiaires | Non                |
| `max_num_stops` | float | Nombre maximal d’arrêts intermédiaires | Non                |

Le nombre d’arrêts est utilisé pour représenter la complexité du trajet.

---

### 6.7. Variables de qualité des données

| Variable               |  Type | Description                              | Utilisation modèle |
| ---------------------- | ----: | ---------------------------------------- | ------------------ |
| `avg_quality_score`    | float | Score qualité moyen associé à la liaison | Oui                |
| `min_quality_score`    | float | Score qualité minimal observé            | Non                |
| `quality_issues_count` |   int | Nombre d’anomalies qualité détectées     | Oui                |

Ces variables évitent de recommander fortement une liaison dont les données sont peu fiables.

---

### 6.8. Variables environnementales

| Variable             |  Type | Description                             | Utilisation modèle |
| -------------------- | ----: | --------------------------------------- | ------------------ |
| `co2_train_kg`       | float | Émissions CO₂ estimées en train         | Oui                |
| `co2_plane_kg`       | float | Émissions CO₂ estimées en avion         | Oui                |
| `co2_saving_kg`      | float | Gain CO₂ estimé en choisissant le train | Oui                |
| `co2_saving_percent` | float | Pourcentage de réduction des émissions  | Oui                |

Les variables CO₂ permettent d’intégrer la dimension environnementale du projet ObRail.

Les estimations sont calculées à partir de la distance et de facteurs d’émission simplifiés.

---

### 6.9. Variable de score métier

| Variable             |  Type | Description                                             | Utilisation modèle |
| -------------------- | ----: | ------------------------------------------------------- | ------------------ |
| `substitution_score` | float | Score métier de potentiel de substitution avion → train | Non                |

La variable `substitution_score` est utilisée pour construire la cible `substitution_potential`.

Elle est exclue de l’entraînement afin d’éviter une fuite de données.

---

### 6.10. Variable cible

| Variable                 |   Type | Description                             | Utilisation modèle |
| ------------------------ | -----: | --------------------------------------- | ------------------ |
| `substitution_potential` | string | Potentiel de substitution avion → train | Cible              |

La cible peut prendre trois valeurs :

```text
faible
moyen
fort
```

---

## 7. Variables utilisées pour l’entraînement

Les variables utilisées par le modèle final sont :

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

---

## 8. Variables exclues de l’entraînement

Certaines variables sont conservées dans le dataset mais exclues de l’entraînement.

| Variable                 | Raison de l’exclusion                                                 |
| ------------------------ | --------------------------------------------------------------------- |
| `route_id`               | Identifiant technique sans valeur prédictive générale                 |
| `departure_station_id`   | Identifiant technique                                                 |
| `arrival_station_id`     | Identifiant technique                                                 |
| `departure_station_name` | Variable textuelle non encodée                                        |
| `arrival_station_name`   | Variable textuelle non encodée                                        |
| `departure_city_name`    | Variable textuelle non encodée                                        |
| `arrival_city_name`      | Variable textuelle non encodée                                        |
| `departure_country_name` | Variable textuelle non encodée                                        |
| `arrival_country_name`   | Variable textuelle non encodée                                        |
| `departure_country_code` | Information déjà synthétisée par `is_international`                   |
| `arrival_country_code`   | Information déjà synthétisée par `is_international`                   |
| `operator_name`          | Variable textuelle non encodée                                        |
| `trip_count`             | Variable proche de `weekly_frequency`                                 |
| `main_train_type`        | Information déjà synthétisée par `has_day_train` et `has_night_train` |
| `min_num_stops`          | Variable secondaire                                                   |
| `max_num_stops`          | Variable secondaire                                                   |
| `min_quality_score`      | Variable secondaire                                                   |
| `substitution_score`     | Exclue pour éviter une fuite de données                               |

---

## 9. Création de la cible métier

La cible `substitution_potential` est construite à partir de `substitution_score`.

Le score métier prend en compte :

| Critère             | Rôle                                                                  |
| ------------------- | --------------------------------------------------------------------- |
| Distance            | Identifier les distances pertinentes pour une concurrence train/avion |
| Durée               | Mesurer la compétitivité temporelle du train                          |
| Fréquence           | Mesurer la crédibilité de l’offre ferroviaire                         |
| Train de nuit       | Favoriser les longues distances avec service de nuit                  |
| Gain CO₂            | Mesurer l’intérêt environnemental                                     |
| Qualité des données | Éviter les recommandations peu fiables                                |
| International       | Valoriser les liaisons stratégiques européennes                       |

Les classes sont ensuite dérivées du score :

```text
score élevé  → fort
score moyen  → moyen
score faible → faible
```

---

## 10. Répartition actuelle de la cible

Dans la version actuelle du dataset :

```text
moyen     2919
faible     733
fort       449
```

Cette répartition permet d’entraîner un modèle de classification multiclasses.

---

## 11. Contrôles qualité appliqués

Avant l’entraînement, plusieurs contrôles sont effectués :

| Contrôle                     | Résultat attendu |
| ---------------------------- | ---------------: |
| Valeurs manquantes critiques |                0 |
| Distances <= 0               |                0 |
| Durées <= 0                  |                0 |
| Fréquences <= 0              |                0 |
| Présence des trois classes   |              Oui |

Dans la version actuelle :

```text
Distances <= 0   : 0
Durées <= 0      : 0
Fréquences <= 0  : 0
Valeurs manquantes critiques : 0
```

---

## 12. Données d’entraînement, validation et test

Le dataset final est séparé en trois fichiers :

```text
data/modeling/train.csv
data/modeling/validation.csv
data/modeling/test.csv
```

La séparation utilisée est stratifiée pour conserver les proportions de classes.

Répartition actuelle :

```text
Train      : 2870 lignes
Validation : 615 lignes
Test       : 616 lignes
```

Répartition par classe :

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

## 13. Types de données attendus par l’API `/predict`

L’API `/predict` attend uniquement les variables utilisées par le modèle.

| Variable               | Type attendu | Contrainte     |
| ---------------------- | -----------: | -------------- |
| `is_international`     |          int | 0 ou 1         |
| `distance_km`          |        float | > 0            |
| `weekly_frequency`     |        float | > 0            |
| `daily_frequency_avg`  |        float | > 0            |
| `avg_duration_minutes` |        float | > 0            |
| `min_duration_minutes` |        float | > 0            |
| `max_duration_minutes` |        float | > 0            |
| `has_night_train`      |          int | 0 ou 1         |
| `has_day_train`        |          int | 0 ou 1         |
| `avg_num_stops`        |        float | >= 0           |
| `avg_quality_score`    |        float | entre 0 et 100 |
| `quality_issues_count` |          int | >= 0           |
| `co2_train_kg`         |        float | >= 0           |
| `co2_plane_kg`         |        float | >= 0           |
| `co2_saving_kg`        |        float | réel           |
| `co2_saving_percent`   |        float | réel           |

---

## 14. Exemple d’entrée API

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

---

## 15. Exemple de sortie API

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

## 16. Hypothèses et limites

### 16.1. Cible construite

La cible `substitution_potential` est une cible métier construite. Elle n’est pas issue d’un historique réel de décisions ObRail.

Le modèle apprend donc à reproduire une logique d’aide à la décision, et non un comportement historique observé.

### 16.2. Facteurs CO₂ simplifiés

Les émissions CO₂ sont estimées à partir de facteurs simplifiés. Ces facteurs pourront être affinés avec des données officielles plus précises.

### 16.3. Données majoritairement issues de l’ETL existant

Le dataset dépend fortement des données harmonisées issues du premier MSPR. Toute limite du flux ETL peut donc influencer le modèle IA.

### 16.4. Variables textuelles non utilisées

Les noms de villes, pays, gares et opérateurs ne sont pas utilisés directement dans le modèle. Ils sont conservés pour la traçabilité et l’interprétation.

---

## 17. Recommandations futures

Pour améliorer le dataset, il serait pertinent de :

1. Ajouter des labels validés par des experts métier.
2. Ajouter des données réelles de fréquentation.
3. Ajouter des données de trafic aérien sur les mêmes liaisons.
4. Utiliser des facteurs CO₂ officiels plus détaillés.
5. Intégrer des données économiques ou démographiques.
6. Ajouter une variable de correspondance avec des aéroports.
7. Ajouter des indicateurs de concurrence avion/train.
8. Connecter directement le modèle à PostgreSQL via un `route_id`.
9. Ajouter des logs de prédiction pour alimenter une boucle de retour.
10. Mettre en place un monitoring de dérive des données.

---

## 18. Conclusion

Le dataset IA ObRail est construit à partir des données harmonisées du flux ETL existant.

Il transforme des données ferroviaires relationnelles en un dataset exploitable par un modèle de classification.

Les variables retenues couvrent les dimensions essentielles du problème :

```text
géographie
durée
fréquence
type de train
qualité des données
impact environnemental
```

Ce dictionnaire permet de comprendre, reproduire et justifier les choix de données utilisés pour entraîner le modèle de prédiction du potentiel de substitution avion → train.

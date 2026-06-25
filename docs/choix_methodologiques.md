# Choix méthodologiques — Projet IA ObRail

## 1. Objectif du document

Ce document présente et justifie les principaux choix méthodologiques réalisés dans le cadre du projet IA ObRail.

Le projet consiste à développer un modèle prédictif permettant d’identifier les liaisons ferroviaires candidates à la substitution avion → train.

Les choix présentés concernent :

* le choix de l’axe métier ;
* les données utilisées ;
* la création du dataset IA ;
* la création de la variable cible ;
* les modèles testés ;
* les métriques d’évaluation ;
* la sélection du modèle final ;
* l’exposition du modèle via API ;
* les limites et perspectives d’amélioration.

---

## 2. Choix de l’axe métier

### 2.1. Axe retenu

L’axe métier retenu est :

```text
Identification automatique des liaisons ferroviaires candidates à la substitution avion par train.
```

L’objectif est de classer chaque liaison ferroviaire selon son potentiel de substitution à l’avion :

```text
faible
moyen
fort
```

Cette classification permet d’aider ObRail à repérer les liaisons les plus pertinentes à valoriser ou à développer dans une logique de mobilité durable.

---

### 2.2. Justification du choix

Cet axe a été retenu pour plusieurs raisons.

Premièrement, il est directement aligné avec la mission d’ObRail, qui souhaite promouvoir le train comme alternative crédible à l’avion sur les trajets intra-européens.

Deuxièmement, il est cohérent avec les données déjà disponibles grâce au premier projet MSPR ETL. Les données extraites et harmonisées contiennent déjà des informations sur les gares, les routes, les trajets, les horaires, les types de trains, les fréquences et les contrôles qualité.

Troisièmement, cet axe est réaliste dans le cadre du projet. Contrairement à la prédiction de fréquentation ou à la saturation des lignes, il ne nécessite pas obligatoirement de données historiques de passagers, souvent difficiles à obtenir.

Enfin, cet axe est facilement compréhensible par un jury ou un client professionnel. Il permet de produire des résultats interprétables : une liaison est classée comme ayant un potentiel faible, moyen ou fort.

---

## 3. Axes non retenus

Plusieurs autres axes ont été envisagés, mais n’ont pas été retenus pour la première version du projet.

### 3.1. Prédiction de la fréquentation future

Cet axe aurait consisté à prédire le nombre futur de passagers sur certaines liaisons.

Il n’a pas été retenu car les données disponibles ne contiennent pas d’historique fiable de fréquentation par liaison. Sans données temporelles sur le nombre de voyageurs, le modèle aurait été difficile à entraîner correctement.

---

### 3.2. Prévision de saturation ou congestion

Cet axe aurait consisté à identifier les liaisons présentant un risque de saturation.

Il n’a pas été retenu car il aurait nécessité des données supplémentaires :

* capacité des trains ;
* nombre de passagers ;
* taux d’occupation ;
* retards ;
* incidents ;
* historique de circulation.

Ces données ne sont pas disponibles dans le périmètre actuel.

---

### 3.3. Estimation simple du gain CO₂

Cet axe aurait consisté uniquement à calculer les émissions évitées en prenant le train plutôt que l’avion.

Il n’a pas été retenu comme sujet principal, car il s’agit davantage d’un calcul métier que d’un véritable problème de classification ou de prédiction. En revanche, le gain CO₂ a été intégré comme variable explicative dans le modèle final.

---

## 4. Choix des données

### 4.1. Réutilisation du flux ETL existant

Le projet IA s’appuie sur les données harmonisées issues du premier MSPR ObRail.

Ces données sont stockées dans :

```text
data/processed/
```

Les principales tables utilisées sont :

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

Ce choix permet de valoriser le travail réalisé dans le premier MSPR et d’assurer une continuité logique :

```text
ETL → Données harmonisées → Dataset IA → Modèle → API
```

---

### 4.2. Justification de la réutilisation des données ETL

Les données ETL sont adaptées au projet IA car elles contiennent les informations nécessaires pour caractériser une liaison ferroviaire :

* gare de départ ;
* gare d’arrivée ;
* pays de départ ;
* pays d’arrivée ;
* horaires ;
* durée ;
* type de train ;
* fréquence ;
* arrêts ;
* score qualité ;
* source de données.

Ces informations permettent de construire des indicateurs pertinents pour évaluer si une liaison ferroviaire peut être une alternative crédible à l’avion.

---

## 5. Choix de la granularité

La granularité retenue est :

```text
1 ligne = 1 liaison ferroviaire
```

Ce choix est justifié par le cas métier. La substitution avion → train ne se décide pas au niveau d’un trajet isolé, mais au niveau d’une liaison entre deux zones géographiques.

Par exemple, on cherche à évaluer le potentiel de liaisons comme :

```text
Paris → Lyon
Paris → Berlin
Lyon → Marseille
```

et non seulement un train précis circulant à une date donnée.

---

## 6. Construction du dataset IA

Le dataset IA est généré par le script :

```text
scripts/ml/build_dataset.py
```

Le fichier final est :

```text
data/modeling/route_substitution_dataset.csv
```

Dans la version actuelle, le dataset contient :

```text
4101 lignes
35 colonnes
0 valeur manquante critique
```

Les étapes principales de construction sont :

1. chargement des fichiers issus de l’ETL ;
2. jointure entre routes, gares, villes, pays, opérateurs et trajets ;
3. calcul de la distance entre gares ;
4. agrégation des durées par liaison ;
5. calcul de la fréquence hebdomadaire ;
6. identification des trains de jour et de nuit ;
7. calcul du nombre moyen d’arrêts ;
8. intégration des scores qualité ;
9. estimation des émissions CO₂ train et avion ;
10. calcul du score métier de substitution ;
11. création de la variable cible ;
12. export du dataset final.

---

## 7. Choix des variables explicatives

Les variables retenues pour l’entraînement du modèle couvrent plusieurs dimensions du problème.

### 7.1. Dimension géographique

```text
is_international
distance_km
```

La distance est essentielle car la concurrence entre train et avion dépend fortement de la longueur du trajet.

La variable `is_international` permet d’identifier les liaisons transfrontalières, particulièrement intéressantes dans un contexte européen.

---

### 7.2. Dimension temporelle

```text
avg_duration_minutes
min_duration_minutes
max_duration_minutes
```

La durée permet de mesurer la compétitivité du train face à l’avion.

Un trajet ferroviaire court ou raisonnablement long peut être plus attractif qu’un vol, surtout si l’on tient compte des temps d’accès aux aéroports, des contrôles et de l’embarquement.

---

### 7.3. Dimension fréquence

```text
weekly_frequency
daily_frequency_avg
```

La fréquence indique la crédibilité de l’offre ferroviaire.

Une liaison rapide mais très peu fréquente est moins pertinente comme alternative à l’avion.

---

### 7.4. Dimension type de service

```text
has_night_train
has_day_train
```

La présence d’un train de nuit est importante pour les longues distances.

Un trajet de 8 à 12 heures peut être acceptable s’il est effectué de nuit, car le temps de trajet peut être partiellement transformé en temps de repos.

---

### 7.5. Dimension complexité du trajet

```text
avg_num_stops
```

Le nombre d’arrêts permet d’approcher la complexité de la liaison.

Une liaison avec beaucoup d’arrêts peut être moins compétitive qu’une liaison directe ou semi-directe.

---

### 7.6. Dimension qualité des données

```text
avg_quality_score
quality_issues_count
```

Ces variables permettent d’éviter de recommander fortement une liaison lorsque les données sont peu fiables.

La qualité des données est importante car le modèle doit produire des recommandations exploitables par ObRail.

---

### 7.7. Dimension environnementale

```text
co2_train_kg
co2_plane_kg
co2_saving_kg
co2_saving_percent
```

Ces variables permettent d’intégrer la dimension écologique au modèle.

Le gain CO₂ est central dans le projet, car ObRail cherche à promouvoir le train comme mode de transport bas-carbone.

---

## 8. Variables exclues de l’entraînement

Certaines variables sont conservées dans le dataset mais exclues du modèle.

### 8.1. Variables d’identification

Les variables suivantes ne sont pas utilisées comme variables d’entrée :

```text
route_id
departure_station_id
arrival_station_id
departure_station_name
arrival_station_name
departure_city_name
arrival_city_name
departure_country_name
arrival_country_name
operator_name
```

Elles sont utiles pour la traçabilité et l’interprétation, mais ne sont pas nécessaires pour le modèle actuel.

---

### 8.2. Variable `substitution_score`

La variable `substitution_score` est volontairement exclue de l’entraînement.

Elle sert à construire la cible `substitution_potential`.

L’utiliser comme variable d’entrée provoquerait une fuite de données, car le modèle apprendrait directement la règle utilisée pour générer la cible.

Ce choix permet d’obtenir une évaluation plus honnête du modèle.

---

## 9. Création de la variable cible

### 9.1. Cible retenue

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

---

### 9.2. Pourquoi une cible construite ?

Les données disponibles ne contiennent pas de label historique indiquant si une liaison a réellement remplacé une liaison aérienne.

Il a donc été nécessaire de construire une cible métier à partir d’indicateurs objectifs :

* distance ;
* durée ;
* fréquence ;
* présence d’un train de nuit ;
* gain CO₂ ;
* qualité de données ;
* caractère international.

Cette approche est adaptée à un prototype d’aide à la décision.

---

### 9.3. Passage d’une règle stricte à un score métier

Une première version de la cible avait été créée à partir de règles strictes.

Cette première version produisait une répartition trop déséquilibrée :

```text
faible : 4022
moyen  : 72
fort   : 8
```

Cette répartition rendait l’entraînement peu pertinent, car la classe `fort` était trop peu représentée.

La méthode a donc été améliorée avec un score métier :

```text
substitution_score
```

Ce score est ensuite transformé en trois classes :

```text
score faible → faible
score moyen  → moyen
score élevé  → fort
```

La nouvelle répartition est plus exploitable :

```text
moyen  : 2919
faible : 733
fort   : 449
```

---

## 10. Préparation et séparation des données

Le dataset est séparé en trois parties :

```text
train.csv
validation.csv
test.csv
```

La stratégie utilisée est une séparation stratifiée.

Ce choix permet de conserver les proportions de classes dans chaque jeu de données.

Répartition actuelle :

```text
Train      : 2870 lignes
Validation : 615 lignes
Test       : 616 lignes
```

La séparation utilisée est :

```text
70 % entraînement
15 % validation
15 % test
```

---

## 11. Choix des modèles candidats

Plusieurs familles de modèles ont été testées afin de répondre à l’exigence de comparaison.

Les modèles entraînés sont :

```text
Logistic Regression
Decision Tree
Random Forest
Gradient Boosting
```

---

### 11.1. Régression logistique

La régression logistique a été utilisée comme modèle de référence.

Elle est simple, rapide à entraîner et interprétable.

Elle permet de disposer d’un point de comparaison minimal.

---

### 11.2. Arbre de décision

L’arbre de décision a été testé car il est facilement explicable.

Il permet de visualiser une logique de décision proche de règles métier.

Il peut cependant être sensible au surapprentissage si sa profondeur n’est pas contrôlée.

---

### 11.3. Random Forest

Le Random Forest combine plusieurs arbres de décision.

Il est généralement plus robuste qu’un arbre seul et gère bien les interactions entre variables.

Il est adapté aux données tabulaires structurées.

---

### 11.4. Gradient Boosting

Le Gradient Boosting construit plusieurs arbres de manière séquentielle, chaque arbre corrigeant les erreurs des précédents.

Il est performant sur des données tabulaires et permet d’obtenir de bons résultats sans nécessiter un réseau de neurones.

C’est le modèle qui a obtenu les meilleures performances dans ce projet.

---

## 12. Pourquoi ne pas utiliser un réseau de neurones ?

Un réseau de neurones n’a pas été retenu pour la version principale du projet.

Les raisons sont les suivantes :

1. le dataset est tabulaire ;
2. le volume de données reste limité ;
3. les modèles à base d’arbres sont plus adaptés et plus interprétables ;
4. un réseau de neurones serait plus complexe à justifier ;
5. le besoin métier demande de l’explicabilité.

Dans ce contexte, Random Forest et Gradient Boosting sont plus pertinents.

---

## 13. Choix des métriques

La tâche est une classification multiclasses.

Les métriques utilisées sont :

```text
accuracy
precision_macro
recall_macro
f1_macro
f1_weighted
```

---

### 13.1. Accuracy

L’accuracy mesure la proportion globale de prédictions correctes.

Elle est utile mais insuffisante lorsque les classes sont déséquilibrées.

---

### 13.2. Precision macro

La précision macro mesure la précision moyenne sur les classes.

Elle permet de vérifier si le modèle évite les faux positifs sur chaque classe.

---

### 13.3. Recall macro

Le rappel macro mesure la capacité du modèle à retrouver les exemples de chaque classe.

Il est important pour ne pas ignorer les classes minoritaires.

---

### 13.4. F1 macro

Le F1 macro est la métrique principale retenue.

Il combine précision et rappel, puis moyenne les résultats sur chaque classe.

Ce choix est pertinent car les classes ne sont pas parfaitement équilibrées.

---

### 13.5. F1 weighted

Le F1 weighted pondère les scores par le nombre d’exemples de chaque classe.

Il complète le F1 macro en donnant une vision globale tenant compte de la distribution réelle des classes.

---

## 14. Résultats obtenus

Les performances sur validation sont les suivantes :

| Modèle              | Accuracy | Precision macro | Recall macro | F1 macro | F1 weighted |
| ------------------- | -------: | --------------: | -----------: | -------: | ----------: |
| Gradient Boosting   |   1.0000 |          1.0000 |       1.0000 |   1.0000 |      1.0000 |
| Random Forest       |   0.9902 |          0.9738 |       0.9954 |   0.9842 |      0.9904 |
| Decision Tree       |   0.9886 |          0.9781 |       0.9820 |   0.9800 |      0.9887 |
| Logistic Regression |   0.7545 |          0.7037 |       0.8744 |   0.7386 |      0.7667 |

Le meilleur modèle sélectionné est :

```text
Gradient Boosting
```

---

## 15. Évaluation finale sur le jeu de test

Après sélection, le modèle Gradient Boosting est réentraîné sur les jeux train + validation, puis évalué sur le jeu de test.

Performances finales :

| Métrique        | Valeur |
| --------------- | -----: |
| Accuracy        | 0.9919 |
| Precision macro | 0.9805 |
| Recall macro    | 0.9921 |
| F1 macro        | 0.9861 |
| F1 weighted     | 0.9920 |

Matrice de confusion :

| Classe réelle | Prédit faible | Prédit moyen | Prédit fort |
| ------------- | ------------: | -----------: | ----------: |
| faible        |           110 |            0 |           0 |
| moyen         |             0 |          434 |           4 |
| fort          |             0 |            1 |          67 |

Le modèle réalise 5 erreurs sur 616 exemples de test.

---

## 16. Interprétation des résultats

Les résultats sont très élevés.

Cela s’explique par le fait que la cible est une cible métier construite à partir d’indicateurs structurés.

Le modèle apprend donc à reproduire une logique métier cohérente, et non un comportement historique complexe ou bruité.

Il est important de présenter le modèle comme un prototype d’aide à la décision.

Une version future devrait intégrer des labels validés par des experts métier ou des données réelles de report modal avion/train.

---

## 17. Choix de sauvegarde du modèle

Le modèle final est sauvegardé avec `joblib`.

Fichier généré :

```text
models/substitution_model.joblib
```

Le choix de `joblib` est adapté aux modèles scikit-learn.

Il permet de recharger le modèle facilement dans un script de prédiction ou une API.

Les métriques sont sauvegardées dans :

```text
models/model_metrics.json
```

Ce fichier permet de documenter :

* le modèle retenu ;
* les variables d’entrée ;
* les métriques ;
* la matrice de confusion ;
* les limites liées à la variable cible.

---

## 18. Choix d’exposition via API

Le modèle est exposé via une API REST développée avec FastAPI.

Les routes IA sont :

```text
GET /model-info
POST /predict
```

---

### 18.1. Justification du choix de FastAPI

FastAPI a été retenu car il permet :

* de créer rapidement une API REST ;
* de valider automatiquement les données d’entrée ;
* de générer une documentation Swagger ;
* d’intégrer facilement un modèle Python ;
* de proposer une route `/predict` exploitable par une future application.

---

### 18.2. Route `/model-info`

Cette route retourne :

* le meilleur modèle ;
* les variables utilisées ;
* la colonne cible ;
* les métriques de test ;
* la note sur l’exclusion de `substitution_score`.

Elle permet de vérifier que l’API charge bien le bon modèle.

---

### 18.3. Route `/predict`

Cette route reçoit les variables d’une liaison ferroviaire et retourne :

* la classe prédite ;
* les probabilités par classe ;
* le niveau de confiance ;
* les données d’entrée.

Exemple de sortie :

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

## 19. Choix de reproductibilité

Plusieurs choix ont été faits pour rendre le projet reproductible.

### 19.1. Scripts séparés

Le pipeline est découpé en scripts spécialisés :

```text
build_dataset.py
split_dataset.py
train_models.py
generate_evaluation_artifacts.py
predict.py
```

Chaque script a une responsabilité claire.

---

### 19.2. Séparation des données

Les fichiers de sortie sont sauvegardés dans :

```text
data/modeling/
```

Cela permet de relancer séparément les étapes de modélisation sans refaire tout l’ETL.

---

### 19.3. Sauvegarde des métriques

Les métriques sont sauvegardées dans :

```text
models/model_metrics.json
reports/model_comparison.csv
reports/rapport_evaluation.md
```

Cela permet de conserver une trace des performances obtenues.

---

### 19.4. Graine aléatoire

Les scripts utilisent une graine aléatoire fixe :

```text
RANDOM_STATE = 42
```

Cela permet d’obtenir des résultats reproductibles lors de la séparation des données et de l’entraînement.

---

## 20. Choix liés à la qualité des données

Le dataset final est contrôlé avant l’entraînement.

Les contrôles portent notamment sur :

```text
valeurs manquantes
distances nulles ou négatives
durées nulles ou négatives
fréquences nulles ou négatives
répartition de la cible
```

Une liaison incohérente avec une distance de 0 km a été supprimée.

Le dataset final contient donc :

```text
Distances <= 0   : 0
Durées <= 0      : 0
Fréquences <= 0  : 0
```

Ces contrôles permettent de sécuriser la qualité du modèle.

---

## 21. Choix réglementaires et éthiques

Le projet ne manipule pas de données personnelles.

Cependant, plusieurs principes ont été respectés :

* traçabilité des sources ;
* documentation des transformations ;
* transparence sur la cible construite ;
* exclusion des variables pouvant provoquer une fuite de données ;
* documentation des limites ;
* explicabilité des choix méthodologiques.

Le modèle est présenté comme une aide à la décision, et non comme un système automatique de décision publique.

---

## 22. Limites méthodologiques

Le projet présente plusieurs limites.

### 22.1. Cible non issue de labels historiques

La cible est construite à partir d’un score métier.

Elle n’est pas encore validée par des experts ObRail ou par des données réelles de report modal.

---

### 22.2. Estimations CO₂ simplifiées

Les émissions CO₂ sont estimées à partir de facteurs simplifiés.

Ces facteurs devront être remplacés ou enrichis par des facteurs officiels plus précis.

---

### 22.3. Couverture géographique limitée

Le dataset dépend des sources intégrées dans l’ETL.

Certaines zones ou certains pays peuvent être sous-représentés.

---

### 22.4. Pas encore de monitoring en production

L’API permet d’exposer le modèle, mais il n’existe pas encore de système complet de suivi en production.

Il serait nécessaire d’ajouter :

* logs de prédiction ;
* suivi des erreurs ;
* suivi de la dérive des données ;
* suivi des distributions des variables.

---

## 23. Perspectives d’amélioration

Les améliorations futures recommandées sont :

1. Faire valider les règles de score par des experts métier.
2. Ajouter des données réelles de fréquentation.
3. Ajouter des données aériennes sur les liaisons comparables.
4. Ajouter des facteurs CO₂ plus précis.
5. Ajouter des données démographiques ou économiques.
6. Tester XGBoost ou LightGBM.
7. Ajouter une optimisation d’hyperparamètres plus poussée.
8. Ajouter une route API permettant de prédire à partir d’un `route_id`.
9. Connecter directement le modèle à PostgreSQL.
10. Mettre en place un monitoring MLOps.

---

## 24. Conclusion

Les choix méthodologiques réalisés permettent de construire une solution IA cohérente, documentée et reproductible.

Le projet suit une chaîne complète :

```text
Données ETL
→ Dataset IA
→ Analyse exploratoire
→ Création de la cible métier
→ Séparation train / validation / test
→ Entraînement de plusieurs modèles
→ Évaluation
→ Sauvegarde
→ Prédiction locale
→ API REST
```

Le modèle retenu, Gradient Boosting, offre les meilleures performances sur le jeu de test.

Les résultats doivent cependant être interprétés dans le cadre d’un prototype d’aide à la décision, car la cible est construite à partir d’un score métier.

La solution constitue une base solide pour une future intégration applicative ObRail et pour des améliorations MLOps plus avancées.

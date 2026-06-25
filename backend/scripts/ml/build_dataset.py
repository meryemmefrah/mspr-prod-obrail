from pathlib import Path
import json
import math
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELING_DIR = PROJECT_ROOT / "data" / "modeling"

OUTPUT_DATASET = MODELING_DIR / "route_substitution_dataset.csv"
OUTPUT_METADATA = MODELING_DIR / "dataset_metadata.json"


# Constantes provisoires pour une V1.
# À documenter dans le rapport et à remplacer plus tard par des facteurs ADEME précis si besoin.
DEFAULT_TRAIN_CO2_KG_PER_KM = 0.014
DEFAULT_PLANE_CO2_KG_PER_KM = 0.230


REQUIRED_FILES = {
    "country": "country.csv",
    "city": "city.csv",
    "station": "station.csv",
    "operator": "operator.csv",
    "train_type": "train_type.csv",
    "route": "route.csv",
    "trip": "trip.csv",
    "trip_stop": "trip_stop.csv",
    "quality_check": "quality_check.csv",
}


def read_csv_table(name: str) -> pd.DataFrame:
    file_name = REQUIRED_FILES[name]
    path = PROCESSED_DIR / file_name

    if not path.exists():
        raise FileNotFoundError(f"Fichier manquant : {path}")

    df = pd.read_csv(path)
    df.columns = [col.strip() for col in df.columns]
    return df


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def haversine_distance_km(lat1, lon1, lat2, lon2):
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return None

    radius_km = 6371.0

    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_km * c


def parse_time_to_minutes(value, day_offset=0):
    if pd.isna(value):
        return None

    value = str(value).strip()
    if not value:
        return None

    try:
        parts = value.split(":")
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2]) if len(parts) > 2 else 0

        offset = 0 if pd.isna(day_offset) else int(day_offset)
        return offset * 1440 + hours * 60 + minutes + round(seconds / 60)
    except Exception:
        return None


def compute_duration_minutes(row):
    existing_duration = pd.to_numeric(row.get("duration_minutes"), errors="coerce")
    if pd.notna(existing_duration) and existing_duration > 0:
        return float(existing_duration)

    departure_minutes = parse_time_to_minutes(
        row.get("departure_time"),
        row.get("departure_day_offset", 0),
    )

    arrival_minutes = parse_time_to_minutes(
        row.get("arrival_time"),
        row.get("arrival_day_offset", 0),
    )

    if departure_minutes is None or arrival_minutes is None:
        return None

    duration = arrival_minutes - departure_minutes

    if duration <= 0:
        return None

    return float(duration)


def build_station_dimension(station, city, country):
    station = station.copy()
    city = city.copy()
    country = country.copy()

    station["latitude"] = to_numeric(station["latitude"])
    station["longitude"] = to_numeric(station["longitude"])

    station_city = station.merge(city, on="city_id", how="left")
    station_city_country = station_city.merge(country, on="country_id", how="left")

    return station_city_country[
        [
            "station_id",
            "station_name",
            "station_code",
            "latitude",
            "longitude",
            "timezone",
            "city_id",
            "city_name",
            "country_id",
            "country_name",
            "country_code",
        ]
    ]


def build_route_base(route, station_dim, operator):
    route = route.copy()
    operator = operator.copy()

    departure_dim = station_dim.add_prefix("departure_")
    arrival_dim = station_dim.add_prefix("arrival_")

    route_base = route.merge(
        departure_dim,
        left_on="departure_station_id",
        right_on="departure_station_id",
        how="left",
    )

    route_base = route_base.merge(
        arrival_dim,
        left_on="arrival_station_id",
        right_on="arrival_station_id",
        how="left",
    )

    route_base = route_base.merge(operator, on="operator_id", how="left")

    route_base["distance_km"] = to_numeric(route_base.get("distance_km"))

    calculated_distance = route_base.apply(
        lambda row: haversine_distance_km(
            row.get("departure_latitude"),
            row.get("departure_longitude"),
            row.get("arrival_latitude"),
            row.get("arrival_longitude"),
        ),
        axis=1,
    )

    route_base["distance_km"] = route_base["distance_km"].fillna(calculated_distance)
    route_base["distance_km"] = route_base["distance_km"].round(2)

    route_base["is_international"] = (
        route_base["departure_country_code"].astype(str)
        != route_base["arrival_country_code"].astype(str)
    ).astype(int)

    return route_base


def build_trip_aggregation(trip, train_type):
    trip = trip.copy()
    train_type = train_type.copy()

    trip["duration_minutes"] = trip.apply(compute_duration_minutes, axis=1)
    trip["co2_estimated_kg"] = to_numeric(trip.get("co2_estimated_kg"))

    trip = trip.merge(train_type, on="train_type_id", how="left")

    trip["type_name"] = trip["type_name"].fillna("unknown").astype(str).str.lower()
    trip["is_night_trip"] = (trip["type_name"] == "night").astype(int)
    trip["is_day_trip"] = (trip["type_name"] == "day").astype(int)

    if "service_date" in trip.columns:
        trip["service_date"] = pd.to_datetime(trip["service_date"], errors="coerce")
    else:
        trip["service_date"] = pd.NaT

    base_agg = trip.groupby("route_id").agg(
        trip_count=("trip_id", "count"),
        avg_duration_minutes=("duration_minutes", "mean"),
        min_duration_minutes=("duration_minutes", "min"),
        max_duration_minutes=("duration_minutes", "max"),
        has_night_train=("is_night_trip", "max"),
        has_day_train=("is_day_trip", "max"),
        avg_existing_train_co2_kg=("co2_estimated_kg", "mean"),
        service_days_count=("service_date", lambda x: x.dropna().dt.date.nunique()),
        first_service_date=("service_date", "min"),
        last_service_date=("service_date", "max"),
    ).reset_index()

    type_mode = (
        trip.groupby("route_id")["type_name"]
        .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else "unknown")
        .reset_index()
        .rename(columns={"type_name": "main_train_type"})
    )

    base_agg = base_agg.merge(type_mode, on="route_id", how="left")

    def compute_weekly_frequency(row):
        trip_count = row["trip_count"]

        first_date = row["first_service_date"]
        last_date = row["last_service_date"]

        if pd.isna(first_date) or pd.isna(last_date):
            return trip_count

        observed_days = (last_date - first_date).days + 1

        if observed_days <= 0:
            return trip_count

        if observed_days <= 7:
            return trip_count

        return trip_count / observed_days * 7

    base_agg["weekly_frequency"] = base_agg.apply(compute_weekly_frequency, axis=1)
    base_agg["daily_frequency_avg"] = base_agg["weekly_frequency"] / 7

    numeric_cols = [
        "avg_duration_minutes",
        "min_duration_minutes",
        "max_duration_minutes",
        "weekly_frequency",
        "daily_frequency_avg",
        "avg_existing_train_co2_kg",
    ]

    for col in numeric_cols:
        base_agg[col] = to_numeric(base_agg[col]).round(2)

    return base_agg


def build_stops_aggregation(trip, trip_stop):
    trip = trip[["trip_id", "route_id"]].copy()
    trip_stop = trip_stop.copy()

    trip_stop_count = (
        trip_stop.groupby("trip_id")
        .agg(stop_count=("station_id", "count"))
        .reset_index()
    )

    trip_stop_count["num_intermediate_stops"] = (
        trip_stop_count["stop_count"] - 2
    ).clip(lower=0)

    trip_stop_count = trip_stop_count.merge(trip, on="trip_id", how="left")

    route_stops = (
        trip_stop_count.groupby("route_id")
        .agg(
            avg_num_stops=("num_intermediate_stops", "mean"),
            min_num_stops=("num_intermediate_stops", "min"),
            max_num_stops=("num_intermediate_stops", "max"),
        )
        .reset_index()
    )

    for col in ["avg_num_stops", "min_num_stops", "max_num_stops"]:
        route_stops[col] = to_numeric(route_stops[col]).round(2)

    return route_stops


def build_quality_aggregation(trip, quality_check):
    trip = trip[["trip_id", "route_id"]].copy()
    quality_check = quality_check.copy()

    if quality_check.empty:
        return pd.DataFrame(
            columns=[
                "route_id",
                "avg_quality_score",
                "min_quality_score",
                "quality_issues_count",
            ]
        )

    quality_check["quality_score"] = to_numeric(quality_check["quality_score"])

    for col in ["has_missing_values", "has_time_error", "is_duplicate"]:
        if col in quality_check.columns:
            quality_check[col] = quality_check[col].astype(str).str.lower().isin(
                ["true", "1", "yes"]
            )

    quality_check["has_quality_issue"] = (
        quality_check.get("has_missing_values", False)
        | quality_check.get("has_time_error", False)
        | quality_check.get("is_duplicate", False)
    ).astype(int)

    quality_route = quality_check.merge(trip, on="trip_id", how="left")

    quality_agg = (
        quality_route.groupby("route_id")
        .agg(
            avg_quality_score=("quality_score", "mean"),
            min_quality_score=("quality_score", "min"),
            quality_issues_count=("has_quality_issue", "sum"),
        )
        .reset_index()
    )

    quality_agg["avg_quality_score"] = to_numeric(
        quality_agg["avg_quality_score"]
    ).round(2)

    return quality_agg


def add_environmental_features(dataset):
    dataset = dataset.copy()

    estimated_train_co2 = dataset["distance_km"] * DEFAULT_TRAIN_CO2_KG_PER_KM

    dataset["co2_train_kg"] = dataset["avg_existing_train_co2_kg"].fillna(
        estimated_train_co2
    )

    dataset["co2_plane_kg"] = dataset["distance_km"] * DEFAULT_PLANE_CO2_KG_PER_KM
    dataset["co2_saving_kg"] = dataset["co2_plane_kg"] - dataset["co2_train_kg"]

    dataset["co2_saving_percent"] = (
    dataset["co2_saving_kg"] / dataset["co2_plane_kg"].replace(0, pd.NA)
    ) * 100

    dataset["co2_saving_percent"] = dataset["co2_saving_percent"].fillna(0)

    for col in [
        "co2_train_kg",
        "co2_plane_kg",
        "co2_saving_kg",
        "co2_saving_percent",
    ]:
        dataset[col] = to_numeric(dataset[col]).round(2)

    return dataset


def compute_substitution_score(row):
    score = 0

    distance = row.get("distance_km")
    duration = row.get("avg_duration_minutes")
    frequency = row.get("weekly_frequency")
    quality = row.get("avg_quality_score")
    has_night_train = row.get("has_night_train", 0)
    co2_saving = row.get("co2_saving_kg")
    is_international = row.get("is_international", 0)

    if pd.isna(distance) or pd.isna(duration) or pd.isna(frequency):
        return 0

    if pd.isna(quality):
        quality = 50

    if pd.isna(co2_saving):
        co2_saving = 0

    # Distance : zone pertinente pour concurrence avec l'avion
    if 250 <= distance <= 900:
        score += 30
    elif 900 < distance <= 1500:
        score += 20
    elif 150 < distance < 250:
        score += 10
    elif distance > 1500 and has_night_train == 1:
        score += 10

    # Durée : compétitivité du train
    if duration <= 180:
        score += 25
    elif duration <= 300:
        score += 20
    elif duration <= 480:
        score += 12
    elif duration <= 720 and has_night_train == 1:
        score += 10

    # Fréquence : crédibilité de l'offre
    if frequency >= 20:
        score += 20
    elif frequency >= 10:
        score += 15
    elif frequency >= 3:
        score += 10
    elif frequency >= 1:
        score += 5

    # Train de nuit : avantage pour longues distances
    if has_night_train == 1 and distance >= 700:
        score += 10

    # Gain CO2
    if co2_saving >= 150:
        score += 15
    elif co2_saving >= 75:
        score += 10
    elif co2_saving > 0:
        score += 5

    # Qualité de données
    if quality >= 80:
        score += 10
    elif quality >= 60:
        score += 5
    elif quality < 50:
        score -= 20

    # Liaison internationale : intérêt stratégique européen
    if is_international == 1:
        score += 5

    return max(0, min(score, 100))


def create_target_from_score(score):
    if score >= 70:
        return "fort"
    if score >= 45:
        return "moyen"
    return "faible"


def build_dataset():
    MODELING_DIR.mkdir(parents=True, exist_ok=True)

    country = read_csv_table("country")
    city = read_csv_table("city")
    station = read_csv_table("station")
    operator = read_csv_table("operator")
    train_type = read_csv_table("train_type")
    route = read_csv_table("route")
    trip = read_csv_table("trip")
    trip_stop = read_csv_table("trip_stop")
    quality_check = read_csv_table("quality_check")

    station_dim = build_station_dimension(station, city, country)
    route_base = build_route_base(route, station_dim, operator)
    trip_agg = build_trip_aggregation(trip, train_type)
    stops_agg = build_stops_aggregation(trip, trip_stop)
    quality_agg = build_quality_aggregation(trip, quality_check)

    dataset = route_base.merge(trip_agg, on="route_id", how="left")
    dataset = dataset.merge(stops_agg, on="route_id", how="left")
    dataset = dataset.merge(quality_agg, on="route_id", how="left")

    dataset["avg_quality_score"] = dataset["avg_quality_score"].fillna(50)
    dataset["min_quality_score"] = dataset["min_quality_score"].fillna(50)
    dataset["quality_issues_count"] = dataset["quality_issues_count"].fillna(0)

    dataset = add_environmental_features(dataset)

    dataset["substitution_score"] = dataset.apply(compute_substitution_score, axis=1)
    dataset["substitution_potential"] = dataset["substitution_score"].apply(create_target_from_score)

    final_columns = [
        "route_id",
        "departure_station_id",
        "arrival_station_id",
        "departure_station_name",
        "arrival_station_name",
        "departure_city_name",
        "arrival_city_name",
        "departure_country_name",
        "arrival_country_name",
        "departure_country_code",
        "arrival_country_code",
        "operator_name",
        "is_international",
        "distance_km",
        "trip_count",
        "weekly_frequency",
        "daily_frequency_avg",
        "avg_duration_minutes",
        "min_duration_minutes",
        "max_duration_minutes",
        "main_train_type",
        "has_night_train",
        "has_day_train",
        "avg_num_stops",
        "min_num_stops",
        "max_num_stops",
        "avg_quality_score",
        "min_quality_score",
        "quality_issues_count",
        "co2_train_kg",
        "co2_plane_kg",
        "co2_saving_kg",
        "co2_saving_percent",
        "substitution_score",
        "substitution_potential",
    ]

    existing_columns = [col for col in final_columns if col in dataset.columns]
    dataset = dataset[existing_columns]

    critical_columns = [
        "route_id",
        "distance_km",
        "weekly_frequency",
        "avg_duration_minutes",
        "substitution_potential",
    ]

    before_drop = len(dataset)

    dataset = dataset.dropna(subset=critical_columns)

    # Suppression des lignes incohérentes pour le cas métier :
    # une liaison candidate à la substitution avion/train doit avoir
    # une distance, une durée et une fréquence strictement positives.
    dataset = dataset[dataset["distance_km"] > 0]
    dataset = dataset[dataset["avg_duration_minutes"] > 0]
    dataset = dataset[dataset["weekly_frequency"] > 0]


    after_drop = len(dataset)

    dataset.to_csv(OUTPUT_DATASET, index=False, encoding="utf-8")

    metadata = {
        "dataset_path": str(OUTPUT_DATASET),
        "rows_before_drop": int(before_drop),
        "rows_after_drop": int(after_drop),
        "removed_rows": int(before_drop - after_drop),
        "columns": list(dataset.columns),
        "target_column": "substitution_potential",
        "target_distribution": dataset["substitution_potential"]
        .value_counts()
        .to_dict(),
        "rules_summary": {
            "fort": [
                "250 <= distance_km <= 900, duration <= 300, weekly_frequency >= 10, quality >= 70",
                "ou 700 <= distance_km <= 1500 avec train de nuit, weekly_frequency >= 3, quality >= 70",
            ],
            "moyen": [
                "250 <= distance_km <= 1200, duration <= 480, weekly_frequency >= 3, quality >= 50"
            ],
            "faible": [
                "données critiques manquantes, qualité < 50, fréquence faible, durée trop longue ou distance peu adaptée"
            ],
        },
        "co2_assumptions": {
            "train_kg_per_km": DEFAULT_TRAIN_CO2_KG_PER_KM,
            "plane_kg_per_km": DEFAULT_PLANE_CO2_KG_PER_KM,
            "note": "Constantes provisoires utilisées pour la V1. À documenter ou remplacer par des facteurs officiels.",
        },
    }

    with open(OUTPUT_METADATA, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2, ensure_ascii=False)

    print("[OK] Dataset IA généré")
    print(f"Fichier : {OUTPUT_DATASET}")
    print(f"Lignes conservées : {after_drop}")
    print("Répartition de la cible :")
    print(dataset["substitution_potential"].value_counts())


if __name__ == "__main__":
    build_dataset()
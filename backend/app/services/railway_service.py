import json
from pathlib import Path


DATABASE_DIR = Path(__file__).resolve().parent.parent / "database"


def load_json(filename):
    path = DATABASE_DIR / filename

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_train(train_number):
    trains = load_json("trains.json")
    return trains.get(str(train_number))


def get_route(train_number):
    routes = load_json("routes.json")
    return routes.get(str(train_number), [])


def get_station(station_name):
    stations = load_json("stations.json")
    return stations.get(station_name)


def get_next_station(train_number, current_station):
    route = get_route(train_number)

    if not route:
        return None

    try:
        index = route.index(current_station)
    except ValueError:
        return None

    if index + 1 >= len(route):
        return None

    return route[index + 1]


def get_delay_history(train_number, station):
    history = load_json("delay_history.json")

    for record in history:
        if (
            record["train_number"] == str(train_number)
            and record["station"].lower() == station.lower()
        ):
            return record["delays"]

    return []
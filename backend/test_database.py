from app.services.railway_service import (
    get_train,
    get_route,
    get_next_station,
    get_station,
)


def main():
    train = get_train("12675")

    print("TRAIN:")
    print(train)

    route = get_route("12675")

    print("\nROUTE:")
    print(route)

    next_station = get_next_station(
        "12675",
        "Salem"
    )

    print("\nNEXT STATION:")
    print(next_station)

    station = get_station("Erode")

    print("\nSTATION:")
    print(station)


if __name__ == "__main__":
    main()
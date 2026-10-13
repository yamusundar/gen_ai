
import json
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.services.llm_service import ask_gemini
from app.services.railway_service import (
    get_train,
    get_route,
    get_station,
    get_next_station,
)

app = FastAPI(title="Train Information AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_PATH = Path(__file__).parent / "app" / "database" / "trains.json"

with open(DATABASE_PATH, "r", encoding="utf-8") as file:
    trains = json.load(file)


@app.get("/")
def home():
    return {
        "message": "Welcome to the Train Information AI!",
        "status": "Backend is working"
    }


@app.get("/train/{train_number}")
def get_train(train_number: str):
    train = trains.get(train_number)

    if train is None:
        return {
            "error": f"Train number {train_number} was not found."
        }

    return {
        "train_number": train_number,
        "train": train
    }


ROUTES_PATH = Path(__file__).parent / "app" / "database" / "routes.json"

with open(ROUTES_PATH, "r", encoding="utf-8") as file:
    routes = json.load(file)


@app.get("/route/{train_number}")
def get_route(train_number: str):
    route = routes.get(train_number)

    if route is None:
        return {
            "error": f"Route for train {train_number} was not found."
        }

    return {
        "train_number": train_number,
        "route": route
    }


@app.get("/next-station/{train_number}/{current_station}")
def get_next_station(train_number: str, current_station: str):
    route = routes.get(train_number)

    if route is None:
        return {"error": f"Train {train_number} was not found."}

    station_index = next(
        (
            i for i, station in enumerate(route)
            if station.lower() == current_station.lower()
        ),
        None
    )

    if station_index is None:
        return {"error": f"{current_station} is not on this route."}

    if station_index == len(route) - 1:
        return {"message": "This is the final station on the route."}

    return {
        "train_number": train_number,
        "current_station": route[station_index],
        "next_station": route[station_index + 1]
    }


STATIONS_PATH = Path(__file__).parent / "app" / "database" / "stations.json"

with open(STATIONS_PATH, "r", encoding="utf-8") as file:
    stations = json.load(file)


@app.get("/station/{station_code}")
def get_station(station_code: str):
    station = stations.get(station_code.upper())

    if station is None:
        station = stations.get(station_code.title())
    if station is None:
        return {"error": f"Station code {station_code} was not found."}

    return {
        "station_code": station_code.title(),
        "station": station
    }


@app.get("/ask")
def ask_question(question: str):
    question = re.sub(r"(?<=\d),(?=\d)", "", question)
    question_lower = question.lower()
    railway_data = None

    # 1. Handle next-station questions FIRST
    # This must come before station-name checks.
    if "next station" in question_lower:
        train_match = re.search(r"\b\d{5}\b", question)

        station_match = re.search(
            r"after\s+(.+?)(?=\s+for\s+train\b|\?|$)",
            question,
            re.IGNORECASE
        )

        if train_match and station_match:
            train_number = train_match.group()
            current_station = station_match.group(1).strip()

            next_station = get_next_station(
                train_number,
                current_station
            )

            if next_station is not None:
                railway_data = {
                    "train_number": train_number,
                    "current_station": current_station,
                    "next_station": next_station,
                }
            else:
                railway_data = {
                    "train_number": train_number,
                    "current_station": current_station,
                    "error": (
                        "Station not found on this route, "
                        "or this is the final station."
                    ),
                }
        else:
            railway_data = {
                "error": (
                    "Please include a five-digit train number "
                    "and a station, for example: "
                    "What is the next station after Salem "
                    "for train 12675?"
                )
            }

    # 2. Handle questions about Erode station
    elif "erode" in question_lower:
        station_info = get_station("Erode")

        railway_data = {
            "station": station_info
        }

    # 3. Detect a five-digit train number automatically
    else:
        train_match = re.search(r"\b\d{5}\b", question)

        if train_match:
            train_number = train_match.group()
            train_info = get_train(train_number)

            if train_info is not None:
                railway_data = {
                    "train": train_info,
                    "route": get_route(train_number),
                }
            else:
                railway_data = {
                    "error": (
                        f"Train number {train_number} "
                        "was not found in the sample database."
                    )
                }

    # 4. Ask Gemini to answer using the retrieved data
    prompt = f"""
    You are a helpful railway information assistant.

    Answer the user's question using the railway data below.
    Treat this data as the source of truth.
    If the data contains an error or says information is missing,
    explain that clearly. Do not invent train details, timings,
    platform numbers, or live delays.

    IMPORTANT LANGUAGE RULE:
    Answer in the same language as the user's question.
    If the question is in Tamil, answer entirely in Tamil.
    If the question is in Hindi, answer entirely in Hindi.
    If the question is in English, answer entirely in English.
    Do not switch languages unless the user requests it.
    Keep train numbers unchanged.
    Railway data:
    {json.dumps(railway_data, ensure_ascii=False, indent=2)}

    User question: {question}
    """

    answer = ask_gemini(prompt)

    # 5. Return the data and AI-generated answer
    return {
        "question": question,
        "railway_data": railway_data,
        "answer": answer
    }

import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash"
)


if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. "
        "Add it to backend/.env"
    )


client = genai.Client(
    api_key=API_KEY
)


def ask_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text.strip()
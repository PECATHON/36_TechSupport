import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

if os.environ.get("GEMINI_API_KEY") is None:
    print("GEMINI_API_KEY is missing")
    exit(1)

client = genai.Client()


def get_responses(path: Path):
    images = []
    for file in (path / "images").glob("*.png"):
        with open(file, "rb") as f:
            csv_bytes = f.read()
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=csv_bytes,
                        mime_type="image/png",
                    ),
                    "Give me a short description for the file",
                ],
            )

            images.append((file, response.text))

    csvs = []
    for file in (path / "tables").glob("*.csv"):
        with open(file, "rb") as f:
            csv_bytes = f.read()
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=csv_bytes,
                        mime_type="text/csv",
                    ),
                    "Give me a short description for the file. These are tables extracted from pdfs",
                ],
            )

            csvs.append((file, response.text))

    return csvs, images

if __name__ == "__main__":
    get_responses(Path("./output/DOC-5"))

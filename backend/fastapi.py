import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .app.images import main as get_files

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
PDF_MEDIA_TYPES = {
    "application/pdf",
    "application/x-pdf",
    "application/acrobat",
    "applications/vnd.pdf",
    "text/pdf",
    "text/x-pdf",
}


def is_pdf(upload: UploadFile) -> bool:
    return upload.content_type in PDF_MEDIA_TYPES or upload.filename.lower().endswith(  # pyright: ignore[reportOptionalMemberAccess]
        ".pdf"
    )


app.mount("/output", StaticFiles(directory="output"), name="output")


@app.post("/upload")
async def parse_files(file: UploadFile = File(...)):
    # Read the file bytes once
    Path("./uploads").mkdir(exist_ok=True)
    data = await file.read()
    out_path = Path(f"./uploads/{uuid.uuid4()}.pdf")

    # If it is already PDF → save directly
    if is_pdf(file):
        with open(out_path, "wb") as f:
            f.write(data)
    else:
        # Otherwise convert using Method 2 (Image → PDF)
        try:
            img = Image.open(BytesIO(data)).convert("RGB")
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="File is not a PDF and not a valid image for PDF conversion",
            )

        img.save(out_path, "PDF")

    csvs_results: list = []
    images_results: list = []

    csvs, images = get_files(out_path)

    for p in csvs:
        csv_path = p[0]
        png_path = p[1]

        if not csv_path.exists():
            csvs_results.append(("", "", f"Missing file: {p}"))
            continue

        # You generate or retrieve the description however you want
        description = p[2]

        csvs_results.append(
            (
                f"http://localhost:8000/output/{out_path.name.split('.')[0]}/tables/{str(csv_path.name)}",
                f"http://localhost:8000/output/{out_path.name.split('.')[0]}/tables/{str(png_path.name)}",
                description,
            )
        )

    for p in images:
        csv_path = p[0]
        png_path = p[1]

        if not csv_path.exists():
            images_results.append(("", "", f"Missing file: {p}"))
            continue

        # You generate or retrieve the description however you want
        description = p[2]

        images_results.append(
            (
                f"http://localhost:8000/output/{out_path.name.split('.')[0]}/tables/{str(csv_path.name)}",
                f"http://localhost:8000/output/{out_path.name.split('.')[0]}/tables/{str(png_path.name)}",
                description,
            )
        )

    return {"csvs": csvs_results, "images": images_results}

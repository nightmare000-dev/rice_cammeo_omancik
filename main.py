#!/usr/bin/env python3

from pathlib import Path
from tempfile import TemporaryDirectory
import csv

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from predict_agent import load_model, classify


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

# Подключаем CSS и JavaScript
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

# Загружаем модель
model = load_model(str(BASE_DIR / "rice_model.pkl"))


@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "index.html")


@app.post("/classify")
async def classify_file(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Пожалуйста, загрузите CSV-файл"
        )

    try:
        with TemporaryDirectory() as temp_dir:

            input_path = Path(temp_dir) / "input.csv"
            output_path = Path(temp_dir) / "results.csv"

            content = await file.read()
            input_path.write_bytes(content)

            classify(
                model,
                str(input_path),
                str(output_path)
            )

            with open(
                output_path,
                "r",
                encoding="utf-8"
            ) as result_file:

                reader = csv.DictReader(result_file)
                results = list(reader)

            return {
                "results": results,
                "count": len(results)
            }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
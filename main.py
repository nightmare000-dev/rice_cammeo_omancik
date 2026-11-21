from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import models.rizz_2 as rizz_2

app = FastAPI()

STATIC_DIR = Path(__file__).resolve().parent / 'static'
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

model = rizz_2.load_model('models\\bin\\rizz_2.pkl')

@app.get('/')
def root():
    return FileResponse(STATIC_DIR / 'index.html')

@app.post('/classify')
def classify(payload: dict = Body(...)):
    prediction, probability = rizz_2.classify(model, payload)
    return {'prediction': prediction, 'probability': probability}

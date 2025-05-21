from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes import rh, applicant
from app.routes import results 

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(rh.router, prefix="/rh")
app.include_router(applicant.router, prefix="/aspirante")
app.include_router(results.router, prefix="/rh/resultados")

@app.get("/")
def home():
    return {"message": "Sistema psicométrico activo"}

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from bson.objectid import ObjectId
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

client = MongoClient(os.getenv("MONGO_URI"))
db = client["rh"]
exams = db["exams"]
candidates = db["candidates"]

@router.get("/{token}", response_class=HTMLResponse)
async def mostrar_examenes(request: Request, token: str):
    aspirante = candidates.find_one({"token": token})
    if not aspirante:
        return HTMLResponse("<h1>Token no válido</h1>")
    lista = list(exams.find({"_id": {"$in": aspirante["examenes"]}}))
    return templates.TemplateResponse("exam.html", {"request": request, "aspirante": aspirante, "examenes": lista})

@router.post("/{token}")
async def guardar_respuestas(request: Request, token: str):
    form = await request.form()
    respuestas = {k: v for k, v in form.items()}
    candidates.update_one({"token": token}, {"$set": {"respuestas": respuestas}})
    return HTMLResponse("<h2>¡Gracias por completar tu evaluación!</h2>")
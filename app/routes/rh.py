from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from bson.objectid import ObjectId
from app.services import converter, emailer
import os
import uuid
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

client = MongoClient(os.getenv("MONGO_URI"))
db = client["rh"]
exams = db["exams"]
candidates = db["candidates"]

# ---------- PANEL RH ----------
@router.get("/", response_class=HTMLResponse)
async def rh_panel(request: Request):
    all_exams = list(exams.find())
    aspirantes = list(candidates.find())      # <-- lista de candidatos
    return templates.TemplateResponse(
        "panel.html",
        {
            "request": request,
            "exams": all_exams,
            "aspirantes": aspirantes         # <-- se envía a la plantilla
        }
    )

# ---------- SUBIR EXAMEN ----------
@router.post("/upload")
async def upload_exam(nombre: str = Form(...), archivo: UploadFile = File(...)):
    html_content = await converter.convert_docx_to_html(archivo)
    exams.insert_one({"nombre": nombre, "html": html_content})
    return RedirectResponse(url="/rh", status_code=303)

# ---------- ASIGNAR EXAMEN ----------
@router.post("/asignar")
async def asignar_examen(request: Request):
    form = await request.form()
    nombre = form.get("nombre")
    correo = form.get("correo")
    exam_ids = form.getlist("examenes")
    token = str(uuid.uuid4())

    candidates.insert_one(
        {
            "nombre": nombre,
            "correo": correo,
            "token": token,
            "examenes": [ObjectId(eid) for eid in exam_ids],
            "respuestas": {}
        }
    )

    enlace = f"{request.base_url}aspirante/{token}"
    emailer.enviar_enlace(correo, enlace)

    return RedirectResponse(url="/rh", status_code=303)

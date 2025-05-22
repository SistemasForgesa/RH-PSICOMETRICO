from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from bson.objectid import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv
from app.services import converter, emailer
import os, uuid

load_dotenv()

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

client = MongoClient(os.getenv("MONGO_URI"))
db = client["rh"]
exams = db["exams"]
candidates = db["candidates"]


# ─────────────────────────  HOME (landing)  ──────────────────────────
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    exams_count        = exams.count_documents({})
    aspirantes_count   = candidates.count_documents({})
    respondidos_count  = candidates.count_documents({"resultados": {"$exists": True, "$ne": {}}})

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "exams_count": exams_count,
            "aspirantes_count": aspirantes_count,
            "respondidos_count": respondidos_count,
        },
    )


# ─────────────────────────  SUBIR EXAMEN (página)  ────────────────────
@router.get("/subir", response_class=HTMLResponse)
async def subir_page(request: Request):
    return templates.TemplateResponse("subir.html", {"request": request})


@router.post("/upload")
async def upload_exam(nombre: str = Form(...), archivo: UploadFile = File(...)):
    html_content = await converter.convert_docx_to_html(archivo)
    exams.insert_one({"nombre": nombre, "html": html_content})
    return RedirectResponse(url="/rh/subir", status_code=303)


# ────────────────────────  ASIGNAR EXÁMENES (página)  ─────────────────
@router.get("/asignar", response_class=HTMLResponse)
async def asignar_page(request: Request):
    all_exams = list(exams.find())
    return templates.TemplateResponse(
        "asignar.html",
        {"request": request, "exams": all_exams},
    )


@router.post("/asignar")
async def asignar_examen(request: Request):
    form     = await request.form()
    nombre   = form.get("nombre")
    correo   = form.get("correo")
    exam_ids = form.getlist("examenes")
    token    = str(uuid.uuid4())

    candidates.insert_one(
        {
            "nombre": nombre,
            "correo": correo,
            "token": token,
            "examenes": [ObjectId(eid) for eid in exam_ids],
            "respuestas": {},
        }
    )

    enlace = f"{request.base_url}aspirante/{token}"
    emailer.enviar_enlace(correo, enlace)
    return RedirectResponse(url="/rh/asignar", status_code=303)


# ─────────────────────────  ASPIRANTES (página)  ──────────────────────
@router.get("/aspirantes", response_class=HTMLResponse)
async def aspirantes_page(request: Request):
    aspirantes = list(candidates.find())
    return templates.TemplateResponse(
        "aspirantes.html",
        {"request": request, "aspirantes": aspirantes},
    )


# ───────────────────────  PANEL COMPLETO (legacy)  ────────────────────
@router.get("/panel", response_class=HTMLResponse)
async def rh_panel(request: Request):
    all_exams   = list(exams.find())
    aspirantes  = list(candidates.find())
    return templates.TemplateResponse(
        "panel.html",
        {"request": request, "exams": all_exams, "aspirantes": aspirantes},
    )

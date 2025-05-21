from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
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
candidates = db["candidates"]

@router.get("/{cid}", response_class=HTMLResponse)
async def view_results(request: Request, cid: str):
    cand = candidates.find_one({"_id": ObjectId(cid)})
    if not cand or "resultados" not in cand:
        return HTMLResponse("<h2>No hay resultados registrados para este aspirante.</h2>")
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "c": cand,
            "resumen": cand["resultados"]
        }
    )

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.ai import generate_plan
from app.config import get_settings
from app.database import create_user, get_user, init_db, list_users, update_plan
from app.schemas import PlanRequest

logging.basicConfig(level=logging.INFO)
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="FitBuddy", description="Personalized fitness plans powered by Gemini", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/health")
async def health():
    return {"status": "ok", "ai_mode": "gemini" if get_settings().gemini_api_key else "demo"}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"error": None})


@app.post("/generate-workout", response_class=HTMLResponse)
async def generate_workout(request: Request,
    name: str = Form(...), age: int = Form(...), goal: str = Form(...), level: str = Form(...),
    days_per_week: int = Form(...), equipment: str = Form(...), constraints: str = Form("")):
    raw = {"name": name.strip(), "age": age, "goal": goal, "level": level,
           "days_per_week": days_per_week, "equipment": equipment.strip(), "constraints": constraints.strip()}
    try:
        profile = PlanRequest.model_validate(raw).model_dump()
        plan = await generate_plan(profile)
        user_id = create_user(profile, plan)
        return RedirectResponse(url=f"/plan/{user_id}", status_code=303)
    except Exception as exc:
        logging.exception("Plan generation failed")
        message = str(exc) if isinstance(exc, ValueError) else "We couldn't generate your plan right now. Check your settings or try again."
        return templates.TemplateResponse(request=request, name="index.html", context={"error": message, "values": raw}, status_code=400)


@app.get("/plan/{user_id}", response_class=HTMLResponse)
async def show_plan(request: Request, user_id: int):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Plan not found")
    return templates.TemplateResponse(request=request, name="result.html", context={"user": user, "error": None})


@app.post("/submit-feedback/{user_id}", response_class=HTMLResponse)
async def submit_feedback(request: Request, user_id: int, feedback: str = Form(...)):
    user = get_user(user_id)
    note = feedback.strip()
    if not user:
        raise HTTPException(status_code=404, detail="Plan not found")
    if not note or len(note) > 500:
        return templates.TemplateResponse(request=request, name="result.html",
            context={"user": user, "error": "Please enter feedback up to 500 characters."}, status_code=400)
    try:
        plan = await generate_plan(user, note)
        update_plan(user_id, plan, note)
        return RedirectResponse(url=f"/plan/{user_id}", status_code=303)
    except Exception:
        logging.exception("Feedback update failed")
        return templates.TemplateResponse(request=request, name="result.html",
            context={"user": user, "error": "We couldn't update your plan right now. Please try again."}, status_code=502)


@app.get("/view-all-users", response_class=HTMLResponse)
async def view_all_users(request: Request, token: str = ""):
    admin_token = get_settings().admin_token
    if admin_token and token != admin_token:
        raise HTTPException(status_code=403, detail="Admin token required")
    return templates.TemplateResponse(request=request, name="all_users.html", context={"users": list_users()})

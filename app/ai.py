import json
import logging
import re
from typing import Any
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)


def demo_plan(profile: dict[str, Any]) -> dict:
    goal = profile["goal"].lower()
    if "muscle" in goal:
        workouts = [("Strength A", "Goblet squat, push-ups, one-arm row, glute bridge"),
                    ("Strength B", "Romanian deadlift, overhead press, reverse lunge, plank"),
                    ("Strength C", "Split squat, incline push-up, row, hip hinge")]
    elif "endurance" in goal:
        workouts = [("Easy cardio", "Conversational-pace walk, jog, cycle, or swim"),
                    ("Intervals", "Warm up, then alternate brisk efforts with easy recovery"),
                    ("Long session", "Steady low-impact cardio at a comfortable pace")]
    else:
        workouts = [("Full-body A", "Chair squat, wall push-up, hip bridge, bird dog"),
                    ("Full-body B", "Step-back lunge, incline push-up, backpack row, dead bug"),
                    ("Mobility & cardio", "Brisk walk plus gentle hip, chest, and ankle mobility")]
    days = max(1, profile["days_per_week"])
    days_plan = []
    for i in range(days):
        if i < len(workouts):
            title, moves = workouts[i]
            days_plan.append({"day": f"Day {i + 1}", "focus": title,
                              "details": f"2–3 rounds at a comfortable effort. Exercises: {moves}. Rest 60–90 seconds as needed."})
        else:
            days_plan.append({"day": f"Day {i + 1}", "focus": "Recovery", "details": "Take an easy walk or rest. Keep movement gentle and pain-free."})
    return {"summary": f"A {days}-day beginner-friendly starting plan for {profile['goal'].lower()}.",
            "workouts": days_plan,
            "nutrition": ["Build meals around vegetables or fruit, a protein source, and satisfying high-fiber carbohydrates.",
                          "Drink water regularly; needs vary with activity and climate.",
                          "Choose a sustainable routine and avoid extreme restriction."],
            "safety": "Start gently, use equipment you know how to use, and stop if you feel sharp pain, dizziness, or unusual shortness of breath. Consider a clinician's advice before starting if you have a health condition or injury."}


async def generate_plan(profile: dict, feedback: str = "") -> dict:
    settings = get_settings()
    if not settings.gemini_api_key:
        return demo_plan(profile)
    prompt = f"""Create a safe, practical fitness plan as JSON only. Do not diagnose or prescribe treatment.
Return keys summary (string), workouts (array of {{day,focus,details}}), nutrition (array of strings), safety (string).
Avoid extreme diets, unsupported medical claims, and exercises requiring unavailable equipment. Give beginner-safe modifications.
Profile: {json.dumps(profile)}
User feedback to incorporate: {feedback or 'None'}"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(url, params={"key": settings.gemini_api_key},
                                     json={"contents": [{"parts": [{"text": prompt}]}],
                                           "generationConfig": {"responseMimeType": "application/json", "temperature": 0.6}})
        response.raise_for_status()
        payload = response.json()
    try:
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
        plan = json.loads(text)
        if not isinstance(plan.get("workouts"), list) or not isinstance(plan.get("nutrition"), list):
            raise ValueError("Unexpected plan structure")
        plan.setdefault("summary", "Your personalized fitness plan")
        plan.setdefault("safety", "Stop if you feel pain or unwell, and seek professional advice when appropriate.")
        return plan
    except (KeyError, IndexError, TypeError, json.JSONDecodeError, ValueError) as exc:
        logger.exception("Gemini returned an invalid plan")
        raise RuntimeError("The AI returned an unreadable plan. Please try again.") from exc

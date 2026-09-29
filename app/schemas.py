from typing import Literal
from pydantic import BaseModel, Field


Goal = Literal["Weight loss", "Muscle gain", "General wellness", "Improve endurance"]
Level = Literal["Beginner", "Intermediate", "Advanced"]


class PlanRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    age: int = Field(ge=16, le=100)
    goal: Goal
    level: Level
    days_per_week: int = Field(ge=1, le=7)
    equipment: str = Field(min_length=1, max_length=200)
    constraints: str = Field(default="", max_length=500)

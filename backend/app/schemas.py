from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PredictionRequest(BaseModel):
    team_a: str = Field(min_length=1, max_length=80)
    team_b: str = Field(min_length=1, max_length=80)

    @field_validator("team_a", "team_b")
    @classmethod
    def strip_team_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("O nome da seleção não pode ficar vazio.")
        return value


class ExpectedGoals(BaseModel):
    team_a: float
    team_b: float


class Probabilities(BaseModel):
    win_a: float
    draw: float
    win_b: float


class ScoreProbability(BaseModel):
    goals_a: int
    goals_b: int
    probability: float


class PredictionResponse(BaseModel):
    team_a: str
    team_b: str
    expected_goals: ExpectedGoals
    probabilities: Probabilities
    most_likely_score: ScoreProbability
    top_scores: list[ScoreProbability]
    warnings: list[str]
    model_mode: Literal["keras", "baseline"]
    model_version: str
    data_last_updated: str


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    model_mode: Literal["keras", "baseline"]
    model_version: str
    teams: int
    data_last_updated: str

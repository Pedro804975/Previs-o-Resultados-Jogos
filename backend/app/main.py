import os
from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .runtime import PredictionRuntime
from .schemas import HealthResponse, PredictionRequest, PredictionResponse


@lru_cache
def get_runtime() -> PredictionRuntime:
    return PredictionRuntime()


app = FastAPI(title="Previsão.lab API", version=os.getenv("API_VERSION", "1.0.0"))
origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    runtime = get_runtime()
    return HealthResponse(status="ok", model_mode=runtime.mode, model_version=runtime.version, teams=len(runtime.state.teams), data_last_updated=runtime.state.data_last_updated.isoformat())


@app.get("/model-info")
def model_info() -> dict[str, object]:
    runtime = get_runtime()
    return {"model_mode": runtime.mode, "model_version": runtime.version, "features": 11, "poisson_max_goals": 10, "data_last_updated": runtime.state.data_last_updated.isoformat()}


@app.get("/teams")
def teams() -> dict[str, object]:
    return {"teams": get_runtime().teams()}


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    try:
        return PredictionResponse(**get_runtime().predict(request.team_a, request.team_b))
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

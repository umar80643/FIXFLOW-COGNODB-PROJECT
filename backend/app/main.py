from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .models import DeviceDetail, GraphResponse, HealthResponse, RecommendationResponse, SearchResponse
from .repository import GraphRepository
from .service import FixFlowService

settings = get_settings()
repo = GraphRepository(settings)
service = FixFlowService(repo)

app = FastAPI(title="FixFlow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return service.health()


@app.get("/api/devices", response_model=SearchResponse)
def devices(search: str | None = None, category: str | None = None, limit: int = Query(default=12, ge=1, le=50)) -> SearchResponse:
    return service.search_devices(search, category, limit)


@app.get("/api/devices/{slug}", response_model=DeviceDetail)
def device_detail(slug: str) -> DeviceDetail:
    return service.device_detail(slug)


@app.get("/api/recommendations/{device_slug}/{symptom_slug}", response_model=RecommendationResponse)
def recommendations(device_slug: str, symptom_slug: str) -> RecommendationResponse:
    return service.recommendations(device_slug, symptom_slug)


@app.get("/api/related/{device_slug}", response_model=SearchResponse)
def related_devices(device_slug: str) -> SearchResponse:
    return service.related_devices(device_slug)


@app.get("/api/insights")
def insights():
    return {"insights": [insight.model_dump() for insight in service.insights()]}


@app.get("/api/graph/{device_slug}", response_model=GraphResponse)
def graph(device_slug: str) -> GraphResponse:
    detail = service.device_detail(device_slug)
    if not detail.symptoms:
        raise HTTPException(status_code=404, detail="Device not found")
    symptom = detail.symptoms[0]
    recommendation = service.recommendations(device_slug, symptom.slug)
    return recommendation.graph


@app.on_event("shutdown")
def shutdown() -> None:
    repo.close()

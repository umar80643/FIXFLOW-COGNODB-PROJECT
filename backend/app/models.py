from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    database_connected: bool
    message: str


class LabelRef(BaseModel):
    id: str
    name: str
    slug: str | None = None
    kind: str | None = None


class DeviceSummary(BaseModel):
    id: str
    slug: str
    name: str
    brand: str | None = None
    category: str | None = None
    popularity: int = 0
    difficulty: str = "medium"
    confidence: float = 0.0


class SymptomItem(BaseModel):
    id: str
    slug: str
    name: str
    severity: str
    frequency: int
    likely_fix_time: str


class GuideItem(BaseModel):
    id: str
    slug: str
    title: str
    summary: str
    difficulty: str
    estimated_minutes: int
    score: float


class PartItem(BaseModel):
    id: str
    name: str
    vendor: str
    price: float
    compatibility: int


class ToolItem(BaseModel):
    id: str
    name: str
    purpose: str


class VenueItem(BaseModel):
    id: str
    name: str
    city: str
    rating: float
    support_level: str


class DeviceDetail(BaseModel):
    device: DeviceSummary
    symptoms: list[SymptomItem] = Field(default_factory=list)
    guides: list[GuideItem] = Field(default_factory=list)
    parts: list[PartItem] = Field(default_factory=list)
    tools: list[ToolItem] = Field(default_factory=list)
    venues: list[VenueItem] = Field(default_factory=list)


class Insight(BaseModel):
    label: str
    value: str
    description: str


class GraphNode(BaseModel):
    id: str
    label: str
    kind: str
    x: float
    y: float
    group: str
    meta: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    kind: str


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class RecommendationResponse(BaseModel):
    device: DeviceSummary
    symptom: SymptomItem
    guides: list[GuideItem]
    parts: list[PartItem]
    tools: list[ToolItem]
    venues: list[VenueItem]
    graph: GraphResponse


class SearchResponse(BaseModel):
    query: str
    devices: list[DeviceSummary]

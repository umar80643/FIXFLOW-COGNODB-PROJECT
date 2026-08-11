from __future__ import annotations

from typing import Any

from .demo_data import DEMO_DEVICES, DEMO_DETAIL, DEMO_INSIGHTS
from .models import (
    DeviceDetail,
    DeviceSummary,
    GraphEdge,
    GraphNode,
    GraphResponse,
    HealthResponse,
    Insight,
    RecommendationResponse,
    SearchResponse,
    SymptomItem,
    GuideItem,
    PartItem,
    ToolItem,
    VenueItem,
)
from .queries import (
    DEVICE_DETAIL_QUERY,
    DEVICE_RECOMMENDATION_QUERY,
    DEVICE_SEARCH_QUERY,
    INSIGHTS_QUERY,
    RELATED_DEVICES_QUERY,
)
from .repository import GraphRepository

DIFFICULTY_RANK = {"easy": 0, "medium": 1, "hard": 2}


def _guide_sort_key(guide: GuideItem) -> tuple[int, int, float]:
    return (DIFFICULTY_RANK.get(guide.difficulty, 1), guide.estimated_minutes, -guide.score)


def _demo_device_models() -> list[DeviceSummary]:
    return [DeviceSummary(**item) for item in DEMO_DEVICES]


def _demo_insights() -> list[Insight]:
    return [Insight(**item) for item in DEMO_INSIGHTS]


class FixFlowService:
    def __init__(self, repo: GraphRepository):
        self.repo = repo

    def health(self) -> HealthResponse:
        result = self.repo.run("RETURN 1 AS ok")
        if result.connected:
            return HealthResponse(status="ok", database_connected=True, message="Connected to CognoDB")
        return HealthResponse(status="degraded", database_connected=False, message="Database unreachable, serving demo content")

    def search_devices(self, search: str | None, category: str | None, limit: int = 12) -> SearchResponse:
        result = self.repo.run(DEVICE_SEARCH_QUERY, {"search": search, "category": category, "limit": limit})
        if result.connected and result.records:
            devices: list[DeviceSummary] = []
            for row in result.records:
                d = row["d"]
                b = row.get("b")
                c = row.get("c")
                devices.append(
                    DeviceSummary(
                        id=d["id"],
                        slug=d["slug"],
                        name=d["name"],
                        brand=b["name"] if b else None,
                        category=c["name"] if c else None,
                        popularity=d.get("popularity", 0),
                        difficulty=d.get("difficulty", "medium"),
                        confidence=float(d.get("confidence", 0)),
                    )
                )
            return SearchResponse(query=search or "", devices=devices)
        fallback = _demo_device_models()
        if search:
            fallback = [d for d in fallback if search.lower() in d.name.lower() or search.lower() in d.slug.lower()]
        if category:
            fallback = [d for d in fallback if d.category and category.lower() == d.category.lower()]
        return SearchResponse(query=search or "", devices=fallback[:limit])

    def device_detail(self, slug: str) -> DeviceDetail:
        result = self.repo.run(DEVICE_DETAIL_QUERY, {"slug": slug})
        if result.connected and result.records:
            row = result.records[0]
            d = row["d"]
            b = row.get("b")
            c = row.get("c")
            symptoms = [
                SymptomItem(
                    id=s["id"],
                    slug=s["slug"],
                    name=s["name"],
                    severity=s.get("severity", "medium"),
                    frequency=s.get("frequency", 0),
                    likely_fix_time=s.get("likely_fix_time", "20 min"),
                )
                for s in row.get("symptoms", [])
            ]
            device = DeviceSummary(
                id=d["id"],
                slug=d["slug"],
                name=d["name"],
                brand=b["name"] if b else None,
                category=c["name"] if c else None,
                popularity=d.get("popularity", 0),
                difficulty=d.get("difficulty", "medium"),
                confidence=float(d.get("confidence", 0)),
            )
            recommendation = self.recommendations(slug, symptoms[0].slug) if symptoms else None
            guides = recommendation.guides if recommendation else []
            parts = recommendation.parts if recommendation else []
            tools = recommendation.tools if recommendation else []
            venues = recommendation.venues if recommendation else []
            return DeviceDetail(device=device, symptoms=symptoms, guides=guides, parts=parts, tools=tools, venues=venues)
        fallback = DEMO_DETAIL.get(slug) or next(iter(DEMO_DETAIL.values()))
        return DeviceDetail(
            device=DeviceSummary(**fallback["device"]),
            symptoms=[SymptomItem(**item) for item in fallback["symptoms"]],
            guides=[GuideItem(**item) for item in fallback["guides"]],
            parts=[PartItem(**item) for item in fallback["parts"]],
            tools=[ToolItem(**item) for item in fallback["tools"]],
            venues=[VenueItem(**item) for item in fallback["venues"]],
        )

    def insights(self) -> list[Insight]:
        result = self.repo.run(INSIGHTS_QUERY)
        if result.connected and result.records:
            row = result.records[0]
            return [
                Insight(label="Devices", value=str(row.get("device_count", 0)), description="Devices reachable from symptom chains"),
                Insight(label="Symptoms", value=str(row.get("symptom_count", 0)), description="Unique symptoms captured in the graph"),
                Insight(label="Guides", value=str(row.get("guide_count", 0)), description="Repair guides connected through causes"),
            ]
        return _demo_insights()

    def recommendations(self, device_slug: str, symptom_slug: str) -> RecommendationResponse:
        result = self.repo.run(DEVICE_RECOMMENDATION_QUERY, {"device_slug": device_slug, "symptom_slug": symptom_slug})
        if result.connected and result.records:
            row = result.records[0]
            d = row["d"]
            s = row["s"]
            guides = [g for g in row.get("guides", []) if isinstance(g, dict)]
            guides.sort(
                key=lambda g: (
                    DIFFICULTY_RANK.get(g.get("difficulty", "medium"), 1),
                    g.get("estimated_minutes", 30),
                    -float(g.get("score", 0.8)),
                )
            )
            graph = self._build_graph(d, s, guides, row.get("parts", []), row.get("tools", []), row.get("venues", []))
            return RecommendationResponse(
                device=DeviceSummary(
                    id=d["id"],
                    slug=d["slug"],
                    name=d["name"],
                    brand=None,
                    category=None,
                    popularity=d.get("popularity", 0),
                    difficulty=d.get("difficulty", "medium"),
                    confidence=float(d.get("confidence", 0)),
                ),
                symptom=SymptomItem(
                    id=s["id"],
                    slug=s["slug"],
                    name=s["name"],
                    severity=s.get("severity", "medium"),
                    frequency=s.get("frequency", 0),
                    likely_fix_time=s.get("likely_fix_time", "20 min"),
                ),
                guides=[
                    GuideItem(
                        id=g["id"],
                        slug=g["slug"],
                        title=g["title"],
                        summary=g.get("summary", ""),
                        difficulty=g.get("difficulty", "medium"),
                        estimated_minutes=g.get("estimated_minutes", 30),
                        score=float(g.get("score", 0.8)),
                    )
                    for g in guides
                ],
                parts=[PartItem(id=p["id"], name=p["name"], vendor=p.get("vendor", "OEM"), price=float(p.get("price", 0)), compatibility=int(p.get("compatibility", 0))) for p in row.get("parts", [])],
                tools=[ToolItem(id=t["id"], name=t["name"], purpose=t.get("purpose", "Repair task")) for t in row.get("tools", [])],
                venues=[VenueItem(id=v["id"], name=v["name"], city=v.get("city", ""), rating=float(v.get("rating", 0)), support_level=v.get("support_level", "Independent")) for v in row.get("venues", [])],
                graph=graph,
            )

        detail = DEMO_DETAIL.get(device_slug) or next(iter(DEMO_DETAIL.values()))
        symptom = detail["symptoms"][0]
        guides = sorted((GuideItem(**item) for item in detail["guides"]), key=_guide_sort_key)
        parts = [PartItem(**item) for item in detail["parts"]]
        tools = [ToolItem(**item) for item in detail["tools"]]
        venues = [VenueItem(**item) for item in detail["venues"]]
        graph = self._build_demo_graph(detail["device"], symptom, guides, parts, tools, venues)
        return RecommendationResponse(
            device=DeviceSummary(**detail["device"]),
            symptom=SymptomItem(**symptom),
            guides=guides,
            parts=parts,
            tools=tools,
            venues=venues,
            graph=graph,
        )

    def related_devices(self, device_slug: str) -> SearchResponse:
        result = self.repo.run(RELATED_DEVICES_QUERY, {"device_slug": device_slug})
        if result.connected and result.records:
            devices: list[DeviceSummary] = []
            for row in result.records:
                other = row["other"]
                brand = row.get("b")
                devices.append(
                    DeviceSummary(
                        id=other["id"],
                        slug=other["slug"],
                        name=other["name"],
                        brand=brand["name"] if brand else None,
                        category=None,
                        popularity=other.get("popularity", 0),
                        difficulty=other.get("difficulty", "medium"),
                        confidence=float(other.get("confidence", 0)),
                    )
                )
            return SearchResponse(query=device_slug, devices=devices)
        fallback = [device for device in _demo_device_models() if device.slug != device_slug]
        return SearchResponse(query=device_slug, devices=fallback[:6])

    def _build_demo_graph(
        self,
        device: dict[str, Any],
        symptom: dict[str, Any],
        guides: list[GuideItem],
        parts: list[PartItem],
        tools: list[ToolItem],
        venues: list[VenueItem],
    ) -> GraphResponse:
        nodes = [
            GraphNode(id=device["id"], label=device["name"], kind="Device", x=120, y=240, group="device", meta={"popularity": device.get("popularity", 0)}),
            GraphNode(id=symptom["id"], label=symptom["name"], kind="Symptom", x=310, y=140, group="symptom", meta={"severity": symptom["severity"]}),
        ]
        edges = [GraphEdge(id="edge-device-symptom", source=device["id"], target=symptom["id"], kind="HAS_SYMPTOM")]
        x_offset = 500
        for idx, guide in enumerate(guides):
            gid = guide.id
            nodes.append(GraphNode(id=gid, label=guide.title, kind="RepairGuide", x=x_offset + idx * 180, y=180 + (idx % 2) * 160, group="guide", meta={"difficulty": guide.difficulty}))
            edges.append(GraphEdge(id=f"edge-{symptom['id']}-{gid}", source=symptom["id"], target=gid, kind="RESOLVED_BY"))
        for idx, part in enumerate(parts):
            nodes.append(GraphNode(id=part.id, label=part.name, kind="Part", x=600 + idx * 180, y=390, group="part", meta={"vendor": part.vendor}))
        for idx, tool in enumerate(tools):
            nodes.append(GraphNode(id=tool.id, label=tool.name, kind="Tool", x=600 + idx * 180, y=40, group="tool", meta={"purpose": tool.purpose}))
        for idx, venue in enumerate(venues):
            nodes.append(GraphNode(id=venue.id, label=venue.name, kind="Venue", x=880 + idx * 170, y=240, group="venue", meta={"city": venue.city}))
        return GraphResponse(nodes=nodes, edges=edges)

    def _build_graph(self, device: dict[str, Any], symptom: dict[str, Any], guide_rows: list[dict[str, Any]], part_rows: list[dict[str, Any]], tool_rows: list[dict[str, Any]], venue_rows: list[dict[str, Any]]) -> GraphResponse:
        guides = [row for row in guide_rows if isinstance(row, dict)]
        parts = [row for row in part_rows if isinstance(row, dict)]
        tools = [row for row in tool_rows if isinstance(row, dict)]
        venues = [row for row in venue_rows if isinstance(row, dict)]
        nodes = [
            GraphNode(id=device["id"], label=device["name"], kind="Device", x=120, y=220, group="device", meta={"brand": device.get("brand")}),
            GraphNode(id=symptom["id"], label=symptom["name"], kind="Symptom", x=320, y=110, group="symptom", meta={"severity": symptom.get("severity")}),
        ]
        edges = [GraphEdge(id=f"edge-{device['id']}-{symptom['id']}", source=device["id"], target=symptom["id"], kind="HAS_SYMPTOM")]
        for idx, row in enumerate(guides):
            nodes.append(GraphNode(id=row["id"], label=row["title"], kind="RepairGuide", x=520 + idx * 180, y=180 + (idx % 2) * 130, group="guide", meta={"difficulty": row.get("difficulty")}))
            edges.append(GraphEdge(id=f"edge-{symptom['id']}-{row['id']}", source=symptom["id"], target=row["id"], kind="RESOLVED_BY"))
        for idx, row in enumerate(parts):
            nodes.append(GraphNode(id=row["id"], label=row["name"], kind="Part", x=620 + idx * 170, y=390, group="part", meta={"vendor": row.get("vendor")}))
        for idx, row in enumerate(tools):
            nodes.append(GraphNode(id=row["id"], label=row["name"], kind="Tool", x=620 + idx * 170, y=40, group="tool", meta={"purpose": row.get("purpose")}))
        for idx, row in enumerate(venues):
            nodes.append(GraphNode(id=row["id"], label=row["name"], kind="Venue", x=880 + idx * 170, y=240, group="venue", meta={"city": row.get("city")}))
        return GraphResponse(nodes=nodes, edges=edges)

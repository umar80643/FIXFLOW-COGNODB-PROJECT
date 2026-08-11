from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from neo4j import GraphDatabase


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


@dataclass
class SeedSettings:
    uri: str = os.getenv("COGNODB_URI", "bolt://localhost:7687")
    user: str = os.getenv("COGNODB_USER", "cognodb")
    password: str = os.getenv("COGNODB_PASSWORD", "change-me")
    database: str = os.getenv("COGNODB_DATABASE", "neo4j")


BRANDS = ["Apple", "Microsoft", "Nintendo", "Samsung", "Dell", "Lenovo", "Sony", "Asus"]
CATEGORIES = ["Phone", "Laptop", "Console", "Tablet"]
CITIES = [
    "Austin",
    "Dallas",
    "Seattle",
    "San Francisco",
    "New York",
    "Chicago",
    "Boston",
]
SYMPTOMS = [
    ("battery drains quickly", "high", 82, "20-40 min"),
    ("screen flickers", "medium", 57, "25-45 min"),
    ("won't charge", "high", 73, "30-60 min"),
    ("fan is noisy", "medium", 38, "15-35 min"),
    ("overheats under load", "high", 66, "20-50 min"),
    ("buttons feel sticky", "low", 24, "15-25 min"),
    ("wifi drops randomly", "medium", 44, "20-30 min"),
    ("speaker crackles", "medium", 31, "20-40 min"),
]
CAUSES = [
    "aging battery",
    "loose connector",
    "dust buildup",
    "damaged port",
    "thermal paste breakdown",
    "worn flex cable",
    "failing fan bearing",
    "corroded contact",
]
GUIDES = [
    ("Replace battery pack", "medium", 35, 0.94),
    ("Inspect charging port", "easy", 20, 0.83),
    ("Reseat internal flex cables", "medium", 28, 0.85),
    ("Clean fan and heatsink", "easy", 25, 0.78),
    ("Replace speaker module", "medium", 32, 0.81),
    ("Rebuild thermal stack", "hard", 55, 0.9),
]
TOOLS = [
    ("Pentalobe driver", "Open precision screws"),
    ("Spudger", "Disconnect delicate cables"),
    ("Heat mat", "Soften adhesive"),
    ("Tweezers", "Position tiny parts"),
    ("Compressed air", "Remove dust"),
    ("Torx set", "Open laptop and console frames"),
]
PARTS = [
    ("Battery pack", 59.0),
    ("Charging flex", 24.5),
    ("Fan assembly", 38.0),
    ("Speaker module", 18.0),
    ("Thermal pad kit", 14.5),
    ("Display cable", 19.0),
]
VENUE_TYPES = ["OEM", "Independent", "Mail-in", "Campus", "Retail"]


def slug(text: str) -> str:
    return (
        text.lower()
        .replace("&", " and ")
        .replace("'", "")
        .replace("/", "-")
        .replace(" ", "-")
        .replace("--", "-")
    )


def build_devices() -> list[dict[str, Any]]:
    devices: list[dict[str, Any]] = []
    counter = 1
    for category in CATEGORIES:
        for brand in BRANDS[:2]:
            for variant in range(1, 4):
                name = f"{brand} {category} {variant}"
                devices.append(
                    {
                        "id": f"device-{counter}",
                        "name": name,
                        "slug": slug(name),
                        "popularity": 55 + (counter * 3) % 45,
                        "difficulty": ["easy", "medium", "hard"][counter % 3],
                        "confidence": round(0.72 + ((counter % 13) / 100), 2),
                        "brand": brand,
                        "category": category,
                    }
                )
                counter += 1
    return devices


def build_related_records(devices: list[dict[str, Any]]):
    symptoms = [
        {"id": f"symptom-{idx+1}", "name": symptom[0], "slug": slug(symptom[0]), "severity": symptom[1], "frequency": symptom[2], "likely_fix_time": symptom[3]}
        for idx, symptom in enumerate(SYMPTOMS)
    ]
    causes = [{"id": f"cause-{idx+1}", "name": cause, "slug": slug(cause)} for idx, cause in enumerate(CAUSES)]
    guides = [
        {"id": f"guide-{idx+1}", "title": title, "slug": slug(title), "summary": f"Step-by-step {title.lower()} for repairability.", "difficulty": difficulty, "estimated_minutes": minutes, "score": score}
        for idx, (title, difficulty, minutes, score) in enumerate(GUIDES)
    ]
    parts = [
        {"id": f"part-{idx+1}", "name": name, "slug": slug(name), "vendor": vendor, "price": price}
        for idx, (name, price) in enumerate(PARTS)
        for vendor in ["OEM compatible" if idx % 2 == 0 else "Aftermarket"]
    ]
    tools = [{"id": f"tool-{idx+1}", "name": name, "slug": slug(name), "purpose": purpose} for idx, (name, purpose) in enumerate(TOOLS)]
    cities = [{"id": f"city-{idx+1}", "name": city, "slug": slug(city)} for idx, city in enumerate(CITIES)]
    venues = [
        {
            "id": f"venue-{idx+1}",
            "name": f"{city} Fix Center {idx+1}",
            "slug": slug(f"{city} Fix Center {idx+1}"),
            "rating": round(4.3 + ((idx % 6) * 0.1), 1),
            "support_level": VENUE_TYPES[idx % len(VENUE_TYPES)],
            "city": city,
        }
        for idx, city in enumerate(CITIES * 2)
    ]
    return symptoms, causes, guides, parts, tools, cities, venues


def main() -> None:
    settings = SeedSettings()
    devices = build_devices()
    symptoms, causes, guides, parts, tools, cities, venues = build_related_records(devices)

    driver = GraphDatabase.driver(
        settings.uri,
        auth=(settings.user, settings.password),
    )

    with driver.session(database=settings.database) as session:
        session.run("MATCH (n) DETACH DELETE n")

        session.run(
            """
            UNWIND $rows AS row
            MERGE (b:Brand {id: row.id})
            SET b.name = row.name
            """,
            {"rows": [{"id": f"brand-{slug(name)}", "name": name} for name in BRANDS]},
        )
        session.run(
            """
            UNWIND $rows AS row
            MERGE (c:Category {id: row.id})
            SET c.name = row.name
            """,
            {"rows": [{"id": f"category-{slug(name)}", "name": name} for name in CATEGORIES]},
        )
        session.run(
            """
            UNWIND $rows AS row
            MERGE (city:City {id: row.id})
            SET city.name = row.name, city.slug = row.slug
            """,
            {"rows": cities},
        )
        session.run(
            """
            UNWIND $rows AS row
            MERGE (s:Symptom {id: row.id})
            SET s.name = row.name, s.slug = row.slug, s.severity = row.severity, s.frequency = row.frequency, s.likely_fix_time = row.likely_fix_time
            """,
            {"rows": symptoms},
        )
        session.run(
            """
            UNWIND $rows AS row
            MERGE (c:Cause {id: row.id})
            SET c.name = row.name, c.slug = row.slug
            """,
            {"rows": causes},
        )
        session.run(
            """
            UNWIND $rows AS row
            MERGE (g:RepairGuide {id: row.id})
            SET g.title = row.title, g.slug = row.slug, g.summary = row.summary, g.difficulty = row.difficulty, g.estimated_minutes = row.estimated_minutes, g.score = row.score
            """,
            {"rows": guides},
        )
        session.run(
            """
            UNWIND $rows AS row
            MERGE (p:Part {id: row.id})
            SET p.name = row.name, p.slug = row.slug, p.vendor = row.vendor, p.price = row.price
            """,
            {"rows": parts},
        )
        session.run(
            """
            UNWIND $rows AS row
            MERGE (t:Tool {id: row.id})
            SET t.name = row.name, t.slug = row.slug, t.purpose = row.purpose
            """,
            {"rows": tools},
        )
        session.run(
            """
            UNWIND $rows AS row
            MERGE (v:RepairVenue {id: row.id})
            SET v.name = row.name, v.slug = row.slug, v.rating = row.rating, v.support_level = row.support_level
            """,
            {"rows": venues},
        )
        session.run(
            """
            UNWIND $rows AS row
            MERGE (d:Device {id: row.id})
            SET d.name = row.name, d.slug = row.slug, d.popularity = row.popularity, d.difficulty = row.difficulty, d.confidence = row.confidence
            WITH d, row
            MATCH (b:Brand {id: row.brand_id})
            MATCH (c:Category {id: row.category_id})
            MERGE (d)-[:BELONGS_TO]->(b)
            MERGE (d)-[:IN_CATEGORY]->(c)
            """,
            {
                "rows": [
                    {
                        **device,
                        "brand_id": f"brand-{slug(device['brand'])}",
                        "category_id": f"category-{slug(device['category'])}",
                    }
                    for device in devices
                ]
            },
        )

        for index, device in enumerate(devices):
            for offset in range(2):
                symptom = symptoms[(index + offset) % len(symptoms)]
                cause = causes[(index + offset) % len(causes)]
                guide = guides[(index + offset) % len(guides)]
                part = parts[(index + offset) % len(parts)]
                tool = tools[(index + offset) % len(tools)]
                venue = venues[(index + offset) % len(venues)]
                city = cities[(index + offset) % len(cities)]

                session.run(
                    """
                    MATCH (d:Device {id: $device_id})
                    MATCH (s:Symptom {id: $symptom_id})
                    MATCH (c:Cause {id: $cause_id})
                    MATCH (g:RepairGuide {id: $guide_id})
                    MATCH (p:Part {id: $part_id})
                    MATCH (t:Tool {id: $tool_id})
                    MATCH (v:RepairVenue {id: $venue_id})
                    MATCH (city:City {id: $city_id})
                    MERGE (d)-[:HAS_SYMPTOM]->(s)
                    MERGE (s)-[:INDICATES]->(c)
                    MERGE (c)-[:RESOLVED_BY]->(g)
                    MERGE (g)-[:USES_PART]->(p)
                    MERGE (g)-[:USES_TOOL]->(t)
                    MERGE (g)-[:SUPPORTED_BY]->(v)
                    MERGE (v)-[:LOCATED_IN]->(city)
                    MERGE (p)-[:COMPATIBLE_WITH]->(d)
                    """,
                    {
                        "device_id": device["id"],
                        "symptom_id": symptom["id"],
                        "cause_id": cause["id"],
                        "guide_id": guide["id"],
                        "part_id": part["id"],
                        "tool_id": tool["id"],
                        "venue_id": venue["id"],
                        "city_id": city["id"],
                    },
                )

        driver.close()

    print(f"Seeded {len(devices)} devices, {len(symptoms)} symptoms, {len(guides)} guides, and supporting graph data.")


if __name__ == "__main__":
    main()

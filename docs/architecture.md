# FixFlow architecture

FixFlow is intentionally split into two layers:

1. a graph API that knows how to read repair knowledge from CognoDB
2. a frontend that turns the graph into a usable repair workflow

## Backend responsibilities

- own the Neo4j/CognoDB connection
- expose parameterized read endpoints
- normalize graph records into JSON
- fall back to demo content when the database is unreachable

## Frontend responsibilities

- search and browse devices
- surface the strongest repair path for a selected symptom
- show parts, tools, and venues in a way that feels human, not academic
- keep loading and error states obvious

## Data contracts

The backend returns compact JSON shapes:

- `DeviceSummary`
- `DeviceDetail`
- `Recommendation`
- `Insight`
- `GraphNode` and `GraphEdge`

The frontend treats those as presentation-ready objects and does not need to know the Cypher structure.

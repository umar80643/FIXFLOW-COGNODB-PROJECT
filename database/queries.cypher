// 1. Browse devices with category and brand filters.
MATCH (d:Device)
OPTIONAL MATCH (d)-[:BELONGS_TO]->(b:Brand)
OPTIONAL MATCH (d)-[:IN_CATEGORY]->(c:Category)
WHERE ($search IS NULL OR toLower(d.name) CONTAINS toLower($search))
  AND ($category IS NULL OR toLower(c.name) = toLower($category))
RETURN d, b, c
ORDER BY d.popularity DESC, d.name ASC
LIMIT $limit;

// 2. Look up one device by slug.
MATCH (d:Device {slug: $slug})
OPTIONAL MATCH (d)-[:BELONGS_TO]->(b:Brand)
OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
OPTIONAL MATCH (d)-[:IN_CATEGORY]->(c:Category)
RETURN d, b, c, collect(DISTINCT s) AS symptoms;

// 3. Multi-hop recommendation path.
// Note: guides are sorted application-side after collect(), not here --
// `g` falls out of scope once aggregated, so `ORDER BY g.difficulty` would
// raise a CypherSyntaxError (and get masked as "database unreachable" by
// the backend's error handling).
MATCH path = (d:Device {slug: $device_slug})-[:HAS_SYMPTOM]->(s:Symptom)-[:INDICATES]->(cause:Cause)-[:RESOLVED_BY]->(g:RepairGuide)
OPTIONAL MATCH (g)-[:USES_PART]->(p:Part)
OPTIONAL MATCH (g)-[:USES_TOOL]->(t:Tool)
RETURN d, s, cause, collect(DISTINCT g) AS guides, collect(DISTINCT p) AS parts, collect(DISTINCT t) AS tools, path;

// 4. Related devices through shared symptoms and guides.
MATCH (d:Device {slug: $device_slug})-[:HAS_SYMPTOM]->(:Symptom)<-[:HAS_SYMPTOM]-(other:Device)
OPTIONAL MATCH (other)-[:BELONGS_TO]->(b:Brand)
RETURN other, b, count(*) AS signal
ORDER BY signal DESC, other.popularity DESC
LIMIT 12;

// 5. Nearby venues for a guide.
MATCH (g:RepairGuide {slug: $guide_slug})-[:SUPPORTED_BY]->(v:RepairVenue)-[:LOCATED_IN]->(c:City)
RETURN g, v, c
ORDER BY v.rating DESC, v.name ASC;

// 6. A query that is awkward in a relational model.
// Find device families where a symptom, guide, part, and venue all connect within three hops.
MATCH (d:Device)-[:HAS_SYMPTOM]->(s:Symptom)-[:INDICATES]->(:Cause)-[:RESOLVED_BY]->(g:RepairGuide)-[:USES_PART]->(p:Part)
MATCH (g)-[:SUPPORTED_BY]->(v:RepairVenue)
OPTIONAL MATCH (d)-[:BELONGS_TO]->(b:Brand)
RETURN d, s, g, p, v, b
ORDER BY d.popularity DESC, v.rating DESC;

DEVICE_SEARCH_QUERY = """
MATCH (d:Device)
OPTIONAL MATCH (d)-[:BELONGS_TO]->(b:Brand)
OPTIONAL MATCH (d)-[:IN_CATEGORY]->(c:Category)
WHERE ($search IS NULL OR toLower(d.name) CONTAINS toLower($search) OR toLower(d.slug) CONTAINS toLower($search))
  AND ($category IS NULL OR toLower(c.name) = toLower($category))
RETURN d, b, c
ORDER BY d.popularity DESC, d.name ASC
LIMIT $limit
"""

DEVICE_DETAIL_QUERY = """
MATCH (d:Device {slug: $slug})
OPTIONAL MATCH (d)-[:BELONGS_TO]->(b:Brand)
OPTIONAL MATCH (d)-[:IN_CATEGORY]->(c:Category)
OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
RETURN d, b, c, collect(DISTINCT s) AS symptoms
"""

DEVICE_RECOMMENDATION_QUERY = """
MATCH (d:Device {slug: $device_slug})-[:HAS_SYMPTOM]->(s:Symptom {slug: $symptom_slug})
MATCH (s)-[:INDICATES]->(cause:Cause)-[:RESOLVED_BY]->(g:RepairGuide)
OPTIONAL MATCH (g)-[:USES_PART]->(p:Part)
OPTIONAL MATCH (g)-[:USES_TOOL]->(t:Tool)
OPTIONAL MATCH (g)-[:SUPPORTED_BY]->(v:RepairVenue)-[:LOCATED_IN]->(city:City)
RETURN d, s, cause,
       collect(DISTINCT g) AS guides,
       collect(DISTINCT p) AS parts,
       collect(DISTINCT t) AS tools,
       collect(DISTINCT v) AS venues,
       collect(DISTINCT city) AS cities
"""
# Note: guides are sorted in Python (see service.py) rather than in Cypher.
# `g` is consumed by collect(DISTINCT g) above, so it falls out of scope for
# ORDER BY -- referencing g.difficulty here raises a CypherSyntaxError, which
# GraphRepository.run() silently swallows as "database unreachable" and masks
# the real error. Keep sorting out of this query.

RELATED_DEVICES_QUERY = """
MATCH (d:Device {slug: $device_slug})-[:HAS_SYMPTOM]->(:Symptom)<-[:HAS_SYMPTOM]-(other:Device)
OPTIONAL MATCH (other)-[:BELONGS_TO]->(b:Brand)
RETURN other, b, count(*) AS signal
ORDER BY signal DESC, other.popularity DESC
LIMIT 12
"""

INSIGHTS_QUERY = """
MATCH (d:Device)-[:HAS_SYMPTOM]->(s:Symptom)-[:INDICATES]->(:Cause)-[:RESOLVED_BY]->(g:RepairGuide)
RETURN count(DISTINCT d) AS device_count,
       count(DISTINCT s) AS symptom_count,
       count(DISTINCT g) AS guide_count
"""

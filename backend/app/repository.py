from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from .config import Settings


@dataclass
class RepositoryResult:
    records: list[dict[str, Any]]
    connected: bool


class GraphRepository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._driver = None

    def _connect(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.settings.cognodb_uri,
                auth=(self.settings.cognodb_user, self.settings.cognodb_password),
            )
        return self._driver

    def run(self, query: str, params: dict[str, Any] | None = None) -> RepositoryResult:
        params = params or {}
        try:
            driver = self._connect()
            with driver.session(database=self.settings.cognodb_database) as session:
                result = session.run(query, params)
                return RepositoryResult(records=[record.data() for record in result], connected=True)
        except (ServiceUnavailable, Neo4jError, OSError):
            return RepositoryResult(records=[], connected=False)

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None

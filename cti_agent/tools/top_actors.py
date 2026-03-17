from __future__ import annotations

import os
from dataclasses import dataclass

from cti_agent.telemetry import timed_tool_call


class TopActorsClient:
    def get_top_actors(self, *, limit: int) -> str:  # pragma: no cover
        raise NotImplementedError


@dataclass(frozen=True)
class SqlTopActorsClient(TopActorsClient):
    """
    Placeholder top-actors client.

    Real implementation would execute SQL_TOP_ACTORS_QUERY against SQL_URL and return a compact
    list for the LLM (names + priority/tags).
    """

    enabled: bool
    query: str

    @classmethod
    def from_env(cls) -> "SqlTopActorsClient":
        sql_url = os.getenv("SQL_URL", "").strip()
        query = os.getenv(
            "SQL_TOP_ACTORS_QUERY",
            "SELECT name, priority FROM top_actors ORDER BY priority ASC LIMIT 20;",
        )
        return cls(enabled=bool(sql_url), query=query)

    def get_top_actors(self, *, limit: int) -> str:
        if not self.enabled:
            return "(top actors disabled: SQL_URL not set)"
        with timed_tool_call(
            "top_actors.sql.query",
            input_summary=f"limit={limit}",
        ) as meta:
            out = f"(top actors enabled: would run query '{self.query}' with limit {limit})"
            meta["output_summary"] = "template_response"
            return out


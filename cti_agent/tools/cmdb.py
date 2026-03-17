from __future__ import annotations

import os
from dataclasses import dataclass

from cti_agent.telemetry import timed_tool_call


class CmdbClient:
    def get_high_value_assets_summary(self, *, limit: int) -> str:  # pragma: no cover
        raise NotImplementedError


@dataclass(frozen=True)
class OpenSearchCmdbClient(CmdbClient):
    """
    Placeholder CMDB client.

    In a real implementation, this would query OpenSearch with auth and return a compact summary
    of the most critical assets (e.g., internet-exposed, tier-0, crown jewels, etc.).
    """

    enabled: bool
    index: str

    @classmethod
    def from_env(cls) -> "OpenSearchCmdbClient":
        url = os.getenv("OPENSEARCH_URL", "").strip()
        index = os.getenv("OPENSEARCH_CMDB_INDEX", "cmdb-assets")
        return cls(enabled=bool(url), index=index)

    def get_high_value_assets_summary(self, *, limit: int) -> str:
        if not self.enabled:
            return "(cmdb disabled: OPENSEARCH_URL not set)"
        with timed_tool_call(
            "cmdb.opensearch.summary",
            input_summary=f"index={self.index}, limit={limit}",
        ) as meta:
            out = f"(cmdb enabled: would query index '{self.index}' for top {limit} assets)"
            meta["output_summary"] = "template_response"
            return out


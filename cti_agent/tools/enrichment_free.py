from __future__ import annotations

import os
from dataclasses import dataclass

from cti_agent.tools.enrichment import EnrichmentClient


@dataclass(frozen=True)
class OtxClient(EnrichmentClient):
    name: str = "otx"
    enabled: bool = False

    @classmethod
    def from_env(cls) -> "OtxClient":
        return cls(enabled=bool(os.getenv("OTX_API_KEY", "").strip()))

    def enrich(self, *, ioc_type: str, value: str) -> dict[str, object]:
        return {"note": "TODO: call OTX API", "ioc_type": ioc_type, "value": value}


@dataclass(frozen=True)
class ThreatFoxClient(EnrichmentClient):
    name: str = "threatfox"
    enabled: bool = True  # often usable without key, keep as enabled by default

    @classmethod
    def from_env(cls) -> "ThreatFoxClient":
        return cls(enabled=True)

    def enrich(self, *, ioc_type: str, value: str) -> dict[str, object]:
        return {"note": "TODO: call ThreatFox API", "ioc_type": ioc_type, "value": value}


@dataclass(frozen=True)
class MalwareBazaarClient(EnrichmentClient):
    name: str = "malwarebazaar"
    enabled: bool = True

    @classmethod
    def from_env(cls) -> "MalwareBazaarClient":
        return cls(enabled=True)

    def enrich(self, *, ioc_type: str, value: str) -> dict[str, object]:
        if ioc_type != "hash":
            return {"skipped": True, "reason": "hash only"}
        return {"note": "TODO: call MalwareBazaar API", "hash": value}


@dataclass(frozen=True)
class UrlHausClient(EnrichmentClient):
    name: str = "urlhaus"
    enabled: bool = True

    @classmethod
    def from_env(cls) -> "UrlHausClient":
        return cls(enabled=True)

    def enrich(self, *, ioc_type: str, value: str) -> dict[str, object]:
        if ioc_type not in {"url", "domain"}:
            return {"skipped": True, "reason": "url/domain only"}
        return {"note": "TODO: call URLhaus API", "ioc_type": ioc_type, "value": value}


@dataclass(frozen=True)
class UrlscanClient(EnrichmentClient):
    name: str = "urlscan"
    enabled: bool = False

    @classmethod
    def from_env(cls) -> "UrlscanClient":
        return cls(enabled=bool(os.getenv("URLSCAN_API_KEY", "").strip()))

    def enrich(self, *, ioc_type: str, value: str) -> dict[str, object]:
        if ioc_type not in {"url", "domain", "ip"}:
            return {"skipped": True, "reason": "url/domain/ip only"}
        return {"note": "TODO: call urlscan.io API", "ioc_type": ioc_type, "value": value}


from __future__ import annotations

import os
from dataclasses import dataclass

from cti_agent.tools.enrichment import EnrichmentClient


@dataclass(frozen=True)
class RecordedFutureClient(EnrichmentClient):
    name: str = "recordedfuture"
    enabled: bool = False

    @classmethod
    def from_env(cls) -> "RecordedFutureClient":
        return cls(enabled=bool(os.getenv("RECORDEDFUTURE_API_KEY", "").strip()))

    def enrich(self, *, ioc_type: str, value: str) -> dict[str, object]:
        return {"note": "TODO: call Recorded Future API", "ioc_type": ioc_type, "value": value}


@dataclass(frozen=True)
class DomainToolsClient(EnrichmentClient):
    name: str = "domaintools"
    enabled: bool = False

    @classmethod
    def from_env(cls) -> "DomainToolsClient":
        return cls(enabled=bool(os.getenv("DOMAINTOOLS_API_KEY", "").strip()))

    def enrich(self, *, ioc_type: str, value: str) -> dict[str, object]:
        if ioc_type not in {"domain", "ip"}:
            return {"skipped": True, "reason": "domain/ip only"}
        return {"note": "TODO: call DomainTools API", "ioc_type": ioc_type, "value": value}


@dataclass(frozen=True)
class VirusTotalClient(EnrichmentClient):
    name: str = "virustotal"
    enabled: bool = False

    @classmethod
    def from_env(cls) -> "VirusTotalClient":
        return cls(enabled=bool(os.getenv("VIRUSTOTAL_API_KEY", "").strip()))

    def enrich(self, *, ioc_type: str, value: str) -> dict[str, object]:
        return {"note": "TODO: call VirusTotal API", "ioc_type": ioc_type, "value": value}


@dataclass(frozen=True)
class GreyNoiseClient(EnrichmentClient):
    name: str = "greynoise"
    enabled: bool = False

    @classmethod
    def from_env(cls) -> "GreyNoiseClient":
        return cls(enabled=bool(os.getenv("GREYNOISE_API_KEY", "").strip()))

    def enrich(self, *, ioc_type: str, value: str) -> dict[str, object]:
        if ioc_type != "ip":
            return {"skipped": True, "reason": "ip only"}
        return {"note": "TODO: call GreyNoise API", "ip": value}


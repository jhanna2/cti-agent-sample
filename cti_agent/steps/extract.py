from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExtractionResult:
    threat_actors: list[str] = field(default_factory=list)
    campaigns: list[str] = field(default_factory=list)
    malware: list[str] = field(default_factory=list)
    iocs: dict[str, list[str]] = field(default_factory=dict)


_RE_IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_RE_DOMAIN = re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b")
_RE_URL = re.compile(r"\bhttps?://[^\s)>\"]+\b")
_RE_SHA256 = re.compile(r"\b[a-fA-F0-9]{64}\b")
_RE_MD5 = re.compile(r"\b[a-fA-F0-9]{32}\b")


def extract_entities_and_iocs(text: str) -> ExtractionResult:
    """
    Part 3 (first half): Extract entities + IOCs.

    This is a regex-based starter. In real deployments, combine:
    - structured parsing for vendor advisories
    - LLM-assisted extraction with validation
    - allow/deny lists and normalization
    """
    ips = sorted(set(_RE_IP.findall(text)))
    urls = sorted(set(_RE_URL.findall(text)))
    hashes = sorted(set(_RE_SHA256.findall(text) + _RE_MD5.findall(text)))
    domains = sorted(set(_RE_DOMAIN.findall(text)))

    iocs = {
        "ip": ips,
        "url": urls,
        "domain": domains,
        "hash": hashes,
    }
    return ExtractionResult(iocs=iocs)


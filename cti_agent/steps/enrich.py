from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from cti_agent.fact_cards import FactCard
from cti_agent.tools.enrichment import EnrichmentClient, MultiEnrichmentClient
from cti_agent.tools.enrichment_free import (
    MalwareBazaarClient,
    OtxClient,
    ThreatFoxClient,
    UrlHausClient,
    UrlscanClient,
)
from cti_agent.tools.enrichment_paid import (
    DomainToolsClient,
    GreyNoiseClient,
    RecordedFutureClient,
    VirusTotalClient,
)


@dataclass(frozen=True)
class EnrichmentResult:
    notes: str
    enriched_iocs: dict[str, dict[str, object]]


def enrich_entities_and_iocs(
    *,
    fact_cards: list[FactCard],
    out_dir: Path,
    cache_ttl_hint: str = "template",
) -> EnrichmentResult:
    """
    Part 3 (second half): Tool-based enrichment loop.

    This template wires multiple enrichment sources behind a single interface, with graceful
    degradation when API keys are missing.
    """
    clients: list[EnrichmentClient] = [
        # Free sources (optional)
        OtxClient.from_env(),
        ThreatFoxClient.from_env(),
        MalwareBazaarClient.from_env(),
        UrlHausClient.from_env(),
        UrlscanClient.from_env(),
        # Paid sources (optional placeholders)
        RecordedFutureClient.from_env(),
        DomainToolsClient.from_env(),
        VirusTotalClient.from_env(),
        GreyNoiseClient.from_env(),
    ]
    multi = MultiEnrichmentClient([c for c in clients if c.enabled])

    cache_dir = out_dir / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "enrichment_cache.json"

    cache: dict[str, dict[str, object]] = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            cache = {}

    # Only enrich IOCs from selected fact cards (already gated upstream).
    to_enrich: dict[str, set[str]] = {}
    for c in fact_cards:
        for ioc_type, values in (c.iocs or {}).items():
            for v in values:
                to_enrich.setdefault(ioc_type, set()).add(v)

    enriched: dict[str, dict[str, object]] = {}
    for ioc_type, values in to_enrich.items():
        for v in sorted(values):
            cached = (cache.get(ioc_type) or {}).get(v)
            if cached is not None:
                enriched.setdefault(ioc_type, {})[v] = cached
                continue
            out = multi.enrich(ioc_type=ioc_type, value=v)
            enriched.setdefault(ioc_type, {})[v] = out
            cache.setdefault(ioc_type, {})[v] = out

    # Best-effort cache write
    try:
        cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except Exception:
        pass

    return EnrichmentResult(
        notes=f"Enrichment complete (sources enabled based on available API keys). cache={cache_ttl_hint}",
        enriched_iocs=enriched,
    )


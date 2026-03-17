from __future__ import annotations

from dataclasses import dataclass

from cti_agent.steps.extract import ExtractionResult
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


def enrich_entities_and_iocs(extracted: ExtractionResult) -> EnrichmentResult:
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

    enriched: dict[str, dict[str, object]] = {}
    for ioc_type, values in extracted.iocs.items():
        for v in values:
            enriched.setdefault(ioc_type, {})[v] = multi.enrich(ioc_type=ioc_type, value=v)

    return EnrichmentResult(
        notes="Enrichment complete (sources enabled based on available API keys).",
        enriched_iocs=enriched,
    )


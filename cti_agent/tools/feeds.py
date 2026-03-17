from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import httpx

from cti_agent.steps.fetch import _normalize_whitespace
from cti_agent.models import Bulletin


@dataclass(frozen=True)
class ThreatFeed:
    """
    Simple description of a free CTI feed we can pull from.

    These are intentionally generic and do not assume a specific schema – the goal is to
    download bulletins / advisories that can then be normalized and passed into the pipeline.
    """

    name: str
    url: str
    description: str


def get_default_free_feeds() -> list[ThreatFeed]:
    """
    A non-exhaustive set of free threat intel sources with HTTP/JSON/RSS endpoints.

    Each of these can be turned into a richer connector later.
    """
    return [
        ThreatFeed(
            name="cisa_kev",
            url="https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
            description="CISA Known Exploited Vulnerabilities (KEV) catalog (JSON).",
        ),
        ThreatFeed(
            name="cisa_ics_advisories",
            url="https://www.cisa.gov/sites/default/files/feeds/ics-advisories.xml",
            description="CISA ICS advisories (XML/RSS-style).",
        ),
        ThreatFeed(
            name="abusech_threatfox",
            url="https://threatfox-api.abuse.ch/api/v1/",
            description="abuse.ch ThreatFox indicator API (POST JSON).",
        ),
        ThreatFeed(
            name="abusech_urlhaus",
            url="https://urlhaus-api.abuse.ch/v1/",
            description="abuse.ch URLhaus malicious URL API (POST JSON).",
        ),
        ThreatFeed(
            name="abusech_malwarebazaar",
            url="https://mb-api.abuse.ch/api/v1/",
            description="abuse.ch MalwareBazaar malware sample/hash API (POST JSON).",
        ),
        ThreatFeed(
            name="otx_pulses",
            url="https://otx.alienvault.com/api/v1/pulses/subscribed",
            description="AlienVault OTX subscribed pulses (requires OTX_API_KEY).",
        ),
        ThreatFeed(
            name="urlscan",
            url="https://urlscan.io/api/v1/search/",
            description="urlscan.io search API for URLs/domains (requires URLSCAN_API_KEY).",
        ),
    ]


def fetch_feed_bodies(feeds: Iterable[ThreatFeed]) -> list[str]:
    """
    Download raw feed bodies as text.

    This is deliberately minimal: no pagination, cursors, or body shaping – the goal is to
    demonstrate where API calls for free feeds would live in this template.
    """
    client = httpx.Client(timeout=30.0)
    bodies: list[str] = []
    for feed in feeds:
        try:
            resp = client.get(feed.url)
            resp.raise_for_status()
            bodies.append(f"# {feed.name}\n\n{resp.text}")
        except Exception as exc:  # pragma: no cover - template robustness
            bodies.append(f"# {feed.name} (error)\n\n{exc}")
    return [_normalize_whitespace(b) for b in bodies]


def fetch_bulletins(feeds: Iterable[ThreatFeed]) -> list[Bulletin]:
    """
    Fetch feeds and return them as Bulletins with basic metadata.

    Title is set to the feed name for now; later you can parse per-item titles from RSS/JSON.
    """
    feeds_list = list(feeds)
    bodies = fetch_feed_bodies(feeds_list)
    bulletins: list[Bulletin] = []
    for feed, body in zip(feeds_list, bodies, strict=False):
        bulletins.append(Bulletin(title=feed.name, source=feed.url, body=body))
    return bulletins


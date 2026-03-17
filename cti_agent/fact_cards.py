from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError


class EvidenceItem(BaseModel):
    summary: str
    source_quote: str | None = None


class FactCard(BaseModel):
    """
    Compact per-bulletin representation (the 'map' output).

    Keep this small: it is what we want to feed into the reduce steps rather than raw articles.
    """

    title: str
    source: str

    published_date: str | None = None  # ISO8601 or free-form if unknown

    entities: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Keys like threat_actor, campaign, malware, vulnerability, product",
    )
    iocs: dict[str, list[str]] = Field(default_factory=dict)

    ttp_tags: list[str] = Field(default_factory=list, description="ATT&CK-ish tags or short phrases")

    # SCC-ish signals
    source_credibility: int = Field(ge=1, le=5, default=3)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    exploit_likelihood: float = Field(ge=0.0, le=1.0, default=0.5)
    novelty: float = Field(ge=0.0, le=1.0, default=0.5, description="How new/urgent vs background noise")

    key_points: list[str] = Field(default_factory=list, max_length=12)
    evidence: list[EvidenceItem] = Field(default_factory=list, max_length=6)

    # Filled later (deterministic scoring)
    score: float | None = None


def try_parse_fact_card(obj: Any) -> FactCard | None:
    try:
        return FactCard.model_validate(obj)
    except ValidationError:
        return None


def try_parse_fact_card_json(text: str) -> FactCard | None:
    """
    Accepts either:
    - raw JSON object
    - JSON wrapped in markdown fences
    """
    s = text.strip()
    if "```" in s:
        # naive fence stripping (good enough for template mode)
        parts = [p for p in s.split("```") if p.strip()]
        s = parts[-1].strip()
        if s.lower().startswith("json"):
            s = s[4:].strip()
    try:
        data = json.loads(s)
    except Exception:
        return None
    return try_parse_fact_card(data)


class SelectionStrategy(BaseModel):
    strategy: Literal["top_n"] = "top_n"
    n: int = Field(default=12, ge=1, le=50)


from __future__ import annotations

from dataclasses import dataclass

from cti_agent.fact_cards import FactCard, try_parse_fact_card_json
from cti_agent.models import Bulletin
from cti_agent.tools.llm import OllamaClient


@dataclass(frozen=True)
class FactCardResult:
    fact_cards: list[FactCard]
    errors: list[str]


def bulletins_to_fact_cards(*, bulletins: list[Bulletin]) -> FactCardResult:
    """
    MAP step: Convert each bulletin into a compact JSON 'fact card'.

    This is intentionally strict about output size and schema to reduce downstream token use.
    """
    llm = OllamaClient.from_env()

    cards: list[FactCard] = []
    errors: list[str] = []
    for b in bulletins:
        prompt = (
            "You are a cyber threat intelligence analyst.\n\n"
            "Create a compact JSON fact card for the bulletin.\n"
            "Rules:\n"
            "- Output JSON only (no prose).\n"
            "- Keep lists short.\n"
            "- Prefer canonical values (CVE-YYYY-NNNN, domains, IPs, URLs, hashes).\n"
            "- If unknown, use null or empty lists.\n\n"
            "JSON SCHEMA (informal):\n"
            "{\n"
            '  "title": string,\n'
            '  "source": string,\n'
            '  "published_date": string|null,\n'
            '  "entities": { "threat_actor": [], "campaign": [], "malware": [], "vulnerability": [], "product": [] },\n'
            '  "iocs": { "ip": [], "domain": [], "url": [], "hash": [], "email": [] },\n'
            '  "ttp_tags": [],\n'
            '  "source_credibility": 1..5,\n'
            '  "confidence": 0..1,\n'
            '  "exploit_likelihood": 0..1,\n'
            '  "novelty": 0..1,\n'
            '  "key_points": [],\n'
            '  "evidence": [{"summary": "...", "source_quote": "..."}]\n'
            "}\n\n"
            f"BULLETIN TITLE: {b.title}\n"
            f"BULLETIN SOURCE: {b.source}\n"
            "BULLETIN TEXT:\n"
            f"{b.body}\n"
        )

        raw = llm.generate(prompt)
        card = try_parse_fact_card_json(raw)
        if card is None:
            errors.append(f"Failed to parse fact card for '{b.title}' from source '{b.source}'")
            continue
        # Ensure provenance is correct even if model deviated.
        card = card.model_copy(update={"title": b.title, "source": b.source})
        cards.append(card)

    return FactCardResult(fact_cards=cards, errors=errors)


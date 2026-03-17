from __future__ import annotations

from dataclasses import dataclass

from cti_agent.fact_cards import FactCard


@dataclass(frozen=True)
class ScoreWeights:
    source_credibility: float = 0.20
    confidence: float = 0.30
    exploit_likelihood: float = 0.30
    novelty: float = 0.20


def score_fact_card(card: FactCard, *, w: ScoreWeights = ScoreWeights()) -> float:
    """
    Deterministic scoring to drive selection and minimize 'LLM-as-a-sorter' cost.

    Returns a 0..100 score.
    """
    s = (card.source_credibility - 1) / 4  # 0..1
    c = float(card.confidence)
    e = float(card.exploit_likelihood)
    n = float(card.novelty)

    base = (w.source_credibility * s) + (w.confidence * c) + (w.exploit_likelihood * e) + (w.novelty * n)

    # Small deterministic boosts for "actionability"
    ioc_count = sum(len(v) for v in (card.iocs or {}).values())
    vuln_count = len((card.entities or {}).get("vulnerability", []))
    boost = 0.0
    if vuln_count > 0:
        boost += 0.05
    if ioc_count >= 5:
        boost += 0.05
    if ioc_count >= 25:
        boost += 0.05

    return round(min(1.0, base + boost) * 100.0, 2)


def rank_and_select(cards: list[FactCard], *, top_n: int = 12) -> tuple[list[FactCard], list[FactCard]]:
    scored: list[FactCard] = []
    for c in cards:
        score = score_fact_card(c)
        scored.append(c.model_copy(update={"score": score}))
    scored.sort(key=lambda x: (x.score or 0.0), reverse=True)
    selected = scored[:top_n]
    remainder = scored[top_n:]
    return selected, remainder


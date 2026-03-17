from __future__ import annotations

from dataclasses import dataclass

from cti_agent.fact_cards import FactCard
from cti_agent.scoring import rank_and_select
from cti_agent.tools.cmdb import CmdbClient, OpenSearchCmdbClient
from cti_agent.tools.llm import OllamaClient
from cti_agent.tools.top_actors import SqlTopActorsClient, TopActorsClient


@dataclass(frozen=True)
class TriageResult:
    selected_titles: list[str]
    selection_summary: str
    concerning_summary: str
    rationale: str


def triage_items(*, fact_cards: list[FactCard], top_n: int = 12) -> TriageResult:
    """
    Part 2: Triage using an LLM + internal context.

    New approach:
    - Deterministically rank/select top N fact cards (cheap).
    - Ask the model to produce a concise triage narrative from compact fact cards + internal context.
    """
    llm = OllamaClient.from_env()

    cmdb: CmdbClient = OpenSearchCmdbClient.from_env()
    top_actors: TopActorsClient = SqlTopActorsClient.from_env()

    # Minimal internal context examples; expand with richer, schema-aware queries.
    cmdb_context = cmdb.get_high_value_assets_summary(limit=25)
    actors_context = top_actors.get_top_actors(limit=20)

    selected, remainder = rank_and_select(fact_cards, top_n=top_n)
    selected_titles = [c.title for c in selected]

    selected_compact = "\n".join(
        [
            f"- title: {c.title}\n"
            f"  score: {c.score}\n"
            f"  key_points: {c.key_points[:6]}\n"
            f"  vulnerabilities: {(c.entities or {}).get('vulnerability', [])}\n"
            f"  malware: {(c.entities or {}).get('malware', [])}\n"
            f"  actors: {(c.entities or {}).get('threat_actor', [])}\n"
            f"  ioc_counts: {{"
            + ", ".join([f"{k}:{len(v)}" for k, v in (c.iocs or {}).items()])
            + "}}\n"
            for c in selected
        ]
    )

    prompt = (
        "You are a cyber threat intelligence triage assistant.\n\n"
        "TASK:\n"
        "- Review the selected fact cards (already filtered and ranked).\n"
        "- Use internal context to determine what is most concerning for the environment.\n"
        "- Produce:\n"
        "  1) A short 'selection summary' describing why these items rose to the top\n"
        "  2) A 'concerning summary' (top risks)\n"
        "  3) A clear rationale tied to environment exposure and actionability\n\n"
        "INTERNAL CONTEXT:\n"
        f"- CMDB (high value assets):\n{cmdb_context}\n\n"
        f"- Top threat actors:\n{actors_context}\n\n"
        "SELECTED FACT CARDS:\n"
        f"{selected_compact}\n"
    )

    response = llm.generate(prompt)
    return TriageResult(
        selected_titles=selected_titles,
        selection_summary="Selected top items by deterministic score; see concerning summary.",
        concerning_summary=response.strip(),
        rationale="(see concerning summary)",
    )


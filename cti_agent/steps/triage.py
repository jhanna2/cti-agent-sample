from __future__ import annotations

from dataclasses import dataclass

from cti_agent.tools.cmdb import CmdbClient, OpenSearchCmdbClient
from cti_agent.tools.llm import OllamaClient
from cti_agent.tools.top_actors import SqlTopActorsClient, TopActorsClient


@dataclass(frozen=True)
class TriageResult:
    concerning_summary: str
    rationale: str


def triage_items(bulletin_text: str) -> TriageResult:
    """
    Part 2: Triage using an LLM + internal context.

    The LLM/tooling is intentionally light here: a single prompt that can be extended into
    a tool-calling loop (function calling / ReAct / JSON schema).
    """
    llm = OllamaClient.from_env()

    cmdb: CmdbClient = OpenSearchCmdbClient.from_env()
    top_actors: TopActorsClient = SqlTopActorsClient.from_env()

    # Minimal internal context examples; expand with richer, schema-aware queries.
    cmdb_context = cmdb.get_high_value_assets_summary(limit=25)
    actors_context = top_actors.get_top_actors(limit=20)

    prompt = (
        "You are a cyber threat intelligence triage assistant.\n\n"
        "TASK:\n"
        "- Read the bulletin.\n"
        "- Use the internal context to decide what is most concerning for the environment.\n"
        "- Output a short 'concerning summary' and a clear rationale.\n\n"
        "INTERNAL CONTEXT:\n"
        f"- CMDB (high value assets):\n{cmdb_context}\n\n"
        f"- Top threat actors:\n{actors_context}\n\n"
        "BULLETIN:\n"
        f"{bulletin_text}\n"
    )

    response = llm.generate(prompt)
    # Template parsing: keep free-form for now; later make it structured JSON.
    return TriageResult(concerning_summary=response.strip(), rationale="(see summary)")


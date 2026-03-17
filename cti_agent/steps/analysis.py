from __future__ import annotations

from pathlib import Path

from cti_agent.fact_cards import FactCard
from cti_agent.steps.enrich import EnrichmentResult
from cti_agent.steps.triage import TriageResult
from cti_agent.tools.llm import OllamaClient


def analyze_and_report(
    *,
    fact_cards: list[FactCard],
    triage: TriageResult,
    enriched: EnrichmentResult,
    out_dir: Path,
) -> Path:
    """
    Part 4: Analysis + reporting.

    Produces a single markdown report with an exec summary + operational recommendations.
    """
    llm = OllamaClient.from_env()
    facts_compact = "\n".join(
        [
            f"- title: {c.title}\n"
            f"  score: {c.score}\n"
            f"  key_points: {c.key_points[:8]}\n"
            f"  entities: {c.entities}\n"
            f"  ioc_counts: {{"
            + ", ".join([f"{k}:{len(v)}" for k, v in (c.iocs or {}).items()])
            + "}}\n"
            for c in fact_cards
        ]
    )
    prompt = (
        "You are a cyber threat intelligence analyst.\n\n"
        "Write a report with:\n"
        "1) Executive summary (daily news bulletin style)\n"
        "2) What is most relevant to the environment and why\n"
        "3) Operational actions + defensive recommendations that are specific and actionable.\n"
        "   Avoid generic advice like 'enable MFA'.\n\n"
        f"TRIAGE SUMMARY:\n{triage.concerning_summary}\n\n"
        f"ENRICHMENT NOTES:\n{enriched.notes}\n\n"
        "SELECTED FACT CARDS:\n"
        f"{facts_compact}\n\n"
        "ENRICHED IOC SUMMARY (partial):\n"
        f"{str(enriched.enriched_iocs)[:4000]}\n"
    )

    report_md = llm.generate(prompt).strip()
    path = out_dir / "cti_report.md"
    path.write_text(report_md + "\n", encoding="utf-8")
    return path


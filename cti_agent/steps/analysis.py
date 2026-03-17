from __future__ import annotations

from pathlib import Path

from cti_agent.steps.enrich import EnrichmentResult
from cti_agent.steps.extract import ExtractionResult
from cti_agent.steps.triage import TriageResult
from cti_agent.tools.llm import OllamaClient


def analyze_and_report(
    *,
    bulletin_text: str,
    triage: TriageResult,
    extracted: ExtractionResult,
    enriched: EnrichmentResult,
    out_dir: Path,
) -> Path:
    """
    Part 4: Analysis + reporting.

    Produces a single markdown report with an exec summary + operational recommendations.
    """
    llm = OllamaClient.from_env()
    prompt = (
        "You are a cyber threat intelligence analyst.\n\n"
        "Write a report with:\n"
        "1) Executive summary (daily news bulletin style)\n"
        "2) What is most relevant to the environment and why\n"
        "3) Operational actions + defensive recommendations that are specific and actionable.\n"
        "   Avoid generic advice like 'enable MFA'.\n\n"
        f"TRIAGE SUMMARY:\n{triage.concerning_summary}\n\n"
        f"EXTRACTED IOC COUNTS:\n"
        f"- ips: {len(extracted.iocs.get('ip', []))}\n"
        f"- domains: {len(extracted.iocs.get('domain', []))}\n"
        f"- urls: {len(extracted.iocs.get('url', []))}\n"
        f"- hashes: {len(extracted.iocs.get('hash', []))}\n\n"
        f"ENRICHMENT NOTES:\n{enriched.notes}\n\n"
        "BULLETIN:\n"
        f"{bulletin_text}\n"
    )

    report_md = llm.generate(prompt).strip()
    path = out_dir / "cti_report.md"
    path.write_text(report_md + "\n", encoding="utf-8")
    return path


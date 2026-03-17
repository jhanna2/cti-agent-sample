from __future__ import annotations

from pathlib import Path

from cti_agent.steps.enrich import EnrichmentResult
from cti_agent.steps.extract import ExtractionResult
from cti_agent.steps.triage import TriageResult
from cti_agent.tools.llm import OllamaClient


def generate_detections(
    *,
    bulletin_text: str,
    triage: TriageResult,
    extracted: ExtractionResult,
    enriched: EnrichmentResult,
    out_dir: Path,
) -> Path:
    """
    Part 5: Generate hunting/detection content (starter templates).
    """
    detections_dir = out_dir / "detections"
    detections_dir.mkdir(parents=True, exist_ok=True)

    llm = OllamaClient.from_env()
    prompt = (
        "You are a detection engineer.\n\n"
        "Based on the bulletin and IOCs, produce:\n"
        "1) OpenSearch detection rule ideas (in JSON-like pseudo-structure)\n"
        "2) YARA rule (only if appropriate)\n"
        "3) Suricata rule (only if appropriate)\n\n"
        "Keep it realistic and grounded in the provided data.\n\n"
        f"TRIAGE:\n{triage.concerning_summary}\n\n"
        f"IOCS:\n{extracted.iocs}\n\n"
        f"ENRICHED (partial):\n{_truncate(str(enriched.enriched_iocs), 3000)}\n\n"
        f"BULLETIN:\n{bulletin_text}\n"
    )

    content = llm.generate(prompt).strip()
    path = detections_dir / "generated_detections.md"
    path.write_text(content + "\n", encoding="utf-8")
    return detections_dir


def _truncate(s: str, max_len: int) -> str:
    if len(s) <= max_len:
        return s
    return s[:max_len] + "...(truncated)"


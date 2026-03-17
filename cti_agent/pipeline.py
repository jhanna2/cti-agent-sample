from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from cti_agent.fact_cards import FactCard
from cti_agent.steps.analysis import analyze_and_report
from cti_agent.steps.detections import generate_detections
from cti_agent.steps.enrich import enrich_entities_and_iocs
from cti_agent.steps.fetch import fetch_and_optimize_text
from cti_agent.steps.fact_cards import bulletins_to_fact_cards
from cti_agent.steps.triage import triage_items
from cti_agent.run_metadata import BulletinMeta, PhaseTiming, RunMetadata
from cti_agent.telemetry import capture_tool_calls


@dataclass(frozen=True)
class PipelineResult:
    report_path: Path
    detections_dir: Path
    run_metadata_path: Path


def run_pipeline(*, out_dir: Path, input_path: Path | None = None) -> PipelineResult:
    started_at = time.time()
    t0 = time.perf_counter()
    phase_timings: list[PhaseTiming] = []

    def _time_phase(name: str, fn):
        p0 = time.perf_counter()
        out = fn()
        phase_timings.append(PhaseTiming(name=name, duration_ms=int((time.perf_counter() - p0) * 1000)))
        return out

    with capture_tool_calls() as tool_calls:
        fetch_result = _time_phase("fetch", lambda: fetch_and_optimize_text(input_path=input_path))
        bulletins_kept = fetch_result.bulletins_kept

        fact_result = _time_phase("fact_cards", lambda: bulletins_to_fact_cards(bulletins=bulletins_kept))
        fact_cards: list[FactCard] = fact_result.fact_cards

        triage = _time_phase("triage", lambda: triage_items(fact_cards=fact_cards, top_n=12))

        selected_fact_cards = [c for c in fact_cards if c.title in set(triage.selected_titles)]
        enriched = _time_phase("enrich", lambda: enrich_entities_and_iocs(fact_cards=selected_fact_cards, out_dir=out_dir))

        report_path = _time_phase(
            "analysis_report",
            lambda: analyze_and_report(
                fact_cards=selected_fact_cards,
                triage=triage,
                enriched=enriched,
                out_dir=out_dir,
            ),
        )

        detections_dir = _time_phase(
            "detections",
            lambda: generate_detections(
                fact_cards=selected_fact_cards,
                triage=triage,
                enriched=enriched,
                out_dir=out_dir,
            ),
        )

    finished_at = time.time()
    total_ms = int((time.perf_counter() - t0) * 1000)
    run_meta = RunMetadata(
        started_at_unix_s=started_at,
        finished_at_unix_s=finished_at,
        total_duration_ms=total_ms,
        phase_timings=phase_timings,
        tool_calls=list(tool_calls),
        bulletins_analyzed=[BulletinMeta(title=b.title, source=b.source) for b in fetch_result.bulletins],
        bulletins_kept=[BulletinMeta(title=b.title, source=b.source) for b in fetch_result.bulletins_kept],
        toon_optimization=fetch_result.toon_optimization,
    )
    run_metadata_path = out_dir / "run_metadata.json"
    run_meta.write_json(run_metadata_path)

    return PipelineResult(
        report_path=report_path,
        detections_dir=detections_dir,
        run_metadata_path=run_metadata_path,
    )


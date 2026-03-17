from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from cti_agent.steps.fetch import TokenOptimizationMeta
from cti_agent.telemetry import ToolCallRecord, tool_calls_as_json


@dataclass(frozen=True)
class PhaseTiming:
    name: str
    duration_ms: int


@dataclass(frozen=True)
class BulletinMeta:
    title: str
    source: str


@dataclass(frozen=True)
class RunMetadata:
    started_at_unix_s: float
    finished_at_unix_s: float
    total_duration_ms: int
    phase_timings: list[PhaseTiming] = field(default_factory=list)
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    bulletins_analyzed: list[BulletinMeta] = field(default_factory=list)
    bulletins_kept: list[BulletinMeta] = field(default_factory=list)
    toon_optimization: TokenOptimizationMeta | None = None

    def to_jsonable(self) -> dict:
        d = asdict(self)
        # Replace tool_calls with stable dicts (dataclass -> dict is fine, but keep explicit)
        d["tool_calls"] = tool_calls_as_json(self.tool_calls)
        return d

    def write_json(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_jsonable(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


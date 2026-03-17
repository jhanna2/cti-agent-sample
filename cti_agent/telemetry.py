from __future__ import annotations

import contextlib
import threading
import time
from dataclasses import asdict, dataclass
from typing import Any, Iterator


@dataclass(frozen=True)
class ToolCallRecord:
    name: str
    started_at_unix_s: float
    duration_ms: int
    input_summary: str
    output_summary: str
    ok: bool


_state = threading.local()


def _get_buffer() -> list[ToolCallRecord] | None:
    return getattr(_state, "buffer", None)


@contextlib.contextmanager
def capture_tool_calls() -> Iterator[list[ToolCallRecord]]:
    """
    Context manager to collect tool calls across the pipeline.

    Tools that want to be tracked should call `record_tool_call(...)`.
    """
    prev = _get_buffer()
    buf: list[ToolCallRecord] = []
    _state.buffer = buf
    try:
        yield buf
    finally:
        _state.buffer = prev


def record_tool_call(
    *,
    name: str,
    input_summary: str,
    output_summary: str,
    started_at_unix_s: float,
    duration_ms: int,
    ok: bool,
) -> None:
    buf = _get_buffer()
    if buf is None:
        return
    buf.append(
        ToolCallRecord(
            name=name,
            started_at_unix_s=started_at_unix_s,
            duration_ms=duration_ms,
            input_summary=input_summary,
            output_summary=output_summary,
            ok=ok,
        )
    )


@contextlib.contextmanager
def timed_tool_call(name: str, input_summary: str) -> Iterator[dict[str, Any]]:
    """
    Helper to time + record a tool call.

    Usage:
      with timed_tool_call("cmdb.get_assets", "limit=25") as meta:
          ... do work ...
          meta["output_summary"] = "..."
    """
    started = time.time()
    t0 = time.perf_counter()
    meta: dict[str, Any] = {"output_summary": "", "ok": True}
    try:
        yield meta
    except Exception as e:  # pragma: no cover
        meta["ok"] = False
        meta["output_summary"] = f"error: {e}"
        raise
    finally:
        dt_ms = int((time.perf_counter() - t0) * 1000)
        record_tool_call(
            name=name,
            input_summary=input_summary,
            output_summary=str(meta.get("output_summary", "")),
            started_at_unix_s=started,
            duration_ms=dt_ms,
            ok=bool(meta.get("ok", True)),
        )


def tool_calls_as_json(tool_calls: list[ToolCallRecord]) -> list[dict[str, Any]]:
    return [asdict(tc) for tc in tool_calls]


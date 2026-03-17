from __future__ import annotations

from dataclasses import dataclass

from cti_agent.telemetry import timed_tool_call


class EnrichmentClient:
    name: str
    enabled: bool

    def enrich(self, *, ioc_type: str, value: str) -> dict[str, object]:  # pragma: no cover
        raise NotImplementedError


@dataclass(frozen=True)
class MultiEnrichmentClient:
    clients: list[EnrichmentClient]

    def enrich(self, *, ioc_type: str, value: str) -> dict[str, object]:
        results: dict[str, object] = {"sources": {}}
        for c in self.clients:
            with timed_tool_call(
                f"enrich.{c.name}",
                input_summary=f"{ioc_type}={value}",
            ) as meta:
                try:
                    out = c.enrich(ioc_type=ioc_type, value=value)
                    results["sources"][c.name] = out
                    meta["output_summary"] = "ok"
                except Exception as e:  # keep pipeline moving in template mode
                    results["sources"][c.name] = {"error": str(e)}
                    meta["ok"] = False
                    meta["output_summary"] = f"error: {e}"
        return results


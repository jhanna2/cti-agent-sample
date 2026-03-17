from __future__ import annotations

import os

import httpx

from cti_agent.telemetry import timed_tool_call


class OllamaClient:
    def __init__(self, *, base_url: str, model: str, timeout_s: float = 120.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(timeout=timeout_s)

    @classmethod
    def from_env(cls) -> "OllamaClient":
        return cls(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "mistral:7b"),
        )

    def generate(self, prompt: str) -> str:
        """
        Minimal Ollama generate call.
        Later: add structured JSON output, tool calling, streaming, retries, and prompt templates.
        """
        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        with timed_tool_call(
            "ollama.generate",
            input_summary=f"model={self.model}, prompt_chars={len(prompt)}",
        ) as meta:
            r = self._client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            out = str(data.get("response", ""))
            meta["output_summary"] = f"response_chars={len(out)}"
            return out


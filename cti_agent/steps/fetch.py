from __future__ import annotations

import re
from pathlib import Path

from dataclasses import dataclass

from cti_agent.models import Bulletin
from cti_agent.tools.feeds import fetch_bulletins, get_default_free_feeds


@dataclass(frozen=True)
class TokenOptimizationMeta:
    method: str
    input_chars: int
    output_chars: int


@dataclass(frozen=True)
class FetchResult:
    bulletins: list[Bulletin]
    bulletins_kept: list[Bulletin]
    merged_text: str
    toon_optimization: TokenOptimizationMeta


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch_and_optimize_text(*, input_path: Path | None = None) -> FetchResult:
    """
    Part 1: Fetch + token optimization.

    Primary behavior:
    - Pull from a set of free CTI feeds (CISA KEV, abuse.ch, OTX, urlscan, etc.)
      using helpers in `cti_agent.tools.feeds`.
    - Normalize and merge those bulletins into a single text stream.

    Optional:
    - If `input_path` is provided, its contents are appended as an extra bulletin.
    """
    # 1) Remote feeds
    feeds = get_default_free_feeds()
    bulletins = fetch_bulletins(feeds)

    # 2) Optional local bulletin
    if input_path is not None and input_path.exists():
        local_raw = input_path.read_text(encoding="utf-8", errors="replace")
        bulletins.append(Bulletin(title=input_path.name, source=str(input_path), body=_normalize_whitespace(local_raw)))

    # Template filtering: keep all bulletins unless they are empty or errored.
    kept: list[Bulletin] = [b for b in bulletins if b.body.strip()]

    merged_in = "\n\n".join(f"# {b.title}\n\n{b.body}" for b in kept)
    merged_out = _normalize_whitespace(merged_in)

    toon = TokenOptimizationMeta(
        method="normalize_whitespace (template); toon conversion TODO",
        input_chars=len(merged_in),
        output_chars=len(merged_out),
    )

    return FetchResult(
        bulletins=bulletins,
        bulletins_kept=kept,
        merged_text=merged_out,
        toon_optimization=toon,
    )



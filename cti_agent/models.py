from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Bulletin:
    title: str
    source: str
    body: str


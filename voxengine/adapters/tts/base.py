"""Shared data structures for TTS adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class TTSAudio:
    """Audio render result returned by adapters."""

    path: Path
    sample_rate: int
    duration_s: Optional[float] = None
    warnings: List[str] = field(default_factory=list)

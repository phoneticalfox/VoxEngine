"""Adapter registry for VoxEngine."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Protocol

from voxengine.adapters.tts.piper import PiperTTSAdapter


class LLMAdapter(Protocol):
    """Protocol for LLM adapters."""

    def generate_scene(self, prompt: str, constraints: dict) -> dict: ...
    def rewrite_line(self, line: str, direction: str, num: int) -> list[str]: ...


class TTSAdapter(Protocol):
    """Protocol for TTS adapters."""

    def about(self) -> dict: ...
    def speak(self, text: str, out_path, model_path=None, voice=None): ...


@dataclass
class AdapterRegistry:
    """Registered adapters for the engine."""

    llm: Dict[str, LLMAdapter] = field(default_factory=dict)
    tts: Dict[str, TTSAdapter] = field(default_factory=dict)

    @staticmethod
    def default() -> "AdapterRegistry":
        return AdapterRegistry(tts={"piper": PiperTTSAdapter()})

    def list_tts(self) -> List[dict]:
        return [self.tts[k].about() for k in sorted(self.tts.keys())]

    def get_tts(self, name: str) -> TTSAdapter:
        if name not in self.tts:
            raise KeyError(f"Unknown TTS backend '{name}'. Available: {sorted(self.tts.keys())}")
        return self.tts[name]


# Backwards compatibility shims for legacy code paths
registry = AdapterRegistry.default()


def register_llm(name: str, adapter: LLMAdapter) -> None:
    registry.llm[name] = adapter


def register_tts(name: str, adapter: TTSAdapter) -> None:
    registry.tts[name] = adapter

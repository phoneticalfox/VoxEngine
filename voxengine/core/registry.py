"""Adapter registry."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Protocol

class LLMAdapter(Protocol):
    def generate_scene(self, prompt: str, constraints: dict) -> dict: ...
    def rewrite_line(self, line: str, direction: str, num: int) -> list[str]: ...

class TTSAdapter(Protocol):
    def register_voice(self, reference_wav_path: str) -> dict: ...
    def speak(self, text: str, voice_ref: dict, style: dict, output_path: str) -> None: ...

@dataclass
class Registry:
    llm_adapters: Dict[str, LLMAdapter]
    tts_adapters: Dict[str, TTSAdapter]

registry = Registry(llm_adapters={}, tts_adapters={})

def register_llm(name: str, adapter: LLMAdapter) -> None:
    registry.llm_adapters[name] = adapter

def register_tts(name: str, adapter: TTSAdapter) -> None:
    registry.tts_adapters[name] = adapter

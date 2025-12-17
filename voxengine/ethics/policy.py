"""Minimal ethics policy for engine checks."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Attestation:
    has_consent: bool = False
    is_self_voice: bool = False
    is_accessibility_use: bool = False
    notes: str = ""


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str = ""


class EthicsPolicy:
    """Simple policy gate (placeholder for richer rules)."""

    @staticmethod
    def default() -> "EthicsPolicy":
        return EthicsPolicy()

    def check_tts(
        self, text: str, backend: str, voice: Optional[str], attestation: Optional[Attestation]
    ) -> PolicyDecision:
        # v0.1: standard TTS is allowed. Voice cloning will be a separate path with attestations
        # required.
        return PolicyDecision(True, "ok")

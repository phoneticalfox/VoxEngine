"""A minimal always-available TTS backend that writes a short tone.

Used for smoke testing the pipeline without external dependencies.
"""

from __future__ import annotations

import math
import wave
from pathlib import Path
from typing import Optional

from voxengine.adapters.tts.base import TTSAudio
from voxengine.core.errors import UserConfigError


class BeepTTSAdapter:
    """Generate a simple WAV tone for validation."""

    def __init__(self, freq_hz: float = 440.0, duration_s: float = 0.5, sample_rate: int = 16000):
        self.freq_hz = freq_hz
        self.duration_s = duration_s
        self.sample_rate = sample_rate

    def about(self) -> dict:
        return {
            "name": "beep",
            "type": "tts",
            "offline": True,
            "needs_executable": False,
            "executable_found": True,
            "available": True,
            "notes": "Built-in tone generator for smoke tests.",
        }

    def speak(
        self,
        text: str,
        out_path: Path,
        model_path: Optional[Path] = None,
        voice: Optional[str] = None,
        profile: Optional[str] = None,
        out_format: str = "wav",
    ) -> TTSAudio:
        if out_format != "wav":
            raise UserConfigError("Beep backend only supports wav output.")

        out_path.parent.mkdir(parents=True, exist_ok=True)
        num_samples = int(self.duration_s * self.sample_rate)
        amplitude = 32767
        with wave.open(str(out_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(self.sample_rate)
            for i in range(num_samples):
                sample = int(amplitude * math.sin(2 * math.pi * self.freq_hz * i / self.sample_rate))
                wav.writeframes(sample.to_bytes(2, byteorder="little", signed=True))

        return TTSAudio(path=out_path, sample_rate=self.sample_rate, duration_s=self.duration_s)

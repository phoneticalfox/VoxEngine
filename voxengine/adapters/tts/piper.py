"""Piper TTS adapter."""

from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from voxengine.adapters.tts.base import TTSAudio
from voxengine.core.errors import MissingDependencyError, UserConfigError


class PiperTTSAdapter:
    """Lightweight wrapper around the Piper executable."""

    def about(self) -> dict:
        return {
            "name": "piper",
            "type": "tts",
            "offline": True,
            "needs_executable": True,
            "executable_found": shutil.which("piper") is not None,
            "available": shutil.which("piper") is not None,
            "notes": "Requires 'piper' on PATH plus an .onnx model file.",
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
        exe = shutil.which("piper")
        if not exe:
            raise MissingDependencyError("Piper backend selected but 'piper' was not found on PATH.")
        if model_path is None:
            raise UserConfigError("Piper requires --model pointing to an .onnx voice model.")
        if not model_path.exists():
            raise UserConfigError(f"Model path does not exist: {model_path}")
        if out_format != "wav":
            raise UserConfigError("Piper currently only supports wav output.")

        out_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [exe, "--model", str(model_path), "--output_file", str(out_path)]
        if voice:
            cmd += ["--speaker", str(voice)]

        proc = subprocess.run(
            cmd, input=text.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Piper failed: {proc.stderr.decode('utf-8', errors='ignore')}")
        return TTSAudio(path=out_path, sample_rate=22050)

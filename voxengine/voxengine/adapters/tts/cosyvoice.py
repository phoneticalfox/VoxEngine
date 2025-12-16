"""CosyVoice TTS adapter (placeholder)."""

from pathlib import Path

class CosyVoiceTTSAdapter:
    def register_voice(self, reference_wav_path: str) -> dict:
        return {"type": "cosyvoice", "reference_wav": reference_wav_path}

    def speak(self, text: str, voice_ref: dict, style: dict, output_path: str) -> None:
        Path(output_path).write_bytes(b"")  # placeholder

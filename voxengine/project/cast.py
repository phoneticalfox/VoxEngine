"""Cast library management (starter)."""

from __future__ import annotations
from pathlib import Path
import json, uuid

class CastManager:
    def register_voice(self, project_path: str, actor_name: str, reference_wav_path: str, consent: dict) -> str:
        project = Path(project_path)
        voice_id = str(uuid.uuid4())
        actor_dir = project / "cast" / actor_name
        actor_dir.mkdir(parents=True, exist_ok=True)

        consent_doc = {
            "voice_id": voice_id,
            "actor_name": actor_name,
            "reference_wav_path": reference_wav_path,
            "consent": consent,
        }
        (actor_dir / "consent.json").write_text(json.dumps(consent_doc, indent=2), encoding="utf-8")
        return voice_id

    def load_voice_ref(self, project_path: str, voice_id: str) -> dict:
        project = Path(project_path)
        for consent_path in project.glob("cast/*/consent.json"):
            data = json.loads(consent_path.read_text(encoding="utf-8"))
            if data.get("voice_id") == voice_id:
                return {"voice_id": voice_id, "reference_wav_path": data.get("reference_wav_path")}
        raise KeyError(f"voice_id not found in project: {voice_id}")

"""High-level TTS service."""

from __future__ import annotations
from pathlib import Path
from voxengine.core.registry import registry
from voxengine.core.queue import JobQueue
from voxengine.project.cast import CastManager
import threading

class TTSService:
    def __init__(self, tts_provider: str, queue: JobQueue) -> None:
        self.tts_provider = tts_provider
        self.queue = queue
        self.cast = CastManager()

    def speak_async(self, project_path: str, voice_id: str, text: str, style: dict, output_format: str = "wav") -> str:
        job = self.queue.create()
        adapter = registry.tts_adapters[self.tts_provider]
        voice_ref = self.cast.load_voice_ref(project_path, voice_id)

        out_dir = Path(project_path) / "renders" / "adhoc"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{job.id}.{output_format}"

        def run():
            try:
                self.queue.set_running(job.id, "synthesizing")
                adapter.speak(text=text, voice_ref=voice_ref, style=style, output_path=str(out_path))
                self.queue.set_done(job.id, {"audio_path": str(out_path)})
            except Exception as e:
                self.queue.set_error(job.id, str(e))

        threading.Thread(target=run, daemon=True).start()
        return job.id

"""Render service (starter)."""

from __future__ import annotations
from voxengine.core.queue import JobQueue
from voxengine.core.tts_service import TTSService
from voxengine.project.format import ProjectManager
import threading

class RenderService:
    def __init__(self, queue: JobQueue, tts: TTSService, projects: ProjectManager) -> None:
        self.queue = queue
        self.tts = tts
        self.projects = projects

    def render_scene_async(self, project_path: str, scene_id: str, voice_map: dict, options: dict) -> str:
        job = self.queue.create()

        def run():
            try:
                self.queue.set_running(job.id, f"rendering scene {scene_id}")
                self.queue.set_progress(job.id, 0.25, "loading scene")
                self.projects.validate(project_path)
                self.queue.set_progress(job.id, 0.75, "placeholder render complete")
                self.queue.set_done(job.id, {"note": "Scene rendering not implemented yet."})
            except Exception as e:
                self.queue.set_error(job.id, str(e))

        threading.Thread(target=run, daemon=True).start()
        return job.id

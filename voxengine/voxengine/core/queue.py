"""In-memory job queue (starter)."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import uuid
import time

@dataclass
class Job:
    id: str
    status: str = "queued"      # queued | running | done | error
    progress: float = 0.0
    detail: Optional[str] = None
    artifacts: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: time.time())

class JobQueue:
    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}

    def create(self) -> Job:
        job_id = str(uuid.uuid4())
        job = Job(id=job_id)
        self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Job:
        return self._jobs[job_id]

    def set_running(self, job_id: str, detail: str | None = None) -> None:
        j = self._jobs[job_id]
        j.status = "running"
        j.detail = detail

    def set_progress(self, job_id: str, progress: float, detail: str | None = None) -> None:
        j = self._jobs[job_id]
        j.progress = float(progress)
        if detail is not None:
            j.detail = detail

    def set_done(self, job_id: str, artifacts: Dict[str, Any] | None = None) -> None:
        j = self._jobs[job_id]
        j.status = "done"
        j.progress = 1.0
        if artifacts:
            j.artifacts.update(artifacts)

    def set_error(self, job_id: str, detail: str) -> None:
        j = self._jobs[job_id]
        j.status = "error"
        j.detail = detail

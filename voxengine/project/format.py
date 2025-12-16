"""Project format utilities."""

from pathlib import Path

REQUIRED_DIRS = ["cast", "script", "renders"]

class ProjectManager:
    def validate(self, project_path: str) -> dict:
        p = Path(project_path)
        if not p.exists():
            raise FileNotFoundError(f"Project not found: {project_path}")
        for d in REQUIRED_DIRS:
            if not (p / d).exists():
                raise ValueError(f"Missing required directory: {d}")
        if not (p / "project.json").exists():
            raise ValueError("Missing project.json")
        return {"ok": True, "project_path": str(p)}

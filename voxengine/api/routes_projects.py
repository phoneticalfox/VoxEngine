"""Routes for project management."""

from fastapi import APIRouter
from pydantic import BaseModel
from voxengine.core.engine import get_engine

router = APIRouter()

class ValidateProjectRequest(BaseModel):
    project_path: str

@router.post("/validate")
def validate_project(req: ValidateProjectRequest):
    engine = get_engine()
    return engine.projects.validate(req.project_path)

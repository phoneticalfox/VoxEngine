"""Routes for render queue jobs."""

from fastapi import APIRouter
from voxengine.api.schemas import RenderSceneRequest, RenderSceneResponse, JobStatusResponse
from voxengine.core.engine import get_engine

router = APIRouter()

@router.post("/scene", response_model=RenderSceneResponse)
def render_scene(req: RenderSceneRequest):
    engine = get_engine()
    job_id = engine.render.render_scene_async(
        project_path=req.project_path,
        scene_id=req.scene_id,
        voice_map=req.voice_map,
        options=req.options,
    )
    return RenderSceneResponse(job_id=job_id)

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def job_status(job_id: str):
    engine = get_engine()
    j = engine.queue.get(job_id)
    return JobStatusResponse(
        job_id=job_id,
        status=j.status,
        progress=j.progress,
        detail=j.detail,
        artifacts=j.artifacts,
    )

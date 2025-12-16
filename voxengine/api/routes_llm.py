"""Routes for script generation / rewriting."""

from fastapi import APIRouter
from voxengine.api.schemas import GenerateSceneRequest, GenerateSceneResponse, RewriteLineRequest, RewriteLineResponse
from voxengine.core.engine import get_engine

router = APIRouter()

@router.post("/generate_scene", response_model=GenerateSceneResponse)
def generate_scene(req: GenerateSceneRequest):
    engine = get_engine()
    scene = engine.script.generate_scene(prompt=req.prompt, constraints=req.constraints)
    return GenerateSceneResponse(scene_text=scene["text"], metadata=scene.get("metadata", {}))

@router.post("/rewrite_line", response_model=RewriteLineResponse)
def rewrite_line(req: RewriteLineRequest):
    engine = get_engine()
    variants = engine.script.rewrite_line(line=req.line, direction=req.direction, num=req.num_variants)
    return RewriteLineResponse(variants=variants)

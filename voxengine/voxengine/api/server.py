"""FastAPI server entrypoint.

Run (dev):
  uvicorn voxengine.api.server:app --reload --host 127.0.0.1 --port 7788
"""

from fastapi import FastAPI
from voxengine.api.routes_llm import router as llm_router
from voxengine.api.routes_tts import router as tts_router
from voxengine.api.routes_projects import router as projects_router
from voxengine.api.routes_render import router as render_router

app = FastAPI(
    title="VoxEngine",
    version="0.1.0",
    description="Offline-first studio backend for local LLM + TTS with cast libraries.",
)

app.include_router(llm_router, prefix="/v1/script", tags=["script"])
app.include_router(tts_router, prefix="/v1", tags=["tts"])
app.include_router(projects_router, prefix="/v1/projects", tags=["projects"])
app.include_router(render_router, prefix="/v1/render", tags=["render"])

@app.get("/health")
def health():
    return {"ok": True, "name": "voxengine"}

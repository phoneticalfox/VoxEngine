"""FastAPI server entrypoint."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from voxengine.api.schemas import SpeakRequest, SpeakResponse
from voxengine.core.engine import EngineConfig, get_engine
from voxengine.core.logging import configure_logging


def create_app() -> FastAPI:
    """Create a FastAPI app with health, doctor, and TTS routes."""
    configure_logging()
    cfg = EngineConfig.load()
    eng = get_engine()
    app = FastAPI(
        title="VoxEngine",
        version=cfg.version,
        description="Offline-first studio backend for local LLM + TTS with cast libraries.",
    )

    @app.get("/health")
    def health():
        return {"status": "ok", "version": cfg.version}

    @app.get("/doctor")
    def doctor():
        return eng.doctor()

    @app.post("/tts/speak", response_model=SpeakResponse)
    def tts_speak(req: SpeakRequest):
        try:
            result = eng.tts_speak(
                text=req.text, backend=req.backend, model_path=req.model_path, voice=req.voice
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return SpeakResponse(**result, download_url=f"/tts/file?path={result['path']}")

    @app.get("/tts/file")
    def tts_file(path: str):
        return FileResponse(path, media_type="audio/wav", filename="speech.wav")

    return app


def run(host: str = "127.0.0.1", port: int = 7341) -> None:
    uvicorn.run(create_app(), host=host, port=port)


app = create_app()

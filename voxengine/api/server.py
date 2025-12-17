"""FastAPI server entrypoint."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from voxengine.api.schemas import SpeakRequest, SpeakResponse
from voxengine.core.engine import EngineConfig, get_engine
from voxengine.core.errors import MissingDependencyError, UserConfigError, VoxEngineError
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

    @app.get("/v1/backends")
    def list_backends():
        return {"tts": eng.doctor().get("tts_backends", [])}

    @app.post("/tts/speak", response_model=SpeakResponse)
    @app.post("/v1/tts/speak", response_model=SpeakResponse)
    def tts_speak(req: SpeakRequest):
        try:
            result = eng.tts_speak(
                text=req.text,
                backend=req.backend,
                model_path=req.model_path,
                voice=req.voice,
                profile=req.profile,
                out_format=req.out_format,
            )
        except UserConfigError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except MissingDependencyError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except VoxEngineError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        return SpeakResponse(**result, download_url=f"/tts/file?path={result['audio_path']}")

    @app.get("/tts/file")
    def tts_file(path: str):
        return FileResponse(path, media_type="audio/wav", filename="speech.wav")

    return app


def run(host: str = "127.0.0.1", port: int = 7341) -> None:
    uvicorn.run(create_app(), host=host, port=port)


app = create_app()

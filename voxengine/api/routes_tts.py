"""Routes for TTS."""

from fastapi import APIRouter, HTTPException

from voxengine.api.schemas import SpeakRequest, SpeakResponse
from voxengine.core.engine import get_engine

router = APIRouter()


@router.post("/tts/speak", response_model=SpeakResponse)
def tts_speak(req: SpeakRequest):
    engine = get_engine()
    try:
        result = engine.tts_speak(
            text=req.text, backend=req.backend, model_path=req.model_path, voice=req.voice
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return SpeakResponse(**result, download_url=f"/tts/file?path={result['path']}")

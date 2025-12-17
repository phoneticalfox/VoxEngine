"""Routes for TTS."""

from fastapi import APIRouter, HTTPException

from voxengine.api.schemas import SpeakRequest, SpeakResponse
from voxengine.core.engine import get_engine
from voxengine.core.errors import MissingDependencyError, UserConfigError, VoxEngineError

router = APIRouter()


@router.post("/tts/speak", response_model=SpeakResponse)
def tts_speak(req: SpeakRequest):
    try:
        result = get_engine().tts_speak(
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

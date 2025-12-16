"""Routes for cast management and TTS."""

from fastapi import APIRouter
from voxengine.api.schemas import CastRegisterRequest, CastRegisterResponse, SpeakRequest, SpeakResponse
from voxengine.core.engine import get_engine

router = APIRouter()

@router.post("/cast/register", response_model=CastRegisterResponse)
def cast_register(req: CastRegisterRequest):
    engine = get_engine()
    voice_id = engine.cast.register_voice(
        project_path=req.project_path,
        actor_name=req.actor_name,
        reference_wav_path=req.reference_wav_path,
        consent=req.consent,
    )
    return CastRegisterResponse(voice_id=voice_id)

@router.post("/tts/speak", response_model=SpeakResponse)
def tts_speak(req: SpeakRequest):
    engine = get_engine()
    job_id = engine.tts.speak_async(
        project_path=req.project_path,
        voice_id=req.voice_id,
        text=req.text,
        style=req.style,
        output_format=req.output_format,
    )
    return SpeakResponse(job_id=job_id, status="queued")

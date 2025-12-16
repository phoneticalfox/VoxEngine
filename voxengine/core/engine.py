"""Engine orchestration."""

from __future__ import annotations
from dataclasses import dataclass
from voxengine.core.config import settings
from voxengine.core.queue import JobQueue
from voxengine.core.registry import register_llm, register_tts
from voxengine.core.logging import get_logger

from voxengine.adapters.llm.ollama import OllamaLLMAdapter
from voxengine.adapters.llm.llama_cpp import LlamaCppLLMAdapter
from voxengine.adapters.tts.piper import PiperTTSAdapter
from voxengine.adapters.tts.cosyvoice import CosyVoiceTTSAdapter

from voxengine.project.cast import CastManager
from voxengine.project.format import ProjectManager
from voxengine.project.scripts import ScriptService
from voxengine.core.render import RenderService
from voxengine.core.tts_service import TTSService

log = get_logger("voxengine.engine")
_engine = None

@dataclass
class Engine:
    queue: JobQueue
    projects: ProjectManager
    cast: CastManager
    script: ScriptService
    tts: TTSService
    render: RenderService

def _init_registry():
    register_llm("ollama", OllamaLLMAdapter())
    register_llm("llama_cpp", LlamaCppLLMAdapter())
    register_tts("piper", PiperTTSAdapter())
    register_tts("cosyvoice", CosyVoiceTTSAdapter())

def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _init_registry()
        q = JobQueue()
        projects = ProjectManager()
        cast = CastManager()
        script = ScriptService(llm_provider=settings.llm_provider)
        tts = TTSService(tts_provider=settings.tts_provider, queue=q)
        render = RenderService(queue=q, tts=tts, projects=projects)
        _engine = Engine(queue=q, projects=projects, cast=cast, script=script, tts=tts, render=render)
        log.info("Initialized VoxEngine (llm=%s, tts=%s)", settings.llm_provider, settings.tts_provider)
    return _engine

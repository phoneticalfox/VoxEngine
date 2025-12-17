"""Engine orchestration."""

from __future__ import annotations
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from platformdirs import user_cache_dir

from voxengine.core.logging import get_logger
from voxengine.core.registry import AdapterRegistry, registry as default_registry
from voxengine.ethics.policy import Attestation, EthicsPolicy

log = get_logger("voxengine.engine")


@dataclass(frozen=True)
class EngineConfig:
    version: str = "0.1.0"
    cache_dir: Path = Path(user_cache_dir("voxengine", "voxengine"))
    models_dir: Path = Path(user_cache_dir("voxengine_models", "voxengine"))

    @staticmethod
    def load() -> "EngineConfig":
        cache_dir = Path(os.getenv("VOXENGINE_CACHE_DIR", user_cache_dir("voxengine", "voxengine")))
        models_dir = Path(
            os.getenv("VOXENGINE_MODELS_DIR", user_cache_dir("voxengine_models", "voxengine"))
        )
        return EngineConfig(cache_dir=cache_dir, models_dir=models_dir)


class Engine:
    def __init__(self, cfg: EngineConfig, registry: Optional[AdapterRegistry] = None):
        self.cfg = cfg
        self.cfg.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cfg.models_dir.mkdir(parents=True, exist_ok=True)
        self.registry = registry or AdapterRegistry.default()
        self.ethics = EthicsPolicy.default()

    def doctor(self) -> Dict[str, Any]:
        return {
            "version": self.cfg.version,
            "cache_dir": str(self.cfg.cache_dir),
            "models_dir": str(self.cfg.models_dir),
            "tts_backends": self.registry.list_tts(),
        }

    def tts_speak(
        self,
        text: str,
        backend: str = "piper",
        out_path: Optional[Path] = None,
        model_path: Optional[Path] = None,
        voice: Optional[str] = None,
        attestation: Optional[Attestation] = None,
    ) -> Dict[str, Any]:
        decision = self.ethics.check_tts(
            text=text, backend=backend, voice=voice, attestation=attestation
        )
        if not decision.allowed:
            raise ValueError(f"Blocked by policy: {decision.reason}")

        adapter = self.registry.get_tts(backend)
        if out_path is None:
            out_path = self.cfg.cache_dir / f"tts_{uuid.uuid4().hex}.wav"

        result = adapter.speak(text=text, out_path=out_path, model_path=model_path, voice=voice)
        return {"backend": backend, "path": str(result.path), "sample_rate": result.sample_rate}


_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """Return a shared engine instance for HTTP + CLI usage."""
    global _engine
    if _engine is None:
        cfg = EngineConfig.load()
        _engine = Engine(cfg=cfg, registry=default_registry)
        log.info("Initialized VoxEngine %s", cfg.version)
    return _engine

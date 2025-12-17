"""Engine orchestration."""

from __future__ import annotations
import os
import uuid
from dataclasses import dataclass
import json
import platform
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from platformdirs import user_cache_dir

from voxengine.adapters.tts.base import TTSAudio
from voxengine.core.logging import get_logger
from voxengine.core.registry import AdapterRegistry, registry as default_registry
from voxengine.ethics.policy import Attestation, EthicsPolicy
from voxengine.core.errors import MissingDependencyError, UserConfigError

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
        models = self.discover_models()
        tts_backends = self.registry.list_tts()
        available_backends = [b for b in tts_backends if b.get("available")]

        next_steps: List[str] = []
        if not any(b["name"] == "piper" and b.get("executable_found") for b in tts_backends):
            next_steps.append(
                "Install the 'piper' executable and ensure it is on PATH to enable the "
                "default backend."
            )
        if not models:
            next_steps.append(f"Add a Piper model to the models directory: {self.cfg.models_dir}.")
        if not available_backends:
            next_steps.append(
                "Use the built-in beep backend to verify audio output: "
                "voxengine tts speak 'hello' --backend beep."
            )

        return {
            "version": self.cfg.version,
            "system": {
                "python": platform.python_version(),
                "platform": platform.platform(),
            },
            "cache_dir": str(self.cfg.cache_dir),
            "models_dir": str(self.cfg.models_dir),
            "models": models,
            "tts_backends": tts_backends,
            "next_steps": next_steps,
        }

    def discover_models(self) -> List[Dict[str, str]]:
        allowed = {".onnx", ".bin", ".pt"}
        if not self.cfg.models_dir.exists():
            return []
        models: List[Dict[str, str]] = []
        for path in sorted(self.cfg.models_dir.iterdir()):
            if path.is_file() and path.suffix.lower() in allowed:
                models.append({"name": path.stem, "path": str(path)})
        return models

    def add_model(self, source: Path, name: Optional[str] = None) -> Path:
        if not source.exists() or not source.is_file():
            raise UserConfigError(f"Model file not found: {source}")
        dest_name = f"{name or source.stem}{source.suffix}"
        dest_path = self.cfg.models_dir / dest_name
        if dest_path.exists():
            raise UserConfigError(
                f"A model named '{dest_name}' already exists in {self.cfg.models_dir}"
            )
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest_path)
        return dest_path

    def tts_speak(
        self,
        text: str,
        backend: str = "piper",
        out_path: Optional[Path] = None,
        model_path: Optional[Path] = None,
        voice: Optional[str] = None,
        profile: Optional[str] = None,
        attestation: Optional[Attestation] = None,
        out_format: str = "wav",
    ) -> Dict[str, Any]:
        decision = self.ethics.check_tts(
            text=text, backend=backend, voice=voice, attestation=attestation
        )
        if not decision.allowed:
            raise UserConfigError(f"Blocked by policy: {decision.reason}")

        adapter = self.registry.get_tts(backend)
        if out_path is None:
            out_path = self.cfg.cache_dir / f"tts_{uuid.uuid4().hex}.{out_format}"
        else:
            out_path = out_path.with_suffix(f".{out_format}")

        resolved_model = model_path
        if backend == "piper" and model_path is None:
            resolved_model = self._select_piper_model()

        result = adapter.speak(
            text=text,
            out_path=out_path,
            model_path=resolved_model,
            voice=voice,
            profile=profile,
            out_format=out_format,
        )

        meta_path = out_path.with_suffix(".json")
        metadata = self._build_metadata(
            text=text,
            backend=backend,
            voice=voice,
            profile=profile,
            audio_path=out_path,
            meta_path=meta_path,
            render=result,
        )
        meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return {
            "backend": backend,
            "voice_id": voice,
            "profile": profile,
            "audio_path": str(out_path),
            "meta_path": str(meta_path),
            "sample_rate": result.sample_rate,
            "duration_s": result.duration_s,
            "warnings": result.warnings,
        }

    def _select_piper_model(self) -> Path:
        models = [Path(m["path"]) for m in self.discover_models()]
        if not models:
            models_dir = self.cfg.models_dir
            raise MissingDependencyError(
                f"No Piper models found in {models_dir}. "
                "Add one with 'voxengine models add --path <model.onnx>'."
            )
        if len(models) > 1:
            names = ", ".join(sorted(p.name for p in models))
            raise UserConfigError(
                f"Multiple models found. Specify one with --model. Available: {names}"
            )
        return models[0]

    def _build_metadata(
        self,
        *,
        text: str,
        backend: str,
        voice: Optional[str],
        profile: Optional[str],
        audio_path: Path,
        meta_path: Path,
        render: TTSAudio,
    ) -> Dict[str, Any]:
        return {
            "engine_version": self.cfg.version,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "text": text,
            "backend": backend,
            "voice": voice,
            "profile": profile,
            "audio_path": str(audio_path),
            "meta_path": str(meta_path),
            "duration_s": render.duration_s,
            "sample_rate": render.sample_rate,
            "warnings": render.warnings,
        }


_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """Return a shared engine instance for HTTP + CLI usage."""
    global _engine
    if _engine is None:
        cfg = EngineConfig.load()
        _engine = Engine(cfg=cfg, registry=default_registry)
        log.info("Initialized VoxEngine %s", cfg.version)
    return _engine

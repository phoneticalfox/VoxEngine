import json
from pathlib import Path

from fastapi.testclient import TestClient
import pytest
from typer.testing import CliRunner

from voxengine.api.server import create_app
from voxengine.cli import app
from voxengine.core.engine import Engine, EngineConfig
from voxengine.core.registry import AdapterRegistry
from voxengine.core.errors import UserConfigError
import voxengine.core.engine as engine_mod


def test_doctor_cli_json_output():
    runner = CliRunner()
    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0

    data = json.loads(result.output)
    assert "version" in data
    assert "tts_backends" in data


def test_health_endpoint():
    client = TestClient(create_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_beep_backend_generates_audio_and_metadata(tmp_path: Path):
    cfg = EngineConfig(cache_dir=tmp_path / "cache", models_dir=tmp_path / "models")
    eng = Engine(cfg=cfg, registry=AdapterRegistry.default())

    out_path = tmp_path / "tone.wav"
    result = eng.tts_speak(text="hello", backend="beep", out_path=out_path)

    audio_path = Path(result["audio_path"])
    meta_path = Path(result["meta_path"])

    assert audio_path.exists()
    assert meta_path.exists()

    metadata = json.loads(meta_path.read_text())
    assert metadata["backend"] == "beep"
    assert metadata["audio_path"] == str(audio_path)


def test_invalid_profile_rejected(tmp_path: Path):
    cfg = EngineConfig(cache_dir=tmp_path / "cache", models_dir=tmp_path / "models")
    eng = Engine(cfg=cfg, registry=AdapterRegistry.default())

    with pytest.raises(UserConfigError):
        eng.tts_speak(text="hi", backend="beep", out_path=tmp_path / "bad.wav", profile="invalid")


def test_profile_normalized_and_recorded(tmp_path: Path):
    cfg = EngineConfig(cache_dir=tmp_path / "cache", models_dir=tmp_path / "models")
    eng = Engine(cfg=cfg, registry=AdapterRegistry.default())

    out_path = tmp_path / "clip.wav"
    result = eng.tts_speak(
        text="hi", backend="beep", out_path=out_path, profile="Narration", out_format="wav"
    )

    metadata = json.loads(Path(result["meta_path"]).read_text())
    assert metadata["profile"] == "narration"
    assert result["profile"] == "narration"


def test_out_format_validation(tmp_path: Path):
    cfg = EngineConfig(cache_dir=tmp_path / "cache", models_dir=tmp_path / "models")
    eng = Engine(cfg=cfg, registry=AdapterRegistry.default())

    with pytest.raises(UserConfigError):
        eng.tts_speak(text="hi", backend="beep", out_path=tmp_path / "clip", out_format="mp3")


def _reset_engine(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("VOXENGINE_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("VOXENGINE_MODELS_DIR", str(tmp_path / "models"))
    engine_mod._engine = None


def test_api_speak_rejects_invalid_profile(monkeypatch, tmp_path: Path):
    _reset_engine(monkeypatch, tmp_path)
    client = TestClient(create_app())

    resp = client.post("/v1/tts/speak", json={"text": "hello", "backend": "beep", "profile": "bad"})
    assert resp.status_code == 400
    assert "Invalid profile" in resp.json()["detail"]


def test_api_speak_beep_writes_files(monkeypatch, tmp_path: Path):
    _reset_engine(monkeypatch, tmp_path)
    client = TestClient(create_app())

    resp = client.post("/v1/tts/speak", json={"text": "hi", "backend": "beep", "profile": "dialogue"})
    assert resp.status_code == 200
    data = resp.json()

    audio_path = Path(data["audio_path"])
    meta_path = Path(data["meta_path"])
    assert audio_path.exists()
    assert meta_path.exists()
    assert data["profile"] == "dialogue"
    assert data["download_url"].endswith(audio_path.name)

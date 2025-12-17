import json
from pathlib import Path

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from voxengine.api.server import create_app
from voxengine.cli import app
from voxengine.core.engine import Engine, EngineConfig
from voxengine.core.registry import AdapterRegistry


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

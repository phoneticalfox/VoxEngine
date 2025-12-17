"""VoxEngine CLI."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

import typer
from rich import print

from voxengine.core.engine import Engine, EngineConfig, get_engine
from voxengine.core.logging import configure_logging
from voxengine.api.server import run as serve_app

app = typer.Typer(add_completion=False, help="VoxEngine CLI.")
tts_app = typer.Typer(help="Text-to-speech commands.")
app.add_typer(tts_app, name="tts")


def _engine() -> Engine:
    configure_logging()
    return get_engine()


@app.command()
def serve(host: str = "127.0.0.1", port: int = 7341):
    """Start the FastAPI server."""
    serve_app(host=host, port=port)


@app.command()
def doctor():
    """Print engine health and adapter availability."""
    print(json.dumps(_engine().doctor(), indent=2))


@tts_app.command("speak")
def speak(
    text: str,
    out: Path = typer.Option(Path("out.wav"), "--out", "-o", help="Output WAV path"),
    backend: str = typer.Option("piper", "--backend", help="TTS backend name"),
    model: Optional[Path] = typer.Option(None, "--model", help="Path to Piper .onnx model"),
    voice: Optional[str] = typer.Option(None, "--voice", help="Voice/speaker id for the backend"),
):
    """Synthesize speech to a file via the engine."""
    res = _engine().tts_speak(text=text, out_path=out, backend=backend, model_path=model, voice=voice)
    print(f"[green]Wrote[/green] {res['path']}")


if __name__ == "__main__":
    app()

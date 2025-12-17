"""VoxEngine CLI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Optional

import typer
from rich import print

from voxengine.api.server import run as serve_app
from voxengine.core.engine import Engine, get_engine
from voxengine.core.errors import MissingDependencyError, VoxEngineError
from voxengine.core.logging import configure_logging

app = typer.Typer(add_completion=False, help="VoxEngine CLI.")
tts_app = typer.Typer(help="Text-to-speech commands.")
models_app = typer.Typer(help="Manage voice models.")
backends_app = typer.Typer(help="Inspect available backends.")

app.add_typer(tts_app, name="tts")
app.add_typer(models_app, name="models")
app.add_typer(backends_app, name="backends")


def _engine() -> Engine:
    configure_logging()
    return get_engine()


def _safe_execute(action: Callable[[], None], *, debug: bool) -> None:
    try:
        action()
    except VoxEngineError as exc:
        if debug:
            raise
        print(f"[red]{exc}[/red]")
        raise typer.Exit(code=exc.exit_code)
    except Exception as exc:  # noqa: BLE001
        if debug:
            raise
        print(f"[red]Unexpected error:[/red] {exc}")
        raise typer.Exit(code=1)


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Host to bind the API server."),
    port: int = typer.Option(7341, help="Port to bind the API server."),
    debug: bool = typer.Option(False, "--debug", help="Show tracebacks for troubleshooting."),
):
    """Start the FastAPI server."""

    def _run() -> None:
        serve_app(host=host, port=port)

    _safe_execute(_run, debug=debug)


@app.command()
def doctor(
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
    debug: bool = typer.Option(False, "--debug", help="Show tracebacks for troubleshooting."),
):
    """Print engine health and adapter availability."""

    def _run() -> None:
        data = _engine().doctor()
        if json_output:
            typer.echo(json.dumps(data, indent=2))
            return

        print("[bold cyan]VoxEngine Doctor[/bold cyan]")
        print(f"[cyan]Version:[/cyan] {data['version']}")
        system = data.get("system", {})
        if system:
            print(f"[cyan]Python:[/cyan] {system.get('python', 'unknown')}")
            print(f"[cyan]Platform:[/cyan] {system.get('platform', 'unknown')}")
        print(f"[cyan]Cache dir:[/cyan] {data['cache_dir']}")
        print(f"[cyan]Models dir:[/cyan] {data['models_dir']}")

        print("\n[bold]Discovered models[/bold]")
        if data.get("models"):
            for model in data["models"]:
                print(f" • {model['name']} ({model['path']})")
        else:
            print(" • None found")

        print("\n[bold]TTS backends[/bold]")
        for backend in data.get("tts_backends", []):
            status = (
                "[green]available[/green]"
                if backend.get("available")
                else "[yellow]unavailable[/yellow]"
            )
            notes = backend.get("notes") or ""
            print(f" • {backend.get('name')} — {status}. {notes}")

        if data.get("next_steps"):
            print("\n[bold]Next steps[/bold]")
            for step in data["next_steps"]:
                print(f" • {step}")

    _safe_execute(_run, debug=debug)


@backends_app.command("list")
def list_backends(
    debug: bool = typer.Option(False, "--debug", help="Show tracebacks for troubleshooting."),
):
    """List available runtime backends."""

    def _run() -> None:
        data = _engine().doctor()
        for backend in data.get("tts_backends", []):
            status = "available" if backend.get("available") else "unavailable"
            print(f"{backend.get('name')}: {status}")

    _safe_execute(_run, debug=debug)


@models_app.command("list")
def list_models(
    debug: bool = typer.Option(False, "--debug", help="Show tracebacks for troubleshooting."),
):
    """List discovered voice models."""

    def _run() -> None:
        models = _engine().discover_models()
        if not models:
            print("No models found. Add one with 'voxengine models add --path /path/to/model.onnx'")
            return
        for model in models:
            print(f"{model['name']}: {model['path']}")

    _safe_execute(_run, debug=debug)


@models_app.command("add")
def add_model(
    path: Path = typer.Option(
        ..., "--path", exists=True, readable=True, help="Path to a model file."
    ),
    name: Optional[str] = typer.Option(None, "--name", help="Optional name for the model."),
    debug: bool = typer.Option(False, "--debug", help="Show tracebacks for troubleshooting."),
):
    """Copy a model file into the VoxEngine models directory."""

    def _run() -> None:
        dest = _engine().add_model(path, name=name)
        print(f"[green]Added model:[/green] {dest}")

    _safe_execute(_run, debug=debug)


@tts_app.command("voices")
def list_voices(
    backend: str = typer.Option("piper", "--backend", help="Backend to query for voices."),
    debug: bool = typer.Option(False, "--debug", help="Show tracebacks for troubleshooting."),
):
    """List voices known to a backend (placeholder)."""

    def _run() -> None:
        data = _engine().doctor()
        names = [b.get("name") for b in data.get("tts_backends", [])]
        if backend not in names:
            raise MissingDependencyError(f"Backend '{backend}' is not registered.")
        print(
            "Voice discovery not implemented yet for this backend. "
            "Specify --voice if required by the model."
        )

    _safe_execute(_run, debug=debug)


@tts_app.command("speak")
def speak(
    text: str = typer.Argument(..., help="Text to synthesize."),
    out: Path = typer.Option(Path("out.wav"), "--out", "-o", help="Output audio path."),
    backend: str = typer.Option("piper", "--backend", help="TTS backend name."),
    model: Optional[Path] = typer.Option(None, "--model", help="Path to Piper .onnx model"),
    voice: Optional[str] = typer.Option(None, "--voice", help="Voice/speaker id for the backend"),
    profile: Optional[str] = typer.Option(
        "screenreader",
        "--profile",
        help="Accessibility profile: screenreader, narration, dialogue.",
        case_sensitive=False,
    ),
    out_format: str = typer.Option("wav", "--format", help="Audio format (wav)."),
    debug: bool = typer.Option(False, "--debug", help="Show tracebacks for troubleshooting."),
):
    """Synthesize speech to a file via the engine."""

    def _run() -> None:
        normalized_profile = profile.lower() if profile else None
        normalized_format = out_format.lower()
        res = _engine().tts_speak(
            text=text,
            out_path=out,
            backend=backend,
            model_path=model,
            voice=voice,
            profile=normalized_profile,
            out_format=normalized_format,
        )
        print(f"[green]Wrote audio:[/green] {res['audio_path']}")
        print(f"[green]Wrote metadata:[/green] {res['meta_path']}")
        if res.get("warnings"):
            print("Warnings:")
            for w in res["warnings"]:
                print(f" • {w}")

    _safe_execute(_run, debug=debug)


if __name__ == "__main__":
    app()

# VoxEngine

**VoxEngine** is an **offline-first “studio backend”** for:

- **Script generation + rewrites** (local LLMs)
- **Text-to-speech** with a **cast library** (including short-sample voice cloning where supported)
- **Render queues, caching, and project packaging**
- A small local API that any UI can talk to (**VoxStudio is just one frontend**)

It’s meant to feel less like “a demo” and more like **a dependable creative tool**.

---

## Why VoxEngine exists

Cloud AI is convenient… until it isn’t.

VoxEngine is built around a few stubborn ideas:

- **Your studio should work offline.**
- **Your cast and project assets should be portable.**
- **Models should be swappable.**
- **The UI should never need to understand ML internals.**

---

## Key features

- **Offline-first API** (localhost HTTP; gRPC is possible later)
- **Provider-agnostic adapters**
  - LLM: `llama.cpp`, `ollama` (starter adapters)
  - TTS: `cosyvoice`, `piper` (starter adapters)
- **Cast Library**
  - Voices are project assets with metadata, reference clips, and cached embeddings
- **Two-speed audio workflow**
  - fast preview voice (optional)
  - high-quality render voice (optional)
- **Render queue + job status**
- **Portable project format**
  - a project is a folder you can zip, version, and move

---

## Non-goals

- VoxEngine is **not** a hosted cloud service.
- VoxEngine is **not** a “deepfake vending machine.”
- VoxEngine is **not** a UI framework.

It’s the engine room. Put whatever UI you want on top.

---

## Ethics (practical, minimal, non-vibe-killing)

VoxEngine stores **provenance + consent metadata** alongside voice assets and can require a one-time
local attestation file on first run.

That’s it.

- The tool stays clean and studio-oriented.
- If a user chooses to do something unethical, that responsibility is on them.

See: `voxengine/ethics/`.

---

## Quickstart (dev)

> This repo ships with placeholder adapters and a skeleton API. You’ll wire up real model runners as you go.

### 1) Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install

```bash
pip install -e .
```

### 3) Smoke-test the engine

```bash
voxengine doctor
```

### 4) Run the local server

```bash
voxengine serve
# or: uvicorn voxengine.api.server:app --host 127.0.0.1 --port 7341
```

Open:
- http://127.0.0.1:7341/health
- http://127.0.0.1:7341/doctor

### CLI (universal wrench)

- `voxengine doctor` — print engine metadata and available adapters (use `--json` for machine output)
- `voxengine serve` — start the FastAPI service (defaults: 127.0.0.1:7341)
- `voxengine tts speak "hello" --model /path/voice.onnx` — synthesize to `out.wav`
- `voxengine tts speak "test" --backend beep` — write a built-in validation tone + metadata

### First run expectations

- `voxengine doctor` prints a short summary plus next steps. The built-in `beep` backend should
  always show as available; `piper` will be unavailable until you install its executable and add a
  model.
- `voxengine serve` starts FastAPI. `GET /health` returns `{ "status": "ok" }`.
- `voxengine tts speak "hello" --backend beep` writes two files: `out.wav` and a matching
  `out.json` sidecar containing render metadata.

---

## API surface (high-level)

- `GET  /health`
- `GET  /doctor`
- `GET  /v1/backends`
- `POST /tts/speak`
- `POST /v1/tts/speak`
- (legacy draft endpoints for script/render remain in code for future work)

The contract is intentionally small so you can swap UIs and engines without breaking everything.

---

## Project format (portable)

A project is a directory (example in `examples/example_project/`):

```
MyProject/
  project.json
  cast/
    actor_name/
      consent.json
      reference.wav
      embedding.bin   (optional cache)
  script/
    scenes.json
  renders/
    scene01/
      line_001.wav
```

See: `docs/project_format.md`.

---

## License

Apache-2.0 (see `LICENSE`).

---

## Repository

- Default branch: `main`
- Project files live at the repository root (the former `voxengine/` folder was flattened).
- Open pull requests against `main`; feature branches are preferred for changes.

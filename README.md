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

### 3) Run the local server

```bash
uvicorn voxengine.api.server:app --reload --host 127.0.0.1 --port 7788
```

Open:
- http://127.0.0.1:7788/docs

---

## API surface (high-level)

- `POST /v1/script/generate_scene`
- `POST /v1/script/rewrite_line`
- `POST /v1/cast/register`
- `POST /v1/tts/speak`
- `POST /v1/render/scene`
- `GET  /v1/render/jobs/{job_id}`

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

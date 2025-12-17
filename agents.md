# VoxEngine Task List

Task list and spec outline for implementing the engine (CLI + API + adapters + predictable local behavior).

## Definition of Done (v0.1)
A fresh clone + editable install must provide:

1. `voxengine doctor` returns a **human-friendly** summary (and optional `--json`).
2. `voxengine serve` starts FastAPI with:
   - `GET /health`
   - `GET /doctor`
   - `GET /v1/backends`
3. `voxengine tts speak "hello" --out hello.wav` must:
   - produce audio when a backend is available **or**
   - fail with a **friendly, actionable** message (no stack trace) when missing deps/models.
4. Every synth render writes `*.json` **sidecar metadata** next to the audio output.

---

## Task List for Codex

### 0) Repo hygiene / docs correctness
- [ ] Update `README.md` CLI usage so it matches the actual CLI signature (positional `TEXT` arg vs `--text`).
- [ ] Add a short “first run” section: expected outputs for `doctor`, `serve`, `tts speak`.
- [ ] Eliminate any recurring first-run warnings that confuse users (e.g., Pydantic protected namespace warning): rename fields or configure Pydantic.

### 1) Add/normalize an `AGENTS.md` spec file
- [ ] Create `AGENTS.md` at repo root using the format below (see second half of this doc).
- [ ] Make `AGENTS.md` authoritative for:
  - CLI behavior
  - API contract
  - output conventions
  - adapter requirements

### 2) CLI UX: never stack trace for expected errors
- [ ] In `voxengine/cli.py` (or equivalent), wrap top-level commands so expected operational failures become clean messages:
  - missing binary on PATH
  - missing model file
  - unsupported backend
  - invalid output path
- [ ] Add `--debug` flag to re-enable full tracebacks.
- [ ] Ensure exit codes:
  - `0` success
  - `2` user/config error
  - `3` missing dependency/backend
  - `1` unexpected error

### 3) `doctor` should be helpful by default
- [ ] Change `voxengine doctor` default output to a readable summary.
- [ ] Keep `voxengine doctor --json` for machine parsing.
- [ ] `doctor` should report:
  - VoxEngine version
  - OS + Python version
  - available backends + status
  - default config values in effect
  - models directory and discovered voice models
  - actionable “next steps” when something is missing

### 4) Backend discovery endpoint + CLI command
- [ ] Add `GET /v1/backends` that returns the same core data structure as `doctor --json` but scoped to runtime backends.
- [ ] Add `voxengine backends list` to print backends + availability.

### 5) TTS output contract: audio + metadata sidecar
- [ ] Standardize a single render result object returned by any TTS adapter:
  - `audio_path`
  - `meta_path`
  - `backend`
  - `voice_id` (or voice name)
  - `profile`
  - `warnings` list
- [ ] Ensure `tts speak` always writes a sidecar JSON file:
  - same basename as audio
  - includes text, backend, voice, profile, duration if known, created_at, engine_version

### 6) Add a “smoke test” TTS backend (always available)
Purpose: allow users to verify pipeline + file output offline even with no model.

- [ ] Implement a `NullToneTTS` (or `beep`) backend adapter:
  - generates a short WAV tone (e.g., 440Hz, 0.3–0.7s)
  - ignores text
  - requires no external deps beyond minimal audio writing (stdlib `wave` is fine)
- [ ] Expose as `--backend beep` and include in `doctor`.

### 7) Model management (minimal, local-first)
- [ ] Define a default models directory (e.g., `~/.voxengine/models` or project-local configurable).
- [ ] Add `voxengine models list` to enumerate discovered voice models.
- [ ] Add `voxengine models add --path /path/to/model.onnx` to register/copy/link into models dir.
- [ ] Ensure Piper is the default TTS backend selection.
- [ ] Update Piper adapter to:
  - search default models dir if `--model` not provided
  - if multiple models exist, require explicit selection
  - produce a friendly error with suggestions

### 8) Accessibility profiles (engine-level)
- [ ] Define a `profile` option for TTS:
  - `screenreader`
  - `narration`
  - `dialogue`
- [ ] Even if profiles are initially “no-op,” include them in metadata and plumbing.
- [ ] Add `voxengine tts speak TEXT --profile screenreader`.

### 9) API parity for TTS speak
- [ ] Ensure `/tts/speak` supports:
  - `text`
  - `backend` override
  - `voice`/`voice_id`
  - `profile`
  - `out_format`
- [ ] Ensure `/tts/speak` returns job/result including `audio_path` and `meta_path`.

### 10) Tests (thin but real)
- [ ] Add a minimal test suite that verifies:
  - CLI `doctor` exit code and contains expected keys
  - `serve` health endpoint responds
  - `tts speak --backend beep` generates wav + json

---

# AGENTS.md Layout (Authoritative Spec)

Create `AGENTS.md` at repo root with the following structure.

## 1. Purpose
- VoxEngine is an offline-first local TTS engine via CLI + local API.
- VoxEngine must be usable headlessly for accessibility and automation.

## 2. Supported Surfaces
### CLI
- `voxengine doctor [--json] [--debug]`
- `voxengine serve [--host HOST] [--port PORT] [--debug]`
- `voxengine backends list`
- `voxengine models list`
- `voxengine models add --path PATH [--name NAME]`
- `voxengine tts voices [--backend BACKEND]`
- `voxengine tts speak TEXT [--backend BACKEND] [--voice VOICE] [--profile PROFILE] [--out PATH] [--format wav] [--debug]`

### HTTP API
- `GET /health`
- `GET /doctor` (machine-readable)
- `GET /v1/backends`
- `POST /v1/tts/speak`

## 3. Output Contracts
### Render Output
- Every audio output must have a sidecar JSON file with the same basename.
- Sidecar JSON schema:
  - `engine_version`
  - `created_at`
  - `text`
  - `backend`
  - `voice`
  - `profile`
  - `audio_path`
  - `meta_path`
  - `duration_s` (optional)
  - `warnings` (list)

## 4. Error Policy
- Expected operational failures never print stack traces by default.
- Exit codes:
  - `0` success
  - `2` user/config error
  - `3` missing dependency/backend/model
  - `1` unexpected error
- `--debug` enables tracebacks.

## 5. Backends

### Required
- `piper` backend:
  - ships with VoxEngine as the default TTS backend adapter
  - requires `piper` executable at runtime
  - requires a `.onnx` voice model at runtime
  - searches the default models directory if a model is not explicitly provided
  - if missing, errors must be friendly and actionable (no stack traces by default)

### Built-in
- `beep` backend: always available, generates tone wav for pipeline verification.

### Optional
- other TTS backends can be added as adapters (license-aware where needed)

## 6. Accessibility
- Profiles:
  - `screenreader`, `narration`, `dialogue`
- Profiles must be accepted by CLI/API and recorded in metadata.

## 7. Security / Ethics (Local)
- VoxEngine stores provenance/consent metadata for voice assets when applicable.
- Voice-cloning capable backends must require consent metadata and local attestation gating (later milestone).

## 8. Versioning
- CLI flags and API schemas must be kept backward-compatible within minor versions.

## 9. Roadmap (Non-binding)
- Render queue
- Project/cast format enforcement
- Streaming TTS
- Word/phoneme timestamps
- Optional adapters (voice cloning where license/consent allow)


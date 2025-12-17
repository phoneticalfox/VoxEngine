# VoxEngine Agent Guidance

This file describes how VoxEngine is expected to behave. Follow these rules for any code under this repository.

## 1. Purpose
- VoxEngine is an offline-first local TTS engine exposed via CLI + local API.
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

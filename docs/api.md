# VoxEngine API (MVP)

## GET /health
Simple status check. Returns version + ok flag.

## GET /doctor
Returns engine metadata and adapter availability.

## GET /v1/backends
Returns the runtime backends that the engine knows how to use:

```json
{
  "tts": [
    {
      "name": "beep",
      "available": true,
      "notes": "Built-in tone generator for smoke tests."
    },
    {
      "name": "piper",
      "available": false,
      "notes": "Requires 'piper' on PATH plus an .onnx model file."
    }
  ]
}
```

## POST /tts/speak (alias: /v1/tts/speak)
Request:
```json
{
  "text": "hello world",
  "backend": "piper",
  "model_path": "/path/model.onnx",
  "profile": "screenreader",
  "out_format": "wav"
}
```

Response:
```json
{
  "backend": "piper",
  "audio_path": "/tmp/tts_x.wav",
  "meta_path": "/tmp/tts_x.json",
  "profile": "screenreader",
  "duration_s": null,
  "sample_rate": 22050,
  "warnings": [],
  "download_url": "/tts/file?path=/tmp/tts_x.wav"
}
```

Notes:
- Only `wav` output is supported at this stage.
- `profile` must be one of `screenreader`, `narration`, or `dialogue`.
- A JSON sidecar is always written to `meta_path` containing render metadata.

# VoxEngine API (MVP)

## GET /health
Simple status check. Returns version + ok flag.

## GET /doctor
Returns engine metadata and adapter availability.

## POST /tts/speak
Request:
```json
{ "text": "hello", "backend": "piper", "model_path": "/path/model.onnx" }
```
Response:
```json
{
  "backend": "piper",
  "path": "/tmp/tts_x.wav",
  "sample_rate": 22050,
  "download_url": "/tts/file?path=/tmp/tts_x.wav"
}
```

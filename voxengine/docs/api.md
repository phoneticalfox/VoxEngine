# VoxEngine API (Draft)

The API is intentionally small and stable so UIs can swap in/out.

## Endpoints

- `POST /v1/script/generate_scene`
- `POST /v1/script/rewrite_line`
- `POST /v1/cast/register`
- `POST /v1/tts/speak`
- `POST /v1/render/scene`
- `GET  /v1/render/jobs/{job_id}`

See `voxengine/api/schemas.py` for request/response shapes.

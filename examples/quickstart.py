"""Quickstart example (placeholder).

Start the server:
  uvicorn voxengine.api.server:app --reload --host 127.0.0.1 --port 7788

Then run:
  python examples/quickstart.py
"""

import httpx

BASE = "http://127.0.0.1:7788"

def main():
    with httpx.Client() as c:
        print("health:", c.get(f"{BASE}/health").json())
        print("scene:", c.post(f"{BASE}/v1/script/generate_scene", json={
            "prompt": "A quiet kitchen scene where two friends avoid the thing they're both thinking.",
            "constraints": {"length": "short", "format": "screenplay-ish"}
        }).json())

if __name__ == "__main__":
    main()

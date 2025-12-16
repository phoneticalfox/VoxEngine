"""Ethics policy layer (starter)."""

from pathlib import Path
import json

ATTEST_FILE = "user_attestation.json"

def ensure_attestation(cache_dir: str) -> Path:
    p = Path(cache_dir)
    p.mkdir(parents=True, exist_ok=True)
    f = p / ATTEST_FILE
    if not f.exists():
        f.write_text(json.dumps({
            "attested": False,
            "notes": "Set attested=true after showing user the local-use responsibility notice."
        }, indent=2), encoding="utf-8")
    return f

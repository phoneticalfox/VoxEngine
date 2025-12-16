"""Attestation helpers (placeholder)."""

from pathlib import Path
import json

def set_attested(attestation_path: str | Path, value: bool = True) -> None:
    p = Path(attestation_path)
    doc = json.loads(p.read_text(encoding="utf-8"))
    doc["attested"] = bool(value)
    p.write_text(json.dumps(doc, indent=2), encoding="utf-8")

def is_attested(attestation_path: str | Path) -> bool:
    p = Path(attestation_path)
    doc = json.loads(p.read_text(encoding="utf-8"))
    return bool(doc.get("attested", False))

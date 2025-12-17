"""Pydantic schemas for the HTTP API.

Keep these stable. UIs and other clients will depend on them.
"""

from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class GenerateSceneRequest(BaseModel):
    prompt: str
    constraints: Dict[str, Any] = Field(default_factory=dict)


class GenerateSceneResponse(BaseModel):
    scene_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RewriteLineRequest(BaseModel):
    line: str
    direction: str = Field(description="Creative direction, e.g. 'more tender', 'more tense', etc.")
    num_variants: int = 3


class RewriteLineResponse(BaseModel):
    variants: List[str]


class CastRegisterRequest(BaseModel):
    project_path: str
    actor_name: str
    reference_wav_path: str
    consent: Dict[str, Any] = Field(default_factory=dict)


class CastRegisterResponse(BaseModel):
    voice_id: str


class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1)
    backend: str = "piper"
    model_path: Optional[Path] = None
    voice: Optional[str] = None
    profile: Optional[str] = None
    out_format: str = "wav"


class SpeakResponse(BaseModel):
    backend: str
    audio_path: str
    meta_path: str
    voice_id: Optional[str] = None
    profile: Optional[str] = None
    duration_s: Optional[float] = None
    sample_rate: int
    warnings: List[str] = Field(default_factory=list)
    download_url: Optional[str] = None


class RenderSceneRequest(BaseModel):
    project_path: str
    scene_id: str
    voice_map: Dict[str, str] = Field(default_factory=dict)  # character -> voice_id
    options: Dict[str, Any] = Field(default_factory=dict)


class RenderSceneResponse(BaseModel):
    job_id: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float = 0.0
    detail: Optional[str] = None
    artifacts: Dict[str, Any] = Field(default_factory=dict)
